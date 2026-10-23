"""Build the masked-association recovery task (E1 in docs/PLAN.md).

Selects curated gene-drug pairs, writes copies of the KB tables with those pairs' rows
REMOVED, and emits the matching question list. Running a configuration against the masked
tables (env AMG_KB_CLINVAR / AMG_KB_REL, read by AMG-with-KG.py) turns "find what is not
in the graph" into a controlled task: the association is real, its literature exists, only
the curated rows are hidden. Success = the masked gene resurfaces (path proposal, ledger
candidate, answer).

Masking is CLASS-AWARE: a gene is removed for the drug's own name, its brand synonyms and
its class / sibling tokens (pgx_kb.expand_drug_detailed: 'platinum compounds' for
cisplatin, 'anthracyclines and related substances' and daunorubicin for doxorubicin),
otherwise the class row would still make the gene look curated. Gene-DISEASE rows are
kept: they are what lets path pattern A propose the gene again.

This measures ASSOCIATION RECOVERY, not biological novelty.

    python make_masked_recovery.py --pairs ACYP2:cisplatin:ototoxicity \
        SLC28A3:doxorubicin:cardiotoxicity --outdir dataset/ADR_DataSet_masked
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pgx_kb import DEFAULT_CLINVAR, DEFAULT_REL, PharmGKBSearcher, _norm

QUESTION = ("Which pharmacogenomic biomarkers predict {drug}-induced {outcome}, and how strong "
            "is the evidence for each? Note any disagreement between sources.")

DEFAULT_PAIRS = ["ACYP2:cisplatin:ototoxicity", "TPMT:cisplatin:ototoxicity",
                 "COMT:cisplatin:ototoxicity", "GSTP1:cisplatin:ototoxicity",
                 "ABCC3:cisplatin:ototoxicity", "SLC16A5:cisplatin:ototoxicity",
                 "SLC28A3:doxorubicin:cardiotoxicity", "RARG:doxorubicin:cardiotoxicity",
                 "UGT1A6:doxorubicin:cardiotoxicity", "CBR3:doxorubicin:cardiotoxicity"]


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
    ap.add_argument("--pairs", nargs="+", default=DEFAULT_PAIRS,
                    help="GENE:drug[:outcome] triples to mask")
    ap.add_argument("--outdir", default=os.path.join(HERE, "dataset", "ADR_DataSet_masked"))
    args = ap.parse_args()

    try:
        from mesh_terms import MeshVocab
        vocab = MeshVocab(online=False)          # cache only; class names for the dev drugs are cached
    except Exception:
        vocab = None
    pgx = PharmGKBSearcher(vocab=vocab)

    pairs = []
    for p in args.pairs:
        parts = p.split(":")
        g, d = parts[0].strip().upper(), _norm(parts[1])
        outcome = _norm(parts[2]) if len(parts) > 2 else ""
        ex = pgx.expand_drug_detailed(d)
        tokens = sorted(set(ex["exact"]) | set(ex["class"]))
        pairs.append({"gene": g, "drug": d, "outcome": outcome, "tokens": tokens})
        print(f"{g}-{d}: masking chemical tokens {tokens}")
    os.makedirs(args.outdir, exist_ok=True)

    def chem_hits(chems_text, tokens):
        c = _norm(chems_text)
        return any(t == c or t in c for t in tokens)

    def hit_clinvar(header, row):
        r = dict(zip(header, row))
        g = r.get("gene", "").strip().upper()
        return any(g == p["gene"] and chem_hits(r.get("chemicals", ""), p["tokens"]) for p in pairs)

    def hit_rel(header, row):
        r = dict(zip(header, row))
        names = [r.get("Entity1_name", ""), r.get("Entity2_name", "")]
        types = [r.get("Entity1_type", ""), r.get("Entity2_type", "")]
        genes = {n.strip().upper() for n, t in zip(names, types) if t == "Gene"}
        chems = [n for n, t in zip(names, types) if t == "Chemical"]
        return any(p["gene"] in genes and any(chem_hits(c, p["tokens"]) for c in chems) for p in pairs)

    k, m = mask_tsv(DEFAULT_CLINVAR, os.path.join(args.outdir, "clinicalVariants.tsv"), hit_clinvar)
    print(f"clinicalVariants: kept {k}, removed {m}")
    k, m = mask_tsv(DEFAULT_REL, os.path.join(args.outdir, "relationships.tsv"), hit_rel)
    print(f"relationships:    kept {k}, removed {m}")

    qpath = os.path.join(args.outdir, "masked_questions.jsonl")
    with open(qpath, "w", encoding="utf-8") as f:
        for i, p in enumerate(pairs):
            f.write(json.dumps({
                "id": i, "question": QUESTION.format(drug=p["drug"], outcome=p["outcome"] or "adverse reactions"),
                "reference": "", "bench_masked_gene": p["gene"], "bench_masked_drug": p["drug"],
                "bench_outcome": p["outcome"]}) + "\n")
    with open(os.path.join(args.outdir, "masked_pairs.json"), "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=1)
    print(f"questions: {qpath}")
    print("Masked pairs:", ", ".join(f"{p['gene']}-{p['drug']}" for p in pairs))


if __name__ == "__main__":
    main()
