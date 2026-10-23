"""Score the masked-association recovery task (E1).

    python eval_masked_recovery.py phase15=results/maskrec_phase15.jsonl \
        phase13=results/maskrec_phase13.jsonl llm=results/maskrec_llmonly.jsonl

For every masked (gene, drug) pair and every system: was the gene proposed by a path
(and by which pattern), did it enter the ledger, as a candidate, with what confidence,
in which search round was it first queried, and is it named in the answer / risk_genes /
candidate_genes. Rates per system at the end.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("systems", nargs="+", help="name=results.jsonl")
    args = ap.parse_args()
    systems = {}
    for spec in args.systems:
        name, path = spec.split("=", 1)
        systems[name] = {r["id"]: r for r in load(path)}

    rows = []
    for name, recs in systems.items():
        for qid, r in sorted(recs.items()):
            g = (r.get("bench_masked_gene") or "").upper()
            if not g:
                continue
            pat = re.compile(r"(?<![A-Z0-9])" + re.escape(g) + r"(?![A-Z0-9])")
            cand = next((c for c in r.get("path_candidates", []) if c["gene"].upper() == g), None)
            led = [e for e in r.get("gene_ledger", []) if e["gene"].upper() == g]
            round_found = next((x["round"] for x in r.get("search_rounds", [])
                                if any(q["edge"].split("|")[0].upper() == g for q in x["queries"])), None)
            in_digest = any(g in [x.upper() for x in d.get("genes_supported", []) + d.get("genes_refuted", [])]
                            for d in r.get("paper_digests", []))
            rows.append({
                "system": name, "gene": g, "drug": r.get("bench_masked_drug", ""),
                "proposed": bool(cand), "via": "/".join(v.split(":")[1] for v in cand["via"]) if cand else "",
                "queried_round": round_found,
                "in_digest": in_digest,
                "in_ledger": bool(led),
                "candidate": any(e.get("candidate") for e in led),
                "confidence": max((e["confidence"] for e in led), default=None),
                "in_answer": bool(pat.search((r.get("generated_answer") or "").upper())),
                "in_risk_genes": any(x.upper().startswith(g) for x in (r.get("risk_genes") or []) if isinstance(x, str)),
                "in_candidate_genes": any(x.upper().startswith(g) for x in (r.get("candidate_genes") or []) if isinstance(x, str)),
            })

    cols = ["system", "gene", "drug", "proposed", "via", "queried_round", "in_digest", "in_ledger",
            "candidate", "confidence", "in_answer", "in_risk_genes", "in_candidate_genes"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        print("| " + " | ".join("" if r[c] is None else (f"{r[c]:.2f}" if isinstance(r[c], float) else str(r[c])) for c in cols) + " |")
    print("\n## Recovery rates")
    print("| system | n | proposed | in digest | in ledger | candidate | in answer | in risk/candidate genes |")
    print("|---|---|---|---|---|---|---|---|")
    for name in systems:
        rs = [r for r in rows if r["system"] == name]
        if not rs:
            continue
        n = len(rs)
        def rate(k):
            return f"{sum(1 for r in rs if r[k]) / n:.0%}"
        both = sum(1 for r in rs if r["in_risk_genes"] or r["in_candidate_genes"]) / n
        print(f"| {name} | {n} | {rate('proposed')} | {rate('in_digest')} | {rate('in_ledger')} | {rate('candidate')} | {rate('in_answer')} | {both:.0%} |")


if __name__ == "__main__":
    main()
