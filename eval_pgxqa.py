"""Score result files on the PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl).

    python eval_pgxqa.py phase15=results/pgxqa_phase15.jsonl llm=results/pgxqa_llmonly.jsonl \
        amgrag=results/pgxqa_amgrag.jsonl [--bertscore]

d2g / refusal_d2g (well-specified)  gene-list precision / recall / F1 against the CPIC gold
refusal_g2d (well-specified)        drug-list precision / recall / F1
refusal_* (misspecified)            refusal rate: PGxQA's own rule (answer contains 'unknown'
                                    or 'unable') and an extended rule that also accepts an
                                    explicit "not curated / no evidence / unsupported" statement
consult                             BERTScore F1 vs the expert response (--bertscore)
--ci B                              adds two tables: a 95% percentile-bootstrap interval per
                                    cell (B resamples of the items) and, for every system
                                    scored on the same items as --ci-ref (default: the first
                                    system), the paired difference ref - system with its
                                    interval and a two-sided bootstrap p-value

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
                               "not have actionable", "no direct evidence",
                               "misspelling", "not a real", "no known", "not an approved",
                               "cannot answer")      # PaperQA2's fixed refusal sentence; no other system uses the phrase


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
    ap.add_argument("--ci", type=int, default=0, metavar="B", help="bootstrap resamples for 95%% intervals (0 = off)")
    ap.add_argument("--ci-ref", help="reference system for the paired differences (default: first system)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    items = {it["id"]: it for it in load(args.items)}
    pgx = PharmGKBSearcher()
    gvocab = {g.upper() for g in pgx.gene_vocab}
    dvocab = set(pgx.drug_vocab)

    table = {}
    per_item = {}      # system -> metric -> {item id: score}, for the paired bootstrap
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
                agg[f"{sub}:P"].append((qid, p)); agg[f"{sub}:R"].append((qid, rc)); agg[f"{sub}:F1"].append((qid, f))
            if sub == "refusal_g2d" and not mis and it["bench_gold"]:
                p, rc, f = prf(drug_set(r, dvocab, it["bench_gold"]), {_norm(g) for g in it["bench_gold"]}, loose=True)
                agg["g2d:P"].append((qid, p)); agg["g2d:R"].append((qid, rc)); agg["g2d:F1"].append((qid, f))
            if sub.startswith("refusal"):
                key = "misspecified" if mis else "well-specified"
                agg[f"refusal({key}):pgxqa"].append((qid, float(refused(r["generated_answer"], REFUSAL_PGXQA))))
                agg[f"refusal({key}):extended"].append((qid, float(refused(r["generated_answer"], REFUSAL_EXT))))
            if sub == "consult":
                pairs_for_bert.append((qid, r["generated_answer"], it["reference"]))
        if args.bertscore and pairs_for_bert:
            from bert_score import score as bscore
            _, _, F = bscore([a for _, a, _ in pairs_for_bert], [b for _, _, b in pairs_for_bert],
                             model_type="roberta-large", lang="en", rescale_with_baseline=True)
            agg["consult:BERTScore-F1"] = [(q, float(x)) for (q, _, _), x in zip(pairs_for_bert, F)]
        table[name] = {k: (sum(x for _, x in v) / len(v), len(v)) for k, v in agg.items()}
        per_item[name] = {k: dict(v) for k, v in agg.items()}

    keys = sorted({k for t in table.values() for k in t})
    names = list(table)
    print("| metric | " + " | ".join(names) + " | n |")
    print("|---|" + "---|" * (len(names) + 1))
    for k in keys:
        n = max(table[s].get(k, (0, 0))[1] for s in names)
        print(f"| {k} | " + " | ".join(f"{table[s][k][0]:.3f}" if k in table[s] else "-" for s in names) + f" | {n} |")
    if args.ci:
        bootstrap_tables(per_item, names, keys, args.ci, args.ci_ref or names[0], args.seed)


def bootstrap_tables(per_item, names, keys, B, ref, seed):
    """95% percentile-bootstrap interval per cell (items resampled with replacement, B times)
    and the paired difference ref - system for every system scored on exactly the same items,
    with its interval and a two-sided bootstrap p-value (2 x the smaller tail of the resampled
    differences around zero). Metrics are means over items, so a resample is a mean of the
    per-item scores."""
    import numpy as np
    rng = np.random.default_rng(seed)

    def resample_means(vals):
        vals = np.asarray(vals, dtype=float)
        idx = rng.integers(0, len(vals), size=(B, len(vals)))
        return vals[idx].mean(axis=1)

    print()
    print(f"| metric (95% bootstrap CI, B={B}) | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    for k in keys:
        cells = []
        for s in names:
            d = per_item[s].get(k)
            if not d:
                cells.append("-"); continue
            m = resample_means(list(d.values()))
            cells.append(f"{np.mean(list(d.values())):.2f} [{np.percentile(m, 2.5):.2f}, {np.percentile(m, 97.5):.2f}]")
        print(f"| {k} | " + " | ".join(cells) + " |")
    others = [s for s in names if s != ref]
    if ref not in per_item or not others:
        return
    print()
    print(f"| {ref} minus system, paired [95% CI], p two-sided | " + " | ".join(others) + " |")
    print("|---|" + "---|" * len(others))
    for k in keys:
        cells = []
        for s in others:
            a, b = per_item[ref].get(k), per_item[s].get(k)
            if not a or not b or set(a) != set(b):
                cells.append("-"); continue
            diff = [a[q] - b[q] for q in a]
            m = resample_means(diff)
            p = 2 * min((m <= 0).mean(), (m >= 0).mean())
            cells.append(f"{np.mean(diff):+.2f} [{np.percentile(m, 2.5):+.2f}, {np.percentile(m, 97.5):+.2f}] p={min(p, 1.0):.2f}")
        print(f"| {k} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
