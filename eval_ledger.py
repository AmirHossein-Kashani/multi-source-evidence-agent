"""Evaluate the evidence ledger: gene recall, confidence CALIBRATION, contradiction detection.

`ClinPGx-valid %` (used for phases 3-10) is the wrong metric for this goal: it scores a gene as
invalid merely because ClinPGx has not curated it, which penalises exactly the novel findings
the research wants. It is reported here only as a descriptive count.

Two inputs:

  * the ADR question set  -> qualitative: how many genes surfaced, how many disputed, do the
                            answers cite their refs
  * pgx_confidence_bench  -> quantitative: each item is ONE gene-drug pair carrying a ClinPGx
                            label (positive / negative / disputed), so confidence can be
                            calibrated and contradiction detection scored

    python eval_ledger.py --bench results/bench_phase11_ledger.jsonl \
                          --adr   results/adrclin_phase11_ledger.jsonl
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    if not path or not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def spearman(xs, ys):
    """Rank correlation without scipy (ties averaged)."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    if len(xs) < 3:
        return float("nan")
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def entry_for_pair(rec, gene, drug):
    """The ledger entry matching the benchmark's target pair, if the system found it."""
    g, d = gene.strip().upper(), (drug or "").strip().lower()
    best = None
    for e in rec.get("gene_ledger", []) or []:
        if e.get("gene", "").strip().upper() != g:
            continue
        if d and e.get("drug", "").strip().lower() and e["drug"].strip().lower() != d:
            continue
        if best is None or e["confidence"] > best["confidence"]:
            best = e
    return best


def eval_bench(rows, w):
    w("## Benchmark — labelled gene–drug pairs")
    w("")
    if not rows:
        w("_No benchmark results found._")
        w("")
        return
    labels = Counter(r.get("bench_label") for r in rows)
    w(f"{len(rows)} pairs: " + ", ".join(f"**{k}** {v}" for k, v in sorted(labels.items())))
    w("")

    found, conf_by_label, missing = [], defaultdict(list), Counter()
    for r in rows:
        e = entry_for_pair(r, r.get("bench_gene", ""), r.get("bench_drug", ""))
        if e is None:
            missing[r.get("bench_label")] += 1
            continue
        found.append((r, e))
        conf_by_label[r["bench_label"]].append(e["confidence"])

    w("### Did the system surface the target pair at all?")
    w("")
    w("| Label | pairs | target found | recall |")
    w("|---|---|---|---|")
    for lab in ("positive", "negative", "disputed"):
        tot = labels.get(lab, 0)
        got = len(conf_by_label.get(lab, []))
        w(f"| {lab} | {tot} | {got} | {100*got/tot:.0f}% |" if tot else f"| {lab} | 0 | 0 | – |")
    w("")

    w("### Confidence calibration")
    w("")
    w("Mean confidence should be highest for `positive`, lowest for `negative`.")
    w("")
    w("| Label | n | mean confidence | median | label distribution |")
    w("|---|---|---|---|---|")
    for lab in ("positive", "negative", "disputed"):
        v = sorted(conf_by_label.get(lab, []))
        if not v:
            w(f"| {lab} | 0 | – | – | – |")
            continue
        dist = Counter(e["label"] for r, e in found if r["bench_label"] == lab)
        w(f"| {lab} | {len(v)} | {sum(v)/len(v):.3f} | {v[len(v)//2]:.3f} | "
          f"{', '.join(f'{k}:{c}' for k, c in dist.most_common())} |")
    w("")

    pos = conf_by_label.get("positive", [])
    neg = conf_by_label.get("negative", [])
    if pos and neg:
        sep = (sum(pos)/len(pos)) - (sum(neg)/len(neg))
        w(f"**Separation (positive − negative): {sep:+.3f}** — positive above negative is the "
          f"property that makes the score usable.")
        w("")
        # ordinal target: negative 0, disputed 1, positive 2
        order = {"negative": 0, "disputed": 1, "positive": 2}
        xs = [e["confidence"] for r, e in found]
        ys = [order[r["bench_label"]] for r, e in found]
        w(f"**Spearman(confidence, label order) = {spearman(xs, ys):.3f}** over {len(xs)} pairs.")
        w("")

    w("### Contradiction detection")
    w("")
    w("`disputed=True` should fire on `disputed` pairs (ClinPGx `ambiguous`) and stay quiet on "
      "clean positives.")
    w("")
    tp = sum(1 for r, e in found if r["bench_label"] == "disputed" and e["disputed"])
    fn = sum(1 for r, e in found if r["bench_label"] == "disputed" and not e["disputed"])
    fp = sum(1 for r, e in found if r["bench_label"] != "disputed" and e["disputed"])
    tn = sum(1 for r, e in found if r["bench_label"] != "disputed" and not e["disputed"])
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec == prec and rec == rec and (prec + rec) else float("nan")
    w(f"| | flagged disputed | not flagged |")
    w("|---|---|---|")
    w(f"| **is disputed** | {tp} | {fn} |")
    w(f"| **is not** | {fp} | {tn} |")
    w("")
    w(f"precision **{prec:.2f}** · recall **{rec:.2f}** · F1 **{f1:.2f}**")
    w("")
    flags = Counter(f["type"] for r, e in found for f in e.get("contradictions", []))
    if flags:
        w("Flag types raised: " + ", ".join(f"`{k}` {v}" for k, v in flags.most_common()))
        w("")


