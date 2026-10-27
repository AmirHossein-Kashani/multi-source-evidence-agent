"""ClinPGx tables as documents for the literature-only baselines (PaperQA2).

The external systems of section 4 (results/benchmarks.md) read the PubMed abstracts only,
while phase 15 also reads the ClinPGx tables, so that comparison confounds the curated tables
with the method. This script renders the same two tables as plain-text documents and places
them in the shared corpus directory, so PaperQA2 can be run with the same inputs:

  - one document per gene-drug pair of clinicalVariants.tsv: its variants, level of
    evidence, annotation type and phenotypes, plus the pair's line from relationships.tsv
    (association call, PK/PD, PMIDs);
  - one document per gene for the relationships.tsv gene-drug pairs that have no clinical
    annotation (association call and PMIDs per drug).

    python extbase/build_clinpgx_docs.py --set full   --corpus <dir> --manifest <csv>   # PGxQA
    python extbase/build_clinpgx_docs.py --set masked --corpus <dir> --manifest <csv>   # masked recovery
    python extbase/build_clinpgx_docs.py --set none   --corpus <dir>                    # abstracts only again

The document file names carry a hash of their content: paper-qa's directory sync skips a
file name it has indexed before without looking at the content, so a document that changed
between the full and the masked tables must arrive under a new name (the old name vanishes
and the sync removes it). The manifest written for the chosen set holds the abstract rows of
the existing manifest plus one row per document (title/journal, no year), so indexing needs
no LLM call for them.
"""
import argparse
import csv
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pgx_kb import DEFAULT_CLINVAR, DEFAULT_REL, _split  # noqa: E402

MASKED_DIR = os.path.join(os.path.dirname(HERE), "dataset", "ADR_DataSet_masked")
JOURNAL = "ClinPGx (PharmGKB) curated tables"
LEVELS = ("Level of evidence: 1A = variant-drug combination in a clinical practice guideline or "
          "implemented in a major health system; 1B = replicated evidence without a guideline; "
          "2A/2B = moderate evidence; 3 = low (single or unreplicated study); "
          "4 = preliminary (case report, non-significant study or in vitro only).")
MAX_PMIDS = 6


def slug(s: str, n: int = 40) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:n] or "x"


def tables(which: str):
    if which == "full":
        return DEFAULT_CLINVAR, DEFAULT_REL
    return os.path.join(MASKED_DIR, "clinicalVariants.tsv"), os.path.join(MASKED_DIR, "relationships.tsv")


