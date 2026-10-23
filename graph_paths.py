"""Typed short paths over the global ClinPGx graph that propose gene-drug edges the tables
do not hold, each carrying the path that proposed it.

Why typed paths rather than "a path shorter than k exists": the per-question graph is dense
(~30 nodes, ~85 edges) so almost every pair is connected within four hops, and in the global
table hub nodes (cisplatin: 126 curated genes; MAPK8: 74 gene-gene neighbours) connect
anything to anything. Path existence carries no information; each pattern below has a
meaning, a prior, and a hub penalty where it needs one.

  A  gene -assoc- outcome(ADR)                 the drug-outcome link comes from the question
                                               (ClinPGx has no Chemical-Disease rows)
  B  gene' -gene-gene- gene(curated for drug)  Adamic-Adar over the curated neighbours,
                                               divided by the candidate's own degree
  C  gene -curated- drug class                 e.g. "Platinum compounds" rows for cisplatin;
                                               the class comes from MeSH or the static table

Paths use curated rows only; LLM-hypothesised edges never compose into a path (docs/PLAN.md,
section 2). No LLM call here. The proposals are *search hypotheses*: they enter the edge
queue and must find literature support before they count as evidence.
"""
import csv
import math
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set

from pgx_kb import DEFAULT_CLINVAR, DEFAULT_REL, DRUG_CLASS_MEMBERS, PHENO_SYNONYMS, _norm, _split

PRIOR = {"A": 0.50, "B": 0.35, "C": 0.55}
VIA = {"A": "path:A:outcome", "B": "path:B:gene", "C": "path:C:class"}


def _match(term: str, name: str) -> bool:
    """Loose node-name match: equal, or one contains the other when both are real words."""
    return term == name or (len(term) >= 5 and len(name) >= 5 and (term in name or name in term))


