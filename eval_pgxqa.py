"""Score result files on the PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl).

    python eval_pgxqa.py phase15=results/pgxqa_phase15.jsonl llm=results/pgxqa_llmonly.jsonl \
        amgrag=results/pgxqa_amgrag.jsonl [--bertscore]

d2g / refusal_d2g (well-specified)  gene-list precision / recall / F1 against the CPIC gold
refusal_g2d (well-specified)        drug-list precision / recall / F1
refusal_* (misspecified)            refusal rate: PGxQA's own rule (answer contains 'unknown'
                                    or 'unable') and an extended rule that also accepts an
                                    explicit "not curated / no evidence / unsupported" statement
consult                             BERTScore F1 vs the expert response (--bertscore)

Predicted gene set = risk_genes + candidate_genes + gene symbols named in the answer text
(symbols recognised against the ClinPGx gene vocabulary + the gold set). This system answers
in prose, PGxQA expected a bare list; the extraction makes the comparison symmetric across
systems. Scores are for a researcher-mode subsample and are NOT comparable to the PGxQA
paper's full-benchmark numbers.
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pgx_kb import PharmGKBSearcher, _norm

ITEMS = os.path.join(HERE, "dataset", "PGxQA", "pgxqa_eval.jsonl")
_SYM = re.compile(r"\b[A-Z][A-Z0-9]{1,9}(?:-[A-Z0-9]+)?\b")
REFUSAL_PGXQA = ("unknown", "unable")
REFUSAL_EXT = REFUSAL_PGXQA + ("not curated", "no curated", "not a recognized", "not recognized",
                               "no evidence", "unsupported", "no association", "not a known",
                               "could not find", "does not appear", "not found", "no pharmacogen",
                               "not an established", "no established", "no actionable",
                               "not have actionable", "no direct evidence", "insufficient",
                               "misspelling", "not a real", "no known", "not an approved")


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def gene_set(rec, vocab, gold):
    out = {g.strip().upper() for g in (rec.get("risk_genes") or []) + (rec.get("candidate_genes") or [])
           if isinstance(g, str) and g.strip()}
    out = {re.sub(r"\*.*$", "", g) for g in out}
    text = rec.get("generated_answer") or ""
    ok = vocab | {g.upper() for g in gold}
    out |= {t for t in _SYM.findall(text) if t in ok}
    return {g for g in out if g}


def drug_set(rec, dvocab, gold):
    out = {_norm(d) for d in (rec.get("drugs") or []) if isinstance(d, str)}
    text = _norm(rec.get("generated_answer") or "")
    for d in dvocab | {_norm(g) for g in gold}:
        if len(d) >= 4 and re.search(r"(?<![a-z0-9])" + re.escape(d) + r"(?![a-z0-9])", text):
            out.add(d)
    return out


def prf(pred, gold, loose=False):
    gold = {g for g in gold if g}
    if loose:
        hit_p = {p for p in pred if any(p == g or p in g or g in p for g in gold)}
        hit_g = {g for g in gold if any(p == g or p in g or g in p for p in pred)}
    else:
        hit_p = pred & gold; hit_g = gold & pred
    p = len(hit_p) / len(pred) if pred else 0.0
    r = len(hit_g) / len(gold) if gold else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def refused(text, words):
    t = (text or "").lower()
    return any(w in t for w in words)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("systems", nargs="+", help="name=path/to/results.jsonl")
    ap.add_argument("--items", default=ITEMS)
    ap.add_argument("--bertscore", action="store_true")
    args = ap.parse_args()
    items = {it["id"]: it for it in load(args.items)}
    pgx = PharmGKBSearcher()
    gvocab = {g.upper() for g in pgx.gene_vocab}
    dvocab = set(pgx.drug_vocab)

    table = {}
    for spec in args.systems:
        name, path = spec.split("=", 1)
        recs = {r["id"]: r for r in load(path) if r.get("generated_answer")}
        agg = defaultdict(list)
        pairs_for_bert = []
        for qid, it in items.items():
            r = recs.get(qid)
            if r is None:
                continue
            sub, mis = it["bench_subset"], it["bench_misspecified"]
            if sub in ("d2g", "refusal_d2g") and not mis and it["bench_gold"]:
                p, rc, f = prf(gene_set(r, gvocab, it["bench_gold"]), {g.upper() for g in it["bench_gold"]})
                agg[f"{sub}:P"].append(p); agg[f"{sub}:R"].append(rc); agg[f"{sub}:F1"].append(f)
            if sub == "refusal_g2d" and not mis and it["bench_gold"]:
                p, rc, f = prf(drug_set(r, dvocab, it["bench_gold"]), {_norm(g) for g in it["bench_gold"]}, loose=True)
                agg["g2d:P"].append(p); agg["g2d:R"].append(rc); agg["g2d:F1"].append(f)
            if sub.startswith("refusal"):
                key = "misspecified" if mis else "well-specified"
                agg[f"refusal({key}):pgxqa"].append(float(refused(r["generated_answer"], REFUSAL_PGXQA)))
                agg[f"refusal({key}):extended"].append(float(refused(r["generated_answer"], REFUSAL_EXT)))
            if sub == "consult":
                pairs_for_bert.append((r["generated_answer"], it["reference"]))
        if args.bertscore and pairs_for_bert:
            from bert_score import score as bscore
            _, _, F = bscore([a for a, _ in pairs_for_bert], [b for _, b in pairs_for_bert],
                             model_type="roberta-large", lang="en", rescale_with_baseline=True)
            agg["consult:BERTScore-F1"] = [float(x) for x in F]
        table[name] = {k: (sum(v) / len(v), len(v)) for k, v in agg.items()}

    keys = sorted({k for t in table.values() for k in t})
    names = list(table)
    print("| metric | " + " | ".join(names) + " | n |")
    print("|---|" + "---|" * (len(names) + 1))
    for k in keys:
        n = max(table[s].get(k, (0, 0))[1] for s in names)
        print(f"| {k} | " + " | ".join(f"{table[s][k][0]:.3f}" if k in table[s] else "-" for s in names) + f" | {n} |")


if __name__ == "__main__":
    main()
