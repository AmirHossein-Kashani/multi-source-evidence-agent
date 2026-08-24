"""Report for the OPEN-search phases (6/7): what the LLM chose to search and what it found.

Phases 4/5 could only read the papers ClinPGx already cites. Phases 6/7 let an LLM -- aware of
the question and of the evidence/graph retrieved so far -- choose the search topics freely.
This report shows, per question: the answer, the topics the model picked, the papers found
(flagging which ones ClinPGx never cited), and any full-text upgrades.

    python make_adr_phase67_report.py [--tag adrclin]
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    out[r.get("id")] = r
    return out


def topics_of(rec):
    """Distinct search topics the LLM picked, in first-seen order (from via: llm_topic:...)."""
    seen = []
    for e in rec.get("evidence_log", []) or []:
        via = e.get("via") or ""
        m = re.match(r"llm_topic:(.+?)(?:\+|$)", via)
        if m and e.get("stage") != "entity" and not (e.get("stage") or "").startswith("entity:"):
            t = m.group(1).strip()
            if t and t not in seen:
                seen.append(t)
    return seen


def pubmed_items(rec):
    seen, out = set(), []
    for e in sorted(rec.get("evidence_log", []) or [],
                    key=lambda e: 0 if e.get("stage") == "reasoning" else 1):
        if e.get("source") != "PubMed" or e.get("ref") in seen:
            continue
        seen.add(e.get("ref"))
        out.append(e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="adrclin")
    ap.add_argument("--results-dir", default=os.path.join(HERE, "results"))
    ap.add_argument("--input", default=os.path.join(HERE, "dataset", "PharmGKB", "adr_clinical.jsonl"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    p6 = load(os.path.join(args.results_dir, f"{args.tag}_phase6_open_abstracts.jsonl"))
    p7 = load(os.path.join(args.results_dir, f"{args.tag}_phase7_open_fulltext.jsonl"))
    # phases 4/5 only to identify which papers are NEW (never cited by ClinPGx)
    prev = {}
    for name in (f"{args.tag}_phase4_clinpgx_pubmed.jsonl", f"{args.tag}_phase5_fulltext.jsonl"):
        for qid, rec in load(os.path.join(args.results_dir, name)).items():
            prev.setdefault(qid, set()).update(
                (e.get("ref") or "").split("/")[0] for e in rec.get("evidence_log", []) or []
                if e.get("source") == "PubMed")
    questions = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    out_path = args.out or os.path.join(args.results_dir, f"{args.tag}_phase67_open_search.md")

    L = []
    w = L.append
    w("# ADR clinical QA — Phase 6 & 7 (open, LLM-directed literature search)")
    w("")
    w("Phases 4/5 could only read the papers ClinPGx already cites for a gene–drug pair. "
      "**Phases 6/7 remove that restriction**: an LLM that has seen the question *and* the "
      "evidence and knowledge-graph content retrieved so far chooses the search topics, and "
      "each topic is searched separately on PubMed.")
    w("")
    w("| Phase | Configuration | Literature access |")
    w("|---|---|---|")
    w("| **Phase 6** | `AMG_KB_SOURCE=pharmgkb+pubmed_open` | Free topic search — abstracts |")
    w("| **Phase 7** | `+ AMG_PUBMED_FULLTEXT=1` | Free topic search — full paper via PMC |")
    w("")
    w("ClinPGx grounding stays on in both, so these are *phase 3 + unrestricted literature*. "
      "Papers marked **NEW** were never cited by ClinPGx for these pairs, i.e. they are "
      "reachable only because the search was opened up.")
    w("")

    w("## Summary")
    w("")
    w("| # | Topics chosen (phase 7) | Papers | NEW vs phases 4/5 | Full text |")
    w("|---|---|---|---|---|")
    tot_new = tot_pap = tot_ft = 0
    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        r = p7.get(qid) or p6.get(qid)
        if not r:
            w(f"| Q{i} | _not produced_ | - | - | - |")
            continue
        pubs = pubmed_items(r)
        new = [e for e in pubs if (e.get("ref") or "").split("/")[0] not in prev.get(qid, set())]
        ft = [e for e in pubs if "/PMC" in (e.get("ref") or "")]
        tot_pap += len(pubs); tot_new += len(new); tot_ft += len(ft)
        w(f"| Q{i} | {'; '.join(topics_of(r)) or '—'} | {len(pubs)} | **{len(new)}** | {len(ft)} |")
    w(f"| | **Total** | **{tot_pap}** | **{tot_new}** | **{tot_ft}** |")
    w("")
    w("---")
    w("")

    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        w(f"## Q{i}. {q['question']}")
        w("")
        for label, src in (("Phase 6 — open search, abstracts", p6),
                           ("Phase 7 — open search + full text", p7)):
            rec = src.get(qid)
            w(f"#### {label}")
            w("")
            if not rec:
                w("_Not produced (item failed in this phase)._")
                w("")
                continue
            genes = ", ".join(str(g) for g in (rec.get("risk_genes") or [])) or "—"
            w(f"**Genes surfaced:** {genes}")
            w("")
            w((rec.get("generated_answer") or "").strip() or "_(no answer)_")
            w("")
            tps = topics_of(rec)
            if tps:
                w("**Search topics the model chose:** " + "; ".join(f"`{t}`" for t in tps))
                w("")
            pubs = pubmed_items(rec)
            if pubs:
                w("<details><summary>Papers retrieved</summary>")
                w("")
                for e in pubs:
                    ref = e.get("ref") or ""
                    is_new = ref.split("/")[0] not in prev.get(qid, set())
                    tag = " **[NEW]**" if is_new else ""
                    meta = " · ".join(x for x in (e.get("journal", ""), str(e.get("year", ""))) if x)
                    w(f"- `{ref}`{tag} — **{e.get('title', '')}**" + (f" — *{meta}*" if meta else ""))
                    w(f"  - via `{e.get('via', '-')}`")
                w("")
                w("</details>")
                w("")
            st = rec.get("graph_stats", {})
            w(f"<sub>KG: {st.get('num_entities', '?')} entities / {st.get('num_relations', '?')} "
              f"relations · {len(rec.get('references', []) or [])} references</sub>")
            w("")
        w("---")
        w("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {out_path}  (phase6: {len(p6)}, phase7: {len(p7)} items)")


if __name__ == "__main__":
    main()
