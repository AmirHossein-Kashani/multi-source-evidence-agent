"""Contradiction-resolution cards for the 10 ADR questions (phase 13).

Renders, per question, each gene-drug pair resolved to a status with the reason the sources
disagree, the evidence tiers behind it, the study contexts, and the actionable conclusion.
"""
import argparse, json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["CURATED-LITERATURE CONFLICT", "CONFLICTING", "CONTEXT-DEPENDENT",
         "CONSISTENT", "INSUFFICIENT"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(HERE, "results", "adrclin_phase13_resolution.jsonl"))
    ap.add_argument("--input", default=os.path.join(HERE, "dataset", "PharmGKB", "adr_clinical.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "phase13_contradiction_cards.md"))
    a = ap.parse_args()

    recs = {json.loads(l)["id"]: json.loads(l) for l in open(a.results, encoding="utf-8") if l.strip()}
    qs = [json.loads(l) for l in open(a.input, encoding="utf-8") if l.strip()]
    cards = [c for r in recs.values() for c in r.get("contradiction_cards", [])]

    L, w = [], None
    w = L.append
    w("# Phase 13 — contradiction resolution cards")
    w("")
    w("Each gene–drug pair is resolved to a status with the **reason** the sources disagree. "
      "Evidence is tiered (curated / clinical / mechanistic / narrative) and only comparable "
      "tiers may conflict, so an in-vitro null result no longer counts as contradicting a "
      "clinical association. Classification is computed in `contradiction_layer.py`; the model "
      "extracts the fields, the module decides.")
    w("")
    w("| Status | Meaning | n |")
    w("|---|---|---|")
    dist = Counter(c["status"] for c in cards)
    means = {
        "CURATED-LITERATURE CONFLICT": "the curated database and the retrieved literature disagree",
        "CONFLICTING": "comparable credible evidence supports both directions",
        "CONTEXT-DEPENDENT": "the conflict disappears once population / dose / type is fixed",
        "CONSISTENT": "comparable credible evidence agrees",
        "INSUFFICIENT": "too little comparable clinical evidence to judge",
    }
    for s in ORDER:
        w(f"| **{s}** | {means[s]} | {dist.get(s,0)} |")
    w(f"| | **total** | **{len(cards)}** |")
    w("")
    axes = Counter(r["axis"] for c in cards for r in c.get("reasons", []))
    if axes:
        w("**Why sources disagreed:** " + ", ".join(f"`{k}` {v}" for k, v in axes.most_common()))
        w("")
    w("---")
    w("")

    for i, q in enumerate(qs, start=1):
        rec = recs.get(q["id"])
        if not rec:
            continue
        cs = rec.get("contradiction_cards", [])
        w(f"## Q{i}. {q['question']}")
        w("")
        w(f"*{len(cs)} pairs — " + ", ".join(f"{k} {v}" for k, v in
                                             Counter(c["status"] for c in cs).most_common()) + "*")
        w("")
        shown = [c for c in cs if c["status"] != "INSUFFICIENT"] or cs[:3]
        for c in shown[:8]:
            var = f" ({c['variants'][0]})" if c.get("variants") else ""
            w(f"### {c['gene']}{var} — {c['drug']}")
            w("")
            w(f"**Status: {c['status']}**  ·  confidence {c['confidence']:.2f} [{c['label']}]")
            w("")
            for r in c.get("reasons", []):
                extra = ""
                if r.get("supporting_values"):
                    extra = (f" — supporting: {', '.join(r['supporting_values'][:3])}; "
                             f"refuting: {', '.join(r.get('refuting_values', [])[:3])}")
                w(f"- **Why:** {r['detail']}{extra}")
            for n in c.get("notes", []):
                w(f"- *Note:* {n}")
            if c.get("supporting"):
                w("- **Supporting:** " + "; ".join(f"`{s['ref']}` ({s['study_type']})"
                                                   for s in c["supporting"][:3]))
            if c.get("refuting"):
                w("- **Refuting:** " + "; ".join(f"`{s['ref']}` ({s['study_type']})"
                                                 for s in c["refuting"][:3]))
            for fld, lab in (("populations", "Populations"), ("cancer_types", "Cancer types"),
                             ("endpoints", "Endpoints")):
                if c.get(fld):
                    w(f"- **{lab}:** {', '.join(c[fld][:3])}")
            tiers = {k: v for k, v in (c.get("evidence_tiers") or {}).items()
                     if v["support"] or v["refute"]}
            if tiers:
                w("- **Evidence tiers:** " + ", ".join(
                    f"{k} ({v['support']}+/{v['refute']}−)" for k, v in tiers.items()))
            w("")
            w(f"> {c['conclusion']}")
            w("")
        if len(cs) > len(shown):
            w(f"<sub>{len(cs) - len(shown)} further pairs resolved INSUFFICIENT "
              f"(fewer than two comparable clinical sources).</sub>")
            w("")
        w("---")
        w("")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {a.out} ({len(cards)} cards)")


if __name__ == "__main__":
    main()
