"""Local ClinPGx / PharmGKB knowledge-base lookup for AMG-RAG.

Indexes two curated bulk-download tables once and exposes a retrieval interface that mirrors
`PubMedSearcher.search(query, max_results) -> List[str]`, so it drops into the existing
external-evidence seams of AMG-with-KG.py. Unlike live PubMed, it returns the *validated*
pharmacogenomic biomarkers (gene/variant + PharmGKB evidence level) for a drug/phenotype, and
supports a set-membership check for false-premise gating.

Tables (from clinpgx.org/downloads, shipped in ADR_DataSet.zip):
  clinicalVariants.tsv : variant, gene, type, level of evidence, chemicals, phenotypes
  relationships.tsv    : Entity1/2 name+type, Association (associated/not associated/ambiguous), PMIDs

No network, no rate limit, stable schema. Load only when AMG_KB_SOURCE=pharmgkb.
"""
import csv
import os
import re
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
_ADR = os.path.join(HERE, "dataset", "ADR_DataSet")
DEFAULT_CLINVAR = os.path.join(_ADR, "ADR_DataSet", "clinicalVariants", "clinicalVariants.tsv")
DEFAULT_REL = os.path.join(_ADR, "ADR_DataSet", "relationships", "relationships.tsv")

# PharmGKB evidence levels: 1A strongest .. 4 weakest. Lower rank sorts first.
LEVEL_RANK = {"1a": 0, "1b": 1, "2a": 2, "2b": 3, "3": 4, "4": 5}
# Evidence level -> KG edge confidence (kept >=0.4 so level-3/4 clear the 0.3 path threshold).
LEVEL_CONF = {"1a": 0.98, "1b": 0.9, "2a": 0.8, "2b": 0.7, "3": 0.55, "4": 0.4}

# Query phenotype synonyms -> a token that appears in the table's phenotype column.
PHENO_SYNONYMS = {
    "hearing loss": "ototoxicity", "deafness": "ototoxicity", "hearing impairment": "ototoxicity",
    "tinnitus": "ototoxicity", "ototoxic": "ototoxicity",
    "cardiomyopathy": "cardiotoxicity", "cardiomyopathies": "cardiotoxicity",
    "heart failure": "cardiotoxicity", "congestive heart failure": "cardiotoxicity",
    "cardiac toxicity": "cardiotoxicity", "heart muscle damage": "cardiotoxicity",
    "peripheral neuropathy": "neuropathy", "neurotoxicity": "neuropathy",
    "hepatic toxicity": "hepatotoxicity", "liver toxicity": "hepatotoxicity",
    "liver injury": "hepatotoxicity",
}
# Drug brand / class -> table tokens to also try.
DRUG_SYNONYMS = {"platinol": "cisplatin", "adriamycin": "doxorubicin", "oncovin": "vincristine",
                 "taxol": "paclitaxel"}
