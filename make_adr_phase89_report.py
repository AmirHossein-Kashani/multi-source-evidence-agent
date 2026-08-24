"""Search-shape report for the combined-topic phases (8/9).

Phases 8/9 search RELATIONSHIPS: entities related in the knowledge graph go into one
conjunctive PubMed query, and the LLM decides how many terms to combine. This report answers
"what shape did the search take?" -- how many queries were 2-term, 3-term, 4-term, how often
an over-constrained query had to back off, and what each shape actually returned.

    python make_adr_phase89_report.py [--tag adrclin]
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

DRUG_TERMS = {"cisplatin": ["cisplatin", "platinol", "cddp", "platinum"],
              "doxorubicin": ["doxorubicin", "adriamycin", "anthracycline", "daunorubicin"]}
ADR_TERMS = {"ototoxicity": ["ototox", "hearing", "deaf", "tinnitus", "cochlea", "audi"],
             "neuropathy": ["neuropath", "neurotox"],
             "cardiotoxicity": ["cardiotox", "cardiac", "heart", "cardiomyopath"],
             "mucositis": ["mucositis", "stomatitis"]}
QKEY = {0: ("cisplatin", "ototoxicity"), 1: ("cisplatin", "ototoxicity"),
        2: ("cisplatin", "ototoxicity"), 3: ("cisplatin", "ototoxicity"),
        4: ("cisplatin", "neuropathy"), 5: ("doxorubicin", "cardiotoxicity"),
        6: ("doxorubicin", "cardiotoxicity"), 7: ("doxorubicin", "cardiotoxicity"),
        8: ("doxorubicin", "cardiotoxicity"), 9: ("doxorubicin", "mucositis")}


def load(path):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out[r.get("id")] = r
    return out


def on_topic_rate(recs):
    """Share of retrieved papers mentioning both the question's drug and its adverse effect."""
    hit = tot = 0
    for qid, rec in recs.items():
        d, a = QKEY.get(qid, ("", ""))
        dt, at = DRUG_TERMS.get(d, []), ADR_TERMS.get(a, [])
        seen = set()
        for e in rec.get("evidence_log", []) or []:
            if e.get("source") != "PubMed" or e.get("ref") in seen:
                continue
            seen.add(e.get("ref"))
            hay = f"{e.get('title','')} {e.get('snippet','')}".lower()
            tot += 1
            if any(t in hay for t in dt) and any(t in hay for t in at):
                hit += 1
    return (100.0 * hit / tot if tot else None), tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="adrclin")
    ap.add_argument("--results-dir", default=os.path.join(HERE, "results"))
    ap.add_argument("--input", default=os.path.join(HERE, "dataset", "PharmGKB", "adr_clinical.jsonl"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    R = args.results_dir

    p8 = load(os.path.join(R, f"{args.tag}_phase8_combo_abstracts.jsonl"))
    p9 = load(os.path.join(R, f"{args.tag}_phase9_combo_fulltext.jsonl"))
    p6 = load(os.path.join(R, f"{args.tag}_phase6_open_abstracts.jsonl"))
    p7 = load(os.path.join(R, f"{args.tag}_phase7_open_fulltext.jsonl"))
    questions = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    out_path = args.out or os.path.join(R, f"{args.tag}_phase89_search_shape.md")

    L, w = [], None
    w = L.append
    w("# Phases 8 & 9 — combined-topic search over graph relations")
    w("")
    w("Phases 6/7 searched **one topic at a time**, so a bare entity (`tinnitus`, `cancer`) "
      "could drift far off topic. Phases 8/9 search **relationships**: entities that are "
      "related in the knowledge graph are combined into a single conjunctive PubMed query "
      "(`cisplatin AND ACYP2 AND hearing loss`), so the hit is a paper about the *link*.")
    w("")
    w("The LLM sees the knowledge-graph edges and decides **how many terms** go in each query "
      "(the *arity*). A query returning nothing is **backed off** by dropping its last term "
      "and retried, down to 2 terms. Every issued query is recorded in `search_shape`.")
    w("")
    w("| Phase | Configuration | Retrieval |")
    w("|---|---|---|")
    w("| **Phase 8** | `AMG_KB_SOURCE=pharmgkb+pubmed_combo` | combined-topic queries — abstracts |")
    w("| **Phase 9** | `+ AMG_PUBMED_FULLTEXT=1` | combined-topic queries — full paper via PMC |")
    w("")

    # ---------- the search shape ------------------------------------------------
    for label, recs in (("Phase 8", p8), ("Phase 9", p9)):
        stats = [c for r in recs.values() for c in (r.get("search_shape") or [])]
        if not stats:
            continue
        w(f"## Search shape — {label}")
        w("")
        req = Counter(c["requested_arity"] for c in stats)
        used = Counter(c["used_arity"] for c in stats)
        w(f"**{len(stats)} queries issued** across {len(recs)} questions "
          f"({len(stats)/max(len(recs),1):.1f} per question).")
        w("")
        w("### How many terms were searched together")
        w("")
        w("| Terms per query | Requested by LLM | Actually searched | Hit rate | Papers found |")
        w("|---|---|---|---|---|")
        for k in sorted(set(list(req) + list(used))):
            grp = [c for c in stats if c["used_arity"] == k]
            hits = sum(c["hits"] for c in grp)
            hitrate = (100.0 * sum(1 for c in grp if c["hits"] > 0) / len(grp)) if grp else 0
            bar = "█" * int(round(20 * req.get(k, 0) / max(len(stats), 1)))
            w(f"| **{k}-term** | {req.get(k,0)} ({100*req.get(k,0)/len(stats):.0f}%) `{bar}` "
              f"| {used.get(k,0)} | {hitrate:.0f}% | {hits} |")
        w("")
        empty = sum(1 for c in stats if c["hits"] == 0)
        backed = [c for c in stats if c["backoffs"] > 0]
        w(f"- **Back-offs:** {len(backed)} of {len(stats)} queries were over-constrained and "
          f"had to drop terms ({sum(c['backoffs'] for c in stats)} terms dropped in total).")
        w(f"- **Empty after back-off:** {empty} queries ({100*empty/len(stats):.0f}%).")
        w(f"- **Mean arity:** requested {sum(c['requested_arity'] for c in stats)/len(stats):.2f}, "
          f"searched {sum(c['used_arity'] for c in stats)/len(stats):.2f}.")
        w("")
        by_stage = defaultdict(list)
        for c in stats:
            by_stage["entity" if c["stage"].startswith("entity:") else c["stage"]].append(c)
        w("| Stage | Queries | Mean terms | Hit rate |")
        w("|---|---|---|---|")
        for st, cs in sorted(by_stage.items()):
            w(f"| `{st}` | {len(cs)} | {sum(c['used_arity'] for c in cs)/len(cs):.2f} "
              f"| {100*sum(1 for c in cs if c['hits']>0)/len(cs):.0f}% |")
        w("")

    # ---------- precision comparison -------------------------------------------
    w("## Did combining topics improve precision?")
    w("")
    w("On-topic % = share of retrieved papers whose title+abstract mention **both** the "
      "question's drug **and** its adverse effect (same metric as `adr_phase_evaluation.md`).")
    w("")
    w("| Phase | Search shape | Papers | On-topic % |")
    w("|---|---|---|---|")
    for label, recs, shape in (("Phase 6", p6, "one topic per query"),
                               ("Phase 7", p7, "one topic per query"),
                               ("Phase 8", p8, "**combined** topics per query"),
                               ("Phase 9", p9, "**combined** topics per query")):
        if not recs:
            continue
        rate, tot = on_topic_rate(recs)
        w(f"| {label} | {shape} | {tot} | {'n/a' if rate is None else f'{rate:.0f}%'} |")
    w("")

    # ---------- per question ----------------------------------------------------
    w("---")
    w("")
    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        w(f"## Q{i}. {q['question']}")
        w("")
        for label, src in (("Phase 8 — combined topics, abstracts", p8),
                           ("Phase 9 — combined topics + full text", p9)):
            rec = src.get(qid)
            w(f"#### {label}")
            w("")
            if not rec:
                w("_Not produced._")
                w("")
                continue
            genes = ", ".join(str(g) for g in (rec.get("risk_genes") or [])) or "—"
            w(f"**Genes surfaced:** {genes}")
            w("")
            w((rec.get("generated_answer") or "").strip() or "_(no answer)_")
            w("")
            shp = rec.get("search_shape") or []
            if shp:
                w("**Queries issued (terms searched together):**")
                w("")
                w("| Terms | Query | Back-offs | Hits |")
                w("|---|---|---|---|")
                for c in shp:
                    w(f"| {c['used_arity']} | `{' AND '.join(c['terms'])}` | "
                      f"{c['backoffs']} | {c['hits']} |")
                w("")
            seen = set()
            papers = []
            for e in rec.get("evidence_log", []) or []:
                if e.get("source") == "PubMed" and e.get("ref") not in seen:
                    seen.add(e.get("ref"))
                    papers.append(e)
            if papers:
                w("<details><summary>Papers retrieved</summary>")
                w("")
                for e in papers:
                    meta = " · ".join(x for x in (e.get("journal",""), str(e.get("year",""))) if x)
                    w(f"- `{e.get('ref')}` — **{e.get('title','')}**" + (f" — *{meta}*" if meta else ""))
                    w(f"  - via `{e.get('via','-')}`")
                w("")
                w("</details>")
                w("")
        w("---")
        w("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {out_path} (phase8: {len(p8)}, phase9: {len(p9)})")


if __name__ == "__main__":
    main()