def read_tables(clinvar_path: str, rel_path: str):
    """{(gene, drug): [clinvar rows]}, {(gene, drug): relationship rec} (names as written)."""
    pairs = {}
    with open(clinvar_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            gene = r.get("gene", "").strip()
            if not gene:
                continue
            for drug in _split(r.get("chemicals", "")):
                pairs.setdefault((gene, drug), []).append(r)
    rels = {}
    with open(rel_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t1, t2 = r.get("Entity1_type", ""), r.get("Entity2_type", "")
            if {t1, t2} != {"Gene", "Chemical"}:
                continue
            gene, drug = (r["Entity1_name"], r["Entity2_name"]) if t1 == "Gene" else (r["Entity2_name"], r["Entity1_name"])
            key = (gene.strip(), drug.strip())
            prev = rels.get(key)
            if prev is None or (prev["Association"] == "ambiguous" and r["Association"] != "ambiguous"):
                rels[key] = r
    return pairs, rels


def pmid_text(field: str) -> str:
    ids = [p.strip() for p in (field or "").replace(";", ",").split(",") if p.strip()]
    if not ids:
        return "none listed"
    shown = ", ".join(ids[:MAX_PMIDS])
    return shown + (f" (and {len(ids) - MAX_PMIDS} more)" if len(ids) > MAX_PMIDS else "")


def rel_line(gene: str, drug: str, rec: dict) -> str:
    kind = ", ".join(k for k in ("PK", "PD") if (rec.get(k) or "").strip())
    assoc = rec.get("Association", "").strip() or "unspecified"
    return (f"{gene} is {assoc} with {drug}" + (f" ({kind})" if kind else "")
            + f"; evidence types: {rec.get('Evidence', '').strip() or 'n/a'}; PMIDs: {pmid_text(rec.get('PMIDs', ''))}.")


def pair_doc(gene: str, drug: str, rows: list, rel: dict | None) -> str:
    lines = [f"ClinPGx clinical annotations: {gene} and {drug}", "",
             f"Source: ClinPGx (PharmGKB) clinicalVariants table. Gene: {gene}. Drug: {drug}.", LEVELS, "",
             "Annotations:"]
    for r in rows:
        ph = ", ".join(_split(r.get("phenotypes", "")))
        lines.append(f"- {r.get('variant', '').strip() or 'variant not stated'}: level {r.get('level of evidence', '').strip() or '?'}"
                     f", {r.get('type', '').strip() or 'unspecified'}" + (f"; phenotypes: {ph}" if ph else ""))
    if rel is not None:
        lines += ["", "Relationship (relationships table): " + rel_line(gene, drug, rel)]
    return "\n".join(lines) + "\n"


def gene_doc(gene: str, recs: list) -> str:
    lines = [f"ClinPGx gene-drug relationships: {gene}", "",
             f"Source: ClinPGx (PharmGKB) relationships table (variant and summary annotations). Gene: {gene}. "
             f"Pairs that also have a clinical annotation are in the separate 'ClinPGx clinical annotations: "
             f"{gene} and <drug>' documents.", ""]
    for assoc in ("associated", "not associated", "ambiguous"):
        group = [(d, r) for d, r in recs if r.get("Association", "").strip() == assoc]
        if group:
            lines.append(f"{assoc.capitalize()} ({len(group)} drugs):")
            lines += [f"- {rel_line(gene, d, r)}" for d, r in sorted(group)]
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_docs(which: str) -> dict:
    """{file name: content} for the chosen table set."""
    pairs, rels = read_tables(*tables(which))
    docs = {}
    for (gene, drug), rows in pairs.items():
        text = pair_doc(gene, drug, rows, rels.get((gene, drug)))
        h = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
        docs[f"CLINPGX_{slug(gene)}_{slug(drug)}_{h}.txt"] = text
    by_gene = {}
    for (gene, drug), rec in rels.items():
        if (gene, drug) not in pairs:
            by_gene.setdefault(gene, []).append((drug, rec))
    for gene, recs in by_gene.items():
        text = gene_doc(gene, recs)
        h = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
        docs[f"CLINPGX_{slug(gene)}_relationships_{h}.txt"] = text
    return docs


def install(docs: dict, corpus: str):
    """Make the corpus directory hold exactly these ClinPGx documents (abstracts untouched)."""
    present = {n for n in os.listdir(corpus) if n.startswith("CLINPGX_") and n.endswith(".txt")}
    removed = present - set(docs)
    for n in removed:
        os.remove(os.path.join(corpus, n))
    added = set(docs) - present
    for n in added:
        with open(os.path.join(corpus, n), "w", encoding="utf-8") as f:
            f.write(docs[n])
    return len(added), len(removed), len(present & set(docs))


def write_manifest(docs: dict, corpus: str, base_manifest: str, out: str):
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file_location", "title", "journal", "year", "doi"])
        n_base = 0
        if base_manifest and os.path.exists(base_manifest):
            with open(base_manifest, newline="", encoding="utf-8") as b:
                rd = csv.reader(b)
                next(rd, None)
                for row in rd:
                    w.writerow(row); n_base += 1
        for n in sorted(docs):
            w.writerow([os.path.join(corpus, n), docs[n].split("\n", 1)[0], JOURNAL, "", ""])
    return n_base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=["full", "masked", "none"])
    ap.add_argument("--corpus", required=True, help="PaperQA2 paper directory (the PubMed abstract corpus)")
    ap.add_argument("--manifest", help="manifest to write for this set (abstract rows + document rows)")
    ap.add_argument("--base-manifest", help="default: <corpus parent>/paperqa_manifest.csv")
    ap.add_argument("--dry-run", action="store_true", help="count the documents and print one of each kind")
    args = ap.parse_args()
    corpus = os.path.abspath(args.corpus)
    docs = build_docs(args.set) if args.set != "none" else {}
    n_pair = sum(1 for n in docs if "_relationships_" not in n)
    print(f"[clinpgx-docs] set={args.set}: {len(docs)} documents ({n_pair} gene-drug pairs, {len(docs) - n_pair} per-gene relationship lists)")
    if args.dry_run:
        for want_gene_list in (False, True):
            name = next((n for n in sorted(docs) if ("_relationships_" in n) == want_gene_list), None)
            if name:
                print(f"--- {name}\n{docs[name]}")
        return
    added, removed, kept = install(docs, corpus)
    print(f"[clinpgx-docs] corpus {corpus}: {added} added, {removed} removed, {kept} unchanged")
    if args.manifest:
        base = args.base_manifest or os.path.join(os.path.dirname(corpus), "paperqa_manifest.csv")
        n_base = write_manifest(docs, corpus, base, args.manifest)
        print(f"[clinpgx-docs] wrote {args.manifest}: {n_base} abstract rows + {len(docs)} document rows")


if __name__ == "__main__":
    main()
