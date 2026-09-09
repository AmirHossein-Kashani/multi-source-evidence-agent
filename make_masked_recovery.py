"""Build the masked-association recovery task (Phase 14, proposed experiment B2).

Selects well-curated gene-drug pairs, writes copies of the KB tables with those pairs'
rows REMOVED, and emits the matching question list. Running the phase-13 configuration
against the masked tables (env AMG_KB_CLINVAR / AMG_KB_REL, already read by
AMG-with-KG.py) turns "find what is not in the graph" into a controlled task: the
association is real, its literature exists, only the curated row is hidden. Success =
the masked pair resurfaces in the ledger as `uncurated_literature_claim` with a
resolving citation.

This measures ASSOCIATION RECOVERY, not biological novelty.

    python make_masked_recovery.py --pairs SLC28A3:anthracyclines TPMT:mercaptopurine \
        --outdir dataset/ADR_DataSet_masked
Then:
    sbatch --export=ALL,AMG_KB_CLINVAR=dataset/ADR_DataSet_masked/clinicalVariants.tsv,\
AMG_KB_REL=dataset/ADR_DataSet_masked/relationships.tsv,\
ADR_INPUT=dataset/ADR_DataSet_masked/masked_questions.jsonl,ADR_TAG=maskrec \
        run_adr_phase13_alliance.bash
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pgx_kb import DEFAULT_CLINVAR, DEFAULT_REL, _norm

QUESTION = ("Which pharmacogenomic biomarkers predict {drug}-induced adverse reactions, "
            "and how strong is the evidence for each? Note any disagreement between sources.")


def mask_tsv(src, dst, hit):
    kept = removed = 0
    with open(src, newline="", encoding="utf-8") as f, \
         open(dst, "w", newline="", encoding="utf-8") as g:
        rdr = csv.reader(f, delimiter="\t")
        wtr = csv.writer(g, delimiter="\t")
        header = next(rdr)
        wtr.writerow(header)
        for row in rdr:
            if hit(header, row):
                removed += 1
            else:
                kept += 1
                wtr.writerow(row)
    return kept, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", required=True,
                    help="GENE:drug pairs to mask, e.g. SLC28A3:anthracyclines")
    ap.add_argument("--outdir", default=os.path.join(HERE, "dataset", "ADR_DataSet_masked"))
    args = ap.parse_args()

    pairs = []
    for p in args.pairs:
        g, d = p.split(":", 1)
        pairs.append((g.strip().upper(), _norm(d)))
    os.makedirs(args.outdir, exist_ok=True)

    def hit_clinvar(header, row):
        r = dict(zip(header, row))
        g = r.get("gene", "").strip().upper()
        chems = _norm(r.get("chemicals", ""))
        return any(g == pg and pd in chems for pg, pd in pairs)

    def hit_rel(header, row):
        r = dict(zip(header, row))
        chems = {_norm(r.get("Entity1_name", "")), _norm(r.get("Entity2_name", ""))}
        genes = {r.get("Entity1_name", "").strip().upper(),
                 r.get("Entity2_name", "").strip().upper()}
        return any(pg in genes and any(pd in c for c in chems) for pg, pd in pairs)

    k, m = mask_tsv(DEFAULT_CLINVAR, os.path.join(args.outdir, "clinicalVariants.tsv"), hit_clinvar)
    print(f"clinicalVariants: kept {k}, removed {m}")
    k, m = mask_tsv(DEFAULT_REL, os.path.join(args.outdir, "relationships.tsv"), hit_rel)
    print(f"relationships:    kept {k}, removed {m}")

    qpath = os.path.join(args.outdir, "masked_questions.jsonl")
    with open(qpath, "w", encoding="utf-8") as f:
        for i, (g, d) in enumerate(pairs):
            f.write(json.dumps({
                "id": i, "question": QUESTION.format(drug=d), "reference": "",
                "masked_gene": g, "masked_drug": d}) + "\n")
    print(f"questions: {qpath}")
    print("Masked pairs:", ", ".join(f"{g}-{d}" for g, d in pairs))
    print("NOTE: drug-name matching is literal (the audit showed class-level rows like "
          "'Platinum compounds' escape literal matching) — check the removed counts, and "
          "add class names to --pairs when masking a drug that belongs to a curated class.")


if __name__ == "__main__":
    main()