def eval_adr(rows, w):
    w("## ADR question set — recall and reporting")
    w("")
    if not rows:
        w("_No ADR ledger results found._")
        w("")
        return
    genes = [len(r.get("gene_ledger", []) or []) for r in rows]
    disputed = sum(1 for r in rows for e in (r.get("gene_ledger") or []) if e["disputed"])
    total = sum(genes)
    cited = sum(1 for r in rows if re.search(r"(PMID:\d+|ClinPGx:)", r.get("generated_answer", "")))
    labs = Counter(e["label"] for r in rows for e in (r.get("gene_ledger") or []))
    w(f"- **{total} gene–drug pairs** across {len(rows)} questions "
      f"(mean {total/len(rows):.1f} per question; previous phases named 2–3)")
    w(f"- **{disputed}** carry a contradiction flag")
    w(f"- confidence labels: " + ", ".join(f"{k} {v}" for k, v in labs.most_common()))
    w(f"- answers citing a reference: **{cited}/{len(rows)}** "
      f"(phase 10 scored 0/10)")
    w("")
    w("| Q | pairs | disputed | highest-confidence genes |")
    w("|---|---|---|---|")
    for r in rows:
        led = r.get("gene_ledger") or []
        top = ", ".join(f"{e['gene']} {e['confidence']:.2f}" for e in led[:3]) or "—"
        w(f"| Q{r['id']+1} | {len(led)} | {sum(1 for e in led if e['disputed'])} | {top} |")
    w("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default=os.path.join(HERE, "results", "bench_phase11_ledger.jsonl"))
    ap.add_argument("--bench-input", default=os.path.join(
        HERE, "dataset", "PharmGKB", "pgx_confidence_bench.jsonl"),
        help="labelled source; joined by id when the results predate label pass-through")
    ap.add_argument("--adr", default=os.path.join(HERE, "results", "adrclin_phase11_ledger.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "ledger_evaluation.md"))
    args = ap.parse_args()

    L = []
    w = L.append
    w("# Evidence ledger — evaluation")
    w("")
    w("The system now reports **every** candidate gene with a rule-computed confidence and an "
      "explicit contradiction flag, instead of naming 2–3 genes in prose. Confidence is "
      "computed in `evidence_ledger.py` from the ClinPGx evidence level, study types, the "
      "number of independent supporting sources and the weight of refuting ones — the model "
      "never emits the number, which is what makes calibration meaningful.")
    w("")
    bench_rows = load(args.bench)
    if bench_rows and not bench_rows[0].get("bench_label"):
        gold = {g["id"]: g for g in load(args.bench_input)}
        for r in bench_rows:                       # recover labels by id
            r.update({k: v for k, v in gold.get(r.get("id"), {}).items()
                      if k.startswith("bench_")})
        print(f"[eval] joined {len(bench_rows)} results to gold labels by id")
    eval_bench(bench_rows, w)
    eval_adr(load(args.adr), w)
    w("## Caveats")
    w("")
    w("- The benchmark labels come from ClinPGx, and the system also retrieves from ClinPGx, so "
      "calibration is partly self-consistent by construction. It is still informative for the "
      "`negative` and `disputed` classes, where the system must *disagree* with what its own "
      "retrieval surfaces, and for the literature-derived component of every score.")
    w("- `ClinPGx-valid %` from the earlier phase comparison is retired as a quality metric: it "
      "marks uncurated literature findings as wrong, which is the opposite of the goal here.")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    open(args.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
