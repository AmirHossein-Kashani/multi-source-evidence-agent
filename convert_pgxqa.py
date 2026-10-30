"""PGxQA (Keat et al., PSB 2025; github.com/KarlKeat/PGxQA) -> dataset/pgxqa_eval.jsonl

Only the subsets this system is built for are taken; allele / diplotype lookups are not:
  d2g          drug_to_genes_queries.txt, researcher mode, every 4th drug (20 of 79):
               "What genes should I include in a pharmacogenetics panel for <drug>?"
               gold = CPIC-actionable genes (note: ClinPGx-level evidence is broader than
               CPIC-actionable, so precision is expected to be low by construction)
  refusal_d2g  refusal_test_questions.txt rows of category drug_to_genes: 20 real drugs,
               4 invented ones (the premise-check test)
  refusal_g2d  same for gene_to_drugs: 20 real genes, 3 invented
  consult      pgx_consult_questions.txt: 10 open questions with expert responses

Output schema matches run_genmedgpt.py: {id, question, reference} plus bench_* fields that
the runner copies into every result record.
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(HERE, "dataset", "PGxQA", "test_queries")
OUT = os.path.join(HERE, "dataset", "pgxqa_eval.jsonl")   # beside the clone: the clone has its own .git, so nothing inside it can be tracked


def rows(name):
    with open(os.path.join(Q, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    items = []

    def add(subset, question, reference, gold, misspecified=False, **extra):
        items.append({"id": len(items), "question": question, "reference": reference or "",
                      "bench_subset": subset, "bench_gold": gold,
                      "bench_misspecified": bool(misspecified), **extra})

    d2g = [r for r in rows("drug_to_genes_queries.txt") if r["mode"] == "researcher"][::4][:20]
    for r in d2g:
        add("d2g", r["question"], r["answer"], r["genes"].split(";"), bench_drug=r["drug"])

    # The refusal file has no answer column filled in; gold for its well-specified rows is
    # joined from the main query files by the drug / gene named in the question. Rows whose
    # drug or gene is not CPIC-covered keep an empty gold (refusal rate only, no list score).
    d2g_gold = {r["drug"].lower(): r["genes"].split(";") for r in rows("drug_to_genes_queries.txt")}
    g2d_gold = {r["gene"].upper(): r["drugs"].split(";") for r in rows("gene_to_drugs_queries.txt")}
    for r in rows("refusal_test_questions.txt"):
        if r["category"] not in ("drug_to_genes", "gene_to_drugs"):
            continue
        mis = r["is_misspecified"].strip().lower() == "true"
        q = r["question"]
        gold, key = [], ""
        if not mis:
            if r["category"] == "drug_to_genes":
                m = re.search(r"patient ([A-Za-z0-9\-]+)\.|guidelines for ([A-Za-z0-9\-]+)\?", q)
                key = next((x for x in (m.groups() if m else ()) if x), "").lower()
                gold = d2g_gold.get(key, [])
            else:
                m = re.search(r"guidelines for ([A-Za-z0-9\-]+)\?", q)
                key = (m.group(1) if m else "").upper()
                gold = g2d_gold.get(key, [])
        add("refusal_" + ("d2g" if r["category"] == "drug_to_genes" else "g2d"),
            q, ";".join(gold), gold, misspecified=mis, bench_key=key)

    for r in rows("pgx_consult_questions.txt"):
        add("consult", r["question"], r["response"], [])

    with open(OUT, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    from collections import Counter
    c = Counter(it["bench_subset"] for it in items)
    print(f"wrote {len(items)} items -> {OUT}")
    print("  " + ", ".join(f"{k}={v}" for k, v in c.items()),
          f"| misspecified={sum(it['bench_misspecified'] for it in items)}")


if __name__ == "__main__":
    main()
