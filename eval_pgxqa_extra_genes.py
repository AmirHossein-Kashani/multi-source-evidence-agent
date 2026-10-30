"""Where do the extra drug->genes answers come from?

For every gene a system names beyond PGxQA's CPIC-actionable gold, this checks whether ClinPGx
holds a row for that gene and the question's drug (an association at any level, an ambiguous
call, or a negative) or no row at all, and for phase-15 files which answer field named it
(risk_genes, the candidate-associations block, or the prose only). Same gene extraction as
eval_pgxqa.py. Used for the "where the extra answers come from" table of section 3 in
results/benchmarks.md.

    python eval_pgxqa_extra_genes.py phase15=results/pgxqa_phase15.jsonl tables_only=results/pgxqa_clinpgx_only.jsonl ...
"""
import argparse
import os
import re

os.environ.setdefault("AMG_MESH_ONLINE", "0")
import eval_pgxqa as ev            # noqa: E402
from pgx_kb import PharmGKBSearcher  # noqa: E402


def drug_of(item: dict) -> str:
    d = item.get("bench_drug") or item.get("bench_key") or ""
    if not d:
        m = re.search(r"give my patient ([A-Za-z0-9\-]+)", item["question"])
        d = m.group(1) if m else ""
    return d


def strip_alleles(names) -> set:
    return {x.split("*")[0].upper() for x in (names or []) if isinstance(x, str)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("systems", nargs="+", help="name=results/pgxqa_<suffix>.jsonl")
    ap.add_argument("--items", default="dataset/pgxqa_eval.jsonl")
    ap.add_argument("--by-source", action="append", default=[],
                    help="system name whose extra genes are also split by answer field (repeatable)")
    args = ap.parse_args()
    pgx = PharmGKBSearcher()
    gvocab = {g.upper() for g in pgx.gene_vocab}
    items = {it["id"]: it for it in ev.load(args.items)}

    print("| system | subset | extra genes | ClinPGx row for the drug: associated / ambiguous / not associated | no row |")
    print("|---|---|---|---|---|")
    by_source = {}
    for spec in args.systems:
        name, path = spec.split("=", 1)
        recs = {r["id"]: r for r in ev.load(path) if r.get("generated_answer")}
        for subset in ("d2g", "refusal_d2g"):
            extra, kinds, no_row = 0, {"associated": 0, "ambiguous": 0, "not associated": 0}, 0
            for qid, it in items.items():
                if it["bench_subset"] != subset or it["bench_misspecified"] or not it["bench_gold"]:
                    continue
                r = recs.get(qid)
                if r is None:
                    continue
                gold = {g.upper() for g in it["bench_gold"]}
                pred = ev.gene_set(r, gvocab, it["bench_gold"])
                drug = drug_of(it)
                for g in pred - gold:
                    extra += 1
                    a = pgx.association_detailed(g, drug) if drug else None
                    if a:
                        kinds[a.get("assoc", "ambiguous")] = kinds.get(a.get("assoc", "ambiguous"), 0) + 1
                    else:
                        no_row += 1
                    if name in args.by_source:
                        src = ("risk_genes" if g in strip_alleles(r.get("risk_genes"))
                               else "candidate_genes" if g in strip_alleles(r.get("candidate_genes"))
                               else "prose only")
                        cell = by_source.setdefault(name, {}).setdefault(subset, {}).setdefault(src, [0, 0])
                        cell[0] += 1
                        cell[1] += 0 if a else 1
            print(f"| {name} | {subset} | {extra} | {kinds['associated']} / {kinds['ambiguous']} / {kinds['not associated']} | {no_row} |")
    for name, subsets in by_source.items():
        print(f"\n{name}: extra genes by answer field (count, of which no ClinPGx row)")
        for subset, srcs in subsets.items():
            print(f"  {subset}: " + "; ".join(f"{k} {v[0]} ({v[1]} no row)" for k, v in sorted(srcs.items())))


if __name__ == "__main__":
    main()