class ClinPGxGraph:
    """Adjacency of the two bulk tables: gene-disease, gene-chemical, gene-gene."""

    def __init__(self, rel_path: str = DEFAULT_REL, clinvar_path: str = DEFAULT_CLINVAR):
        self.disease_genes: Dict[str, Dict[str, str]] = defaultdict(dict)   # disease -> {GENE: assoc}
        self.chem_genes: Dict[str, Dict[str, str]] = defaultdict(dict)      # chem -> {GENE: assoc}
        self.gg: Dict[str, Set[str]] = defaultdict(set)                     # GENE -> {GENE}
        # Evidence volume behind a row (number of PMIDs it cites): the ranking signal inside
        # a pattern, so candidates of equal prior are not listed alphabetically.
        self.n_pmids: Dict[tuple, int] = defaultdict(int)                  # (node, GENE) -> n
        self._load_rel(rel_path)
        self._load_clinvar(clinvar_path)

    def _load_rel(self, path: str) -> None:
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                t1, t2 = r.get("Entity1_type", ""), r.get("Entity2_type", "")
                n1, n2 = r.get("Entity1_name", "").strip(), r.get("Entity2_name", "").strip()
                assoc = _norm(r.get("Association", "")) or "associated"
                if not n1 or not n2:
                    continue
                pair = {t1: n1, t2: n2}
                n_pm = len([p for p in (r.get("PMIDs") or "").replace(";", ",").split(",") if p.strip()])
                if {t1, t2} == {"Gene", "Disease"}:
                    key, gene = _norm(pair["Disease"]), pair["Gene"].upper()
                    self._put(self.disease_genes, key, gene, assoc)
                    self.n_pmids[(key, gene)] = max(self.n_pmids[(key, gene)], n_pm)
                elif {t1, t2} == {"Gene", "Chemical"}:
                    key, gene = _norm(pair["Chemical"]), pair["Gene"].upper()
                    self._put(self.chem_genes, key, gene, assoc)
                    self.n_pmids[(key, gene)] = max(self.n_pmids[(key, gene)], n_pm)
                elif t1 == t2 == "Gene":
                    self.gg[n1.upper()].add(n2.upper())
                    self.gg[n2.upper()].add(n1.upper())

    def _load_clinvar(self, path: str) -> None:
        """clinicalVariants rows are curated associations too (they carry the evidence level)."""
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                gene = r.get("gene", "").strip().upper()
                if not gene:
                    continue
                # a clinical annotation at level 1-2 is worth more than a single citation
                worth = 5 if _norm(r.get("level of evidence", "")) in ("1a", "1b", "2a", "2b") else 2
                for c in _split(r.get("chemicals", "")):
                    self.chem_genes[_norm(c)].setdefault(gene, "associated")
                    self.n_pmids[(_norm(c), gene)] = max(self.n_pmids[(_norm(c), gene)], worth)
                for p in _split(r.get("phenotypes", "")):
                    self.disease_genes[_norm(p)].setdefault(gene, "associated")
                    self.n_pmids[(_norm(p), gene)] = max(self.n_pmids[(_norm(p), gene)], worth)

    def _volume(self, node: str, gene: str) -> float:
        """0.7 .. 1.0 multiplier from the row's evidence volume (saturates at 5 citations)."""
        return 0.7 + 0.3 * min(1.0, self.n_pmids.get((node, gene), 1) / 5.0)

    @staticmethod
    def _put(index, key, gene, assoc):
        prev = index[key].get(gene)
        if prev is None or (prev == "ambiguous" and assoc != "ambiguous"):   # definite call wins
            index[key][gene] = assoc

    # ---- queries ---------------------------------------------------------------
    def curated_genes(self, drug: str) -> Dict[str, str]:
        """GENE -> association for the drug's own node (exact name only)."""
        return dict(self.chem_genes.get(_norm(drug), {}))

    def class_nodes(self, class_terms: Iterable[str]) -> List[str]:
        """Chemical nodes in the table that name one of the classes (e.g. 'platinum compounds')."""
        out = []
        for cls in {_norm(c) for c in class_terms if c}:
            out += [chem for chem in self.chem_genes if _match(cls, chem)]
        return sorted(set(out))

    def own_nodes(self, drug_names: Iterable[str]) -> List[str]:
        """Chemical nodes that ARE the drug: its name, brand synonyms, and -- when the
        question names a class ('anthracycline') -- the class node itself."""
        out = set()
        for d in {_norm(x) for x in drug_names if x}:
            out |= {chem for chem in self.chem_genes if chem == d or (len(d) >= 5 and d in chem)}
        return sorted(out)

    def propose(self, drug: str, outcome_terms: Iterable[str], class_terms: Iterable[str],
                k: int = 10, exclude: Iterable[str] = (),
                drug_names: Optional[Iterable[str]] = None) -> List[dict]:
        """Candidate genes for `drug`, strongest first, each with via/paths/prior.

        Genes already curated for the drug's own node(s) are never proposed (they are in the
        ledger already, including the 'not associated' ones, which are curated negatives).
        `drug_names` lists every name that counts as the drug itself (brand synonyms, or the
        class node when the question asks about a class)."""
        drug_n = _norm(drug)
        own = self.own_nodes(list(drug_names or []) + [drug_n]) or [drug_n]
        curated_own: Dict[str, str] = {}
        for chem in own:
            for g, a in self.chem_genes.get(chem, {}).items():
                if g not in curated_own or (curated_own[g] == "ambiguous" and a != "ambiguous"):
                    curated_own[g] = a
        known = set(curated_own) | {g.upper() for g in exclude}
        cands: Dict[str, dict] = {}

        def add(gene: str, pattern: str, score: float, path: str) -> None:
            if gene in known:
                return
            c = cands.setdefault(gene, {"gene": gene, "drug": drug_n, "scores": {},
                                        "via": set(), "paths": []})
            # best score per pattern: several synonym nodes of one outcome are one reason
            if score > c["scores"].get(pattern, 0.0):
                c["scores"][pattern] = score
                c["paths"].insert(0, path)
            else:
                c["paths"].append(path)
            c["via"].add(VIA[pattern])

        # A: gene -assoc- outcome; the drug-outcome link is the question itself
        outs = {_norm(o) for o in outcome_terms if o}
        for dis, genes in self.disease_genes.items():
            if any(_match(o, dis) for o in outs):
                for g, assoc in genes.items():
                    if assoc == "not associated":
                        continue
                    add(g, "A", PRIOR["A"] * (1.0 if assoc == "associated" else 0.8) * self._volume(dis, g),
                        f"{g} -[{assoc}, {self.n_pmids.get((dis, g), 1)} ref(s)]- {dis} "
                        f"<- question links {drug_n} to {dis}")

        # C: gene -curated- drug class (never the drug's own nodes)
        for chem in self.class_nodes(class_terms):
            if chem in own:
                continue
            for g, assoc in self.chem_genes[chem].items():
                if assoc == "not associated":
                    continue
                add(g, "C", PRIOR["C"] * (1.0 if assoc == "associated" else 0.8) * self._volume(chem, g),
                    f"{g} -[{assoc}, {self.n_pmids.get((chem, g), 1)} ref(s)]- {chem} "
                    f"(class containing {drug_n})")

        # B: gene' -gene-gene- curated gene, Adamic-Adar, hub-penalised
        curated_pos = [g for g, a in curated_own.items() if a != "not associated"]
        aa: Dict[str, float] = defaultdict(float)
        via_genes: Dict[str, List[str]] = defaultdict(list)
        for g in curated_pos:
            deg = len(self.gg.get(g, ()))
            if not deg:
                continue
            w = 1.0 / math.log(1 + deg)               # a promiscuous curated gene says little
            for g2 in self.gg[g]:
                aa[g2] += w
                via_genes[g2].append(g)
        for g2, s in aa.items():
            if g2 in known:
                continue
            s_norm = s / math.log(2 + len(self.gg.get(g2, ())))   # ...and so does a hub candidate
            score = PRIOR["B"] * (1 - math.exp(-s_norm))
            if score < 0.05:
                continue
            nb = sorted(via_genes[g2], key=lambda g: len(self.gg.get(g, ())))[:3]
            add(g2, "B", score,
                f"{g2} -[gene-gene]- {', '.join(nb)}{'...' if len(via_genes[g2]) > 3 else ''} "
                f"-[curated]- {drug_n}  (AA={s:.2f}, deg={len(self.gg.get(g2, ()))})")

        out = []
        for c in cands.values():
            # several patterns proposing the same gene: noisy-or of their best scores
            p = 1.0
            for s in c["scores"].values():
                p *= (1 - s)
            out.append({"gene": c["gene"], "drug": c["drug"], "prior": round(1 - p, 3),
                        "via": sorted(c["via"]), "paths": c["paths"][:3]})
        out.sort(key=lambda c: (-c["prior"], c["gene"]))
        return out[:k]