DRUG_CLASS_MEMBERS = {
    "anthracycline": ["doxorubicin", "daunorubicin", "epirubicin", "idarubicin",
                      "anthracyclines and related substances"],
    "anthracyclines": ["doxorubicin", "daunorubicin", "epirubicin", "idarubicin",
                       "anthracyclines and related substances"],
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _split(field: str) -> List[str]:
    return [t.strip() for t in (field or "").split(",") if t.strip()]


class PharmGKBSearcher:
    """Drop-in evidence retriever backed by local ClinPGx tables."""

    def __init__(self, clinvar_path: str = DEFAULT_CLINVAR, rel_path: str = DEFAULT_REL):
        self.clinvar_rows: List[dict] = []
        self.by_drug_pheno: Dict[Tuple[str, str], List[dict]] = {}
        self.by_drug: Dict[str, List[dict]] = {}
        self.by_pheno: Dict[str, List[dict]] = {}
        self.by_gene: Dict[str, List[dict]] = {}
        self.pair_assoc: Dict[Tuple[str, str], dict] = {}
        self.drug_vocab: set = set()
        self.pheno_vocab: set = set()
        self.gene_vocab: set = set()
        self._load_clinvar(clinvar_path)
        self._load_relationships(rel_path)

    # ---- loading -----------------------------------------------------------
    def _load_clinvar(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                gene = _norm(r.get("gene", ""))
                variants = _split(r.get("variant", ""))
                chems = _split(r.get("chemicals", ""))
                phenos = _split(r.get("phenotypes", ""))
                level = _norm(r.get("level of evidence", ""))
                row = {"gene": gene, "gene_disp": r.get("gene", "").strip(),
                       "variants": variants, "level": level,
                       "type": r.get("type", "").strip(),
                       "chemicals": chems, "phenotypes": phenos}
                self.clinvar_rows.append(row)
                if gene:
                    self.gene_vocab.add(gene)
                    self.by_gene.setdefault(gene, []).append(row)
                for c in chems:
                    cl = _norm(c)
                    self.drug_vocab.add(cl)
                    self.by_drug.setdefault(cl, []).append(row)
                    for p in phenos:
                        pl = _norm(p)
                        self.pheno_vocab.add(pl)
                        self.by_pheno.setdefault(pl, []).append(row)
                        self.by_drug_pheno.setdefault((cl, pl), []).append(row)

    def _load_relationships(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                a, b = _norm(r.get("Entity1_name", "")), _norm(r.get("Entity2_name", ""))
                if not a or not b:
                    continue
                assoc = _norm(r.get("Association", ""))
                rec = {"assoc": assoc, "pmids": r.get("PMIDs", "").strip(),
                       "t1": r.get("Entity1_type", ""), "t2": r.get("Entity2_type", "")}
                for key in ((a, b), (b, a)):
                    prev = self.pair_assoc.get(key)
                    # prefer a definite call over 'ambiguous'
                    if prev is None or (prev["assoc"] == "ambiguous" and assoc != "ambiguous"):
                        self.pair_assoc[key] = rec

    # ---- normalization / extraction ---------------------------------------
    @staticmethod
    def gene_of_allele(token: str) -> str:
        """CYP2D6*4 -> cyp2d6 ; leaves rsIDs / plain genes unchanged."""
        return _norm(re.sub(r"\*.*$", "", token))

    def _expand_drug(self, drug: str) -> List[str]:
        d = _norm(drug)
        out = {d}
        if d in DRUG_SYNONYMS:
            out.add(DRUG_SYNONYMS[d])
        for cls, members in DRUG_CLASS_MEMBERS.items():
            if cls in d:
                out.update(members)
        return list(out)

    def _expand_pheno(self, pheno: str) -> List[str]:
        p = _norm(pheno)
        out = {p}
        for k, v in PHENO_SYNONYMS.items():
            if k in p:
                out.add(v)
        return list(out)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Find drug / phenotype / gene mentions in free text by matching table vocab."""
        t = " " + _norm(text) + " "
        found = {"drugs": [], "phenotypes": [], "genes": []}

        def hit(term):
            return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", t) is not None

        for term in self.drug_vocab:
            if len(term) >= 4 and hit(term):
                found["drugs"].append(term)
        # brand names / class words that may not be table tokens
        for brand, canon in {**DRUG_SYNONYMS}.items():
            if hit(brand):
                found["drugs"].append(canon)
        for cls in DRUG_CLASS_MEMBERS:
            if hit(cls):
                found["drugs"].append(cls)
        for term in self.pheno_vocab:
            if len(term) >= 4 and hit(term):
                found["phenotypes"].append(term)
        for syn in PHENO_SYNONYMS:
            if hit(syn):
                found["phenotypes"].append(PHENO_SYNONYMS[syn])
        for term in self.gene_vocab:
            if len(term) >= 3 and hit(term):
                found["genes"].append(term)
        # star-allele genes (CYP2D6*4) that word-boundary missed
        for m in re.findall(r"([a-z0-9]+)\*[0-9a-z]+", t):
            if m in self.gene_vocab:
                found["genes"].append(m)
        for k in found:
            found[k] = sorted(set(found[k]))
        return found

    # ---- ranking / formatting ---------------------------------------------
    @staticmethod
    def _rank(row: dict) -> int:
        return LEVEL_RANK.get(row.get("level", ""), 9)

    def _format(self, row: dict, drug: Optional[str] = None) -> str:
        var = row["variants"][0] if row["variants"] else ""
        gene = row["gene_disp"] or row["gene"].upper()
        drug_txt = drug or (row["chemicals"][0] if row["chemicals"] else "the drug")
        phen = ", ".join(row["phenotypes"][:2]) if row["phenotypes"] else row.get("type", "")
        lvl = row["level"].upper() if row["level"] else "n/a"
        assoc = self.is_associated(row["gene"], drug_txt)
        assoc_txt = f" ClinPGx relationship: {assoc}." if assoc else ""
        var_txt = f" ({var})" if var else ""
        return (f"{gene}{var_txt}: PharmGKB evidence level {lvl} linking it to "
                f"{drug_txt}-related {phen or 'pharmacogenomic effect'}.{assoc_txt}")

    # ---- public API --------------------------------------------------------
    def lookup_for_pair(self, drug: str, phenotype: str = "") -> List[dict]:
        """Ranked clinicalVariants rows for a (drug[, phenotype]) pair; drug-only if no pheno."""
        drugs, phenos = self._expand_drug(drug), self._expand_pheno(phenotype)
        rows, seen = [], set()
        keyset = ([(d, p) for d in drugs for p in phenos] if phenotype else [])
        for k in keyset:
            for row in self.by_drug_pheno.get(k, []):
                rid = id(row)
                if rid not in seen:
                    seen.add(rid); rows.append(row)
        if not rows:  # fall back to drug-only
            for d in drugs:
                for row in self.by_drug.get(d, []):
                    rid = id(row)
                    if rid not in seen:
                        seen.add(rid); rows.append(row)
        return sorted(rows, key=self._rank)

    def search(self, query: str, max_results: int = 3) -> List[str]:
        """Drop-in for PubMedSearcher.search: evidence strings for the query, or []."""
        return [d["text"] for d in self.search_detailed(query, max_results=max_results)]

    def is_associated(self, gene: str, drug: str) -> Optional[str]:
        """'associated' | 'not associated' | 'ambiguous', or None if the pair is absent."""
        g = self.gene_of_allele(gene)
        for d in self._expand_drug(drug):
            rec = self.pair_assoc.get((g, _norm(d)))
            if rec:
                return rec["assoc"]
        return None

    def pmids_for_pair(self, gene: str, drug: str) -> List[str]:
        """PMIDs backing the gene-drug association in relationships.tsv ([] if none)."""
        g = self.gene_of_allele(gene)
        for d in self._expand_drug(drug):
            rec = self.pair_assoc.get((g, _norm(d)))
            if rec and rec.get("pmids"):
                return [p.strip() for p in re.split(r"[,;]", rec["pmids"]) if p.strip().isdigit()]
        return []

    def search_detailed(self, query: str, max_results: int = 3) -> List[dict]:
        """Like search(), but returns provenance-rich records instead of bare strings.

        Each record: {source, ref, text, gene, variant, level, drug, phenotypes, pmids}
        where `pmids` are the literature PMIDs relationships.tsv cites for the gene-drug
        pair (the seed for the phase-4 PubMed verification step)."""
        ents = self.extract_entities(query)
        rows: List[dict] = []
        drug_label = None
        if ents["drugs"]:
            drug_label = ents["drugs"][0]
            pheno = ents["phenotypes"][0] if ents["phenotypes"] else ""
            rows = self.lookup_for_pair(drug_label, pheno)
        elif ents["phenotypes"]:
            for p in ents["phenotypes"]:
                rows += self.by_pheno.get(p, [])
            rows = sorted(rows, key=self._rank)
        elif ents["genes"]:
            for g in ents["genes"]:
                rows += self.by_gene.get(g, [])
            rows = sorted(rows, key=self._rank)
        else:
            return []
        out, seen = [], set()
        for row in rows:
            text = self._format(row, drug_label)
            if text in seen:
                continue
            seen.add(text)
            gene = row["gene_disp"] or row["gene"].upper()
            variant = row["variants"][0] if row["variants"] else ""
            level = (row["level"] or "").upper()
            drug = drug_label or (row["chemicals"][0] if row["chemicals"] else "")
            pmids = self.pmids_for_pair(row["gene"], drug) if drug else []
            out.append({
                "source": "ClinPGx",
                "ref": f"ClinPGx:{gene}{'/' + variant if variant else ''}:L{level or 'NA'}",
                "text": text,
                "gene": gene,
                "variant": variant,
                "level": level,
                "drug": drug,
                "phenotypes": row["phenotypes"][:3],
                "pmids": pmids,
            })
            if len(out) >= max_results:
                break
        return out
