"""Quantify evidence dependence in cached ledger results (Phase 14 audit tool).

Two dependences the ledger's document-level dedup does not cover:

  1. The curated ClinPGx row contributes to BOTH the base term and the support sum of
     `evidence_ledger.compute_confidence` (bounded: a single weight-1.0 source multiplies
     the base by 1 + SUPPORT_K*ln(2) ~= 1.125).
  2. A digested paper can be the very study a curated row rests on: its PMID appears in
     relationships.tsv's citation list for the same pair, yet it is counted as an
     additional independent source.

This script measures both over a cached results file. Read-only; no LLM, no network.

    python eval_lineage.py results/adrclin_phase13_resolution.jsonl
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pgx_kb import PharmGKBSearcher


def main(path):
    pgx = PharmGKBSearcher()
    tot = curated_in_support = lit = dep = pairs_dep = 0
    for line in open(path, encoding="utf-8"):
        rec = json.loads(line)
        for e in rec.get("gene_ledger") or []:
            tot += 1
            cited = set(pgx.pmids_for_pair(e.get("gene", ""), e.get("drug", "")))
            dep_here = 0
            for s in e.get("supporting") or []:
                if s.get("study_type") == "curated":
                    curated_in_support += 1
                    continue
                m = re.match(r"PMID:(\d+)", s.get("ref", ""))
                if m:
                    lit += 1
                    if m.group(1) in cited:
                        dep += 1
                        dep_here += 1
            if dep_here:
                pairs_dep += 1
    print(f"file: {path}")
    print(f"ledger pairs: {tot}")
    print(f"pairs whose support list contains the curated row itself: {curated_in_support}")
    print(f"literature supporting sources (document-deduped): {lit}")
    print(f"  of these, PMIDs relationships.tsv cites for the SAME pair: {dep} "
          f"({pairs_dep} pairs affected)")
    print("note: shared cohorts across different publications are NOT detectable here.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/adrclin_phase13_resolution.jsonl")