def propose_for_question(graph: ClinPGxGraph, pgx, question: str, vocab=None, k: int = 10,
                         exclude: Iterable[str] = ()) -> List[dict]:
    """Drug and outcome from the question (via the KB's entity matcher), synonyms and class
    from MeSH when available, static tables otherwise."""
    ents = pgx.extract_entities(question)
    if not ents.get("drugs"):
        return []
    drug = ents["drugs"][0]
    pheno = ents["phenotypes"][0] if ents.get("phenotypes") else ""
    outcomes: Set[str] = {pheno} if pheno else set()
    for k_, v in PHENO_SYNONYMS.items():          # the static family of the question outcome
        if pheno and (v == pheno or k_ == pheno):
            outcomes |= {k_, v}
    classes: Set[str] = {cls for cls, members in DRUG_CLASS_MEMBERS.items() if drug in members}
    if vocab is not None:
        if pheno:
            outcomes |= vocab.synonyms(pheno)
        classes |= set(vocab.parents(drug))
    # names that count as the drug itself (brand synonyms; class members when a class is asked)
    drug_names = pgx.expand_drug_detailed(drug)["exact"] if hasattr(pgx, "expand_drug_detailed") else [drug]
    out = graph.propose(drug, outcomes, classes, k=k, exclude=exclude, drug_names=drug_names)
    for c in out:
        c["outcome"] = pheno
    return out
