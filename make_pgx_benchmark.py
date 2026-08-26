"""Build a LABELLED gene-drug benchmark from the ClinPGx bulk download.

The ADR question set has no gold answers, so confidence can only be inspected, not measured.
`relationships.tsv` however carries 127,988 curated gene x chemical rows with an explicit
Association column, which gives three usable labels:

    positive  Association=associated      (optionally restricted to clinicalVariants level 1A/1B)
    negative  Association=not associated
    disputed  Association=ambiguous       (the curators themselves found conflicting evidence)

Each sampled pair becomes one question in the same schema the runner already consumes
({id, question, reference, ...}), plus the label fields the evaluator needs.

    python make_pgx_benchmark.py --per-class 50 --seed 7

IMPORTANT: the sampled pair's label must never leak into the question text -- the question
names the gene and the drug and asks about the relationship; whether one exists is the answer.
"""
import argparse
import csv
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pgx_kb import DEFAULT_CLINVAR, DEFAULT_REL, _norm

TEMPLATE = ("From a pharmacogenomic and drug-safety perspective, what is the relationship "
            "between the gene {gene} and {drug}? Assess the strength of the evidence and note "
            "any disagreement between sources.")


def load_levels(path):
    """gene -> strongest clinicalVariants evidence level, used to pick confident positives."""
    rank = {"1a": 0, "1b": 1, "2a": 2, "2b": 3, "3": 4, "4": 5}
    best = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            g, lv = _norm(r.get("gene", "")), _norm(r.get("level of evidence", ""))
            if not g or lv not in rank:
                continue
            if g not in best or rank[lv] < rank[best[g]]:
                best[g] = lv
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rel", default=DEFAULT_REL)
    ap.add_argument("--clinvar", default=DEFAULT_CLINVAR)
    ap.add_argument("--per-class", type=int, default=50)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(HERE, "dataset", "PharmGKB",
                                                  "pgx_confidence_bench.jsonl"))
    args = ap.parse_args()

    levels = load_levels(args.clinvar)
    buckets = {"positive": [], "negative": [], "disputed": []}
    label_of = {"associated": "positive", "not associated": "negative", "ambiguous": "disputed"}
    seen = set()

    with open(args.rel, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("Entity1_type") != "Gene" or r.get("Entity2_type") != "Chemical":
                continue
            gene, drug = r.get("Entity1_name", "").strip(), r.get("Entity2_name", "").strip()
            lab = label_of.get(_norm(r.get("Association", "")))
            if not (gene and drug and lab) or (gene, drug) in seen:
                continue
            seen.add((gene, drug))
            pmids = [p.strip() for p in (r.get("PMIDs") or "").split(",") if p.strip().isdigit()]
            # Positives are held to a higher bar: a curated clinical variant level as well.
            if lab == "positive" and _norm(gene) not in levels:
                continue
            buckets[lab].append({
                "gene": gene, "drug": drug, "label": lab,
                "clinpgx_level": levels.get(_norm(gene), ""),
                "n_pmids": len(pmids), "pmids": pmids[:8],
            })

    rng = random.Random(args.seed)
    rows, idx = [], 0
    for lab in ("positive", "negative", "disputed"):
        pool = buckets[lab]
        # Prefer pairs with literature attached: they are the ones a retrieval system can
        # actually find evidence for, so the benchmark tests the pipeline and not luck.
        pool.sort(key=lambda d: -d["n_pmids"])
        pool = pool[: max(args.per_class * 6, args.per_class)]
        rng.shuffle(pool)
        for rec in pool[: args.per_class]:
            rows.append({
                "id": idx,
                "question": TEMPLATE.format(gene=rec["gene"], drug=rec["drug"]),
                "reference": "",                       # no gold text; labels are the gold
                "bench_gene": rec["gene"], "bench_drug": rec["drug"],
                "bench_label": rec["label"], "bench_level": rec["clinpgx_level"],
                "bench_pmids": rec["pmids"],
            })
            idx += 1
    rng.shuffle(rows)
    for i, r in enumerate(rows):
        r["id"] = i

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    counts = {k: sum(1 for r in rows if r["bench_label"] == k) for k in buckets}
    print(f"wrote {args.out}: {len(rows)} pairs {counts}")
    print(f"pool sizes available: "
          f"{ {k: len(v) for k, v in buckets.items()} }")


if __name__ == "__main__":
    main()
