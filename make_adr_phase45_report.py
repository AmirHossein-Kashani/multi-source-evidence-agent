"""Build the complete QA markdown report for the ADR clinical question set.

Reads the phase-4 and phase-5 result JSONLs produced by run_adr_phase45_alliance.bash and
renders, per question: the generated answer, the genes it surfaced, the ClinPGx evidence
retrieved, the PubMed citations checked (phase 4), and the full-text upgrades (phase 5).

    python make_adr_phase45_report.py [--tag adrclin] [--out results/adr_phase45_QA.md]
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    """id -> record (last row wins, matching eval_genmedgpt.py's dedup rule)."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                out[rec.get("id")] = rec
    return out


def refs_of(rec, source=None):
    refs = rec.get("references", []) or []
    return [r for r in refs if source is None or r.get("source") == source]


def evidence_texts(rec, source):
    """Deduplicated snippets from the evidence log for one source, reasoning stage first."""
    seen, out = set(), []
    for e in sorted(rec.get("evidence_log", []) or [],
                    key=lambda e: 0 if e.get("stage") == "reasoning" else 1):
        if e.get("source") != source:
            continue
        snip = (e.get("snippet") or "").strip()
        key = e.get("ref")
        if not snip or key in seen:
            continue
        seen.add(key)
        out.append((key, snip, e))
    return out


def fmt_answer(rec):
    ans = (rec.get("generated_answer") or "").strip()
    return ans if ans else "_(no answer produced)_"


def gene_line(rec):
    genes = rec.get("risk_genes") or []
    genes = [str(g) for g in genes if str(g).strip()]
    return ", ".join(genes) if genes else "—"


def render_phase(w, rec, phase_name, show_fulltext):
    w(f"#### {phase_name}")
    w("")
    if rec is None:
        w("_Not produced — the item failed in this phase (failed items are never written "
          "to the results file, by design, so a re-run retries them)._")
        w("")
        return
    w(f"**Genes surfaced:** {gene_line(rec)}")
    w("")
    w(fmt_answer(rec))
    w("")

    pgx = evidence_texts(rec, "ClinPGx")
    if pgx:
        w("<details><summary>ClinPGx evidence retrieved</summary>")
        w("")
        for ref, snip, _ in pgx:
            w(f"- `{ref}` — {snip}")
        w("")
        w("</details>")
        w("")

    pubs = evidence_texts(rec, "PubMed")
    if pubs:
        label = "PubMed citations checked" + (" (with full-text upgrades)" if show_fulltext else "")
        w(f"<details><summary>{label}</summary>")
        w("")
        for ref, snip, e in pubs:
            via = e.get("via", "esearch")
            title = e.get("title", "")
            meta = " · ".join(x for x in (e.get("journal", ""), str(e.get("year", ""))) if x)
            head = f"- `{ref}` ({via})"
            if title:
                head += f" — **{title}**"
            if meta:
                head += f" — *{meta}*"
            w(head)
            w(f"  - {snip[:280]}…")
        w("")
        w("</details>")
        w("")

    stats = rec.get("graph_stats", {})
    n_ref = len(refs_of(rec))
    n_pub = len(refs_of(rec, "PubMed"))
    w(f"<sub>KG: {stats.get('num_entities', '?')} entities / {stats.get('num_relations', '?')} "
      f"relations · {n_ref} references ({n_pub} PubMed) · "
      f"{len(rec.get('evidence_log', []) or [])} retrieval events</sub>")
    w("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="adrclin")
    ap.add_argument("--results-dir", default=os.path.join(HERE, "results"))
    ap.add_argument("--input", default=os.path.join(HERE, "dataset", "PharmGKB", "adr_clinical.jsonl"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    p3 = load(os.path.join(args.results_dir, f"{args.tag}_phase3_clinpgx.jsonl"))
    p4 = load(os.path.join(args.results_dir, f"{args.tag}_phase4_clinpgx_pubmed.jsonl"))
    p5 = load(os.path.join(args.results_dir, f"{args.tag}_phase5_fulltext.jsonl"))
    questions = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    out_path = args.out or os.path.join(args.results_dir, f"{args.tag}_phase45_QA.md")

    lines = []
    w = lines.append
    w("# ADR clinical QA — Phase 3 / 4 / 5 comparison")
    w("")
    w(f"Complete run over all {len(questions)} ADR questions. The three phases differ **only by "
      f"environment variables** — same code, same entry point, same model (`qwen2.5:14b`), same "
      f"input file — so the retrieval configuration is the only independent variable.")
    w("")
    w("| Phase | Configuration (env vars only) | What it retrieves |")
    w("|---|---|---|")
    w("| **Phase 3** | `AMG_KB_SOURCE=pharmgkb` | Local ClinPGx tables only "
      "(`clinicalVariants.tsv` + `relationships.tsv`). No network. |")
    w("| **Phase 4** | `AMG_KB_SOURCE=pharmgkb+pubmed` | ClinPGx tables, then PubMed — the exact "
      "PMIDs `relationships.tsv` cites for the retrieved gene–drug pairs (`via: clinpgx_citation`), "
      "topped up by a live search. Abstracts only. |")
    w("| **Phase 5** | `+ AMG_PUBMED_FULLTEXT=1` | Same, plus PubMed abstracts used at the reasoning "
      "stage upgraded to PMC full text (JATS XML; OA PDF fallback), capped at "
      "`AMG_FULLTEXT_MAX_CHARS`. |")
    w("")
    w("Every retrieved item is referenced with a stable id (`ClinPGx:GENE/variant:Llevel`, "
      "`PMID:xxx`, `PMID:xxx/PMCxxx`) and persisted per question in the `references` / "
      "`evidence_log` fields of the results JSONL.")
    w("")

    # Coverage + retrieval statistics
    w("## Coverage and retrieval statistics")
    w("")
    w("| # | Question | P3 | P4 | P5 | Refs (P5) | PubMed | Full text | KG entities |")
    w("|---|---|---|---|---|---|---|---|---|")
    tot_refs = tot_pub = tot_ft = 0
    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        r5 = p5.get(qid)
        refs = refs_of(r5) if r5 else []
        pub = [x for x in refs if x.get("source") == "PubMed"]
        ft = [x for x in pub if "/PMC" in (x.get("ref") or "")]
        tot_refs += len(refs); tot_pub += len(pub); tot_ft += len(ft)
        ents = (r5 or {}).get("graph_stats", {}).get("num_entities", "-")
        w(f"| Q{i} | {q['question'][:60]}... | {'YES' if qid in p3 else 'NO'} "
          f"| {'YES' if qid in p4 else 'NO'} | {'YES' if qid in p5 else 'NO'} "
          f"| {len(refs)} | {len(pub)} | {len(ft)} | {ents} |")
    w(f"| | **Total (phase 5)** | | | | **{tot_refs}** | **{tot_pub}** | **{tot_ft}** | |")
    w("")

    vias = {}
    for rec in list(p3.values()) + list(p4.values()) + list(p5.values()):
        for e in rec.get("evidence_log", []) or []:
            if e.get("source") == "PubMed":
                vias[e.get("via", "esearch")] = vias.get(e.get("via", "esearch"), 0) + 1
    if vias:
        w("**How PubMed evidence was reached** (retrieval events, both phases):")
        w("")
        w("| Route | Events | Meaning |")
        w("|---|---|---|")
        meaning = {
            "clinpgx_citation": "the PMID ClinPGx itself cites for the gene-drug pair (phase-4 verification)",
            "esearch": "live PubMed search on the query text (top-up when citations run short)",
            "clinpgx_citation+pmc_xml": "ClinPGx-cited PMID upgraded to PMC full text (phase 5)",
            "esearch+pmc_xml": "search hit upgraded to PMC full text (phase 5)",
        }
        for k, v in sorted(vias.items(), key=lambda kv: -kv[1]):
            w(f"| `{k}` | {v} | {meaning.get(k, '-')} |")
        w("")

    w("### Limitations of this run")
    w("")
    w(f"- **Full text is scarce.** Phase 5 attempts a full-text upgrade for the top 2 PubMed "
      f"items per question at the reasoning stage (at most 20 attempts here); only **{tot_ft}** "
      f"succeeded. Most pharmacogenomics papers ClinPGx cites are older and not open-access in "
      f"PMC, so retrieval falls back to abstracts rather than inventing content.")
    w("- **The live-search top-up is noisy.** When ClinPGx cites fewer PMIDs than the result "
      "cap, the remainder comes from an esearch on the raw question text; for long patient-style "
      "questions this sometimes returns off-topic recent papers. The ClinPGx-cited PMIDs "
      "(`via: clinpgx_citation`) are the reliable part of the phase-4 evidence.")
    w("- **Entity-level retrieval pulls unrelated drugs.** Each extracted entity is searched "
      "separately, which surfaces ClinPGx rows for other drugs (e.g. capecitabine/DPYD rows "
      "inside a cisplatin question). They are logged, so their influence stays auditable.")
    w("")
    w("---")
    w("")

    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        w(f"## Q{i}. {q['question']}")
        w("")
        render_phase(w, p3.get(qid), "Phase 3 — ClinPGx only (offline)", show_fulltext=False)
        render_phase(w, p4.get(qid), "Phase 4 — ClinPGx + PubMed check", show_fulltext=False)
        render_phase(w, p5.get(qid), "Phase 5 — + PMC full text", show_fulltext=True)
        r3, r4, r5 = p3.get(qid), p4.get(qid), p5.get(qid)
        if any((r3, r4, r5)):
            w("**Genes surfaced by phase**")
            w("")
            w("| Phase 3 | Phase 4 | Phase 5 |")
            w("|---|---|---|")
            w(f"| {gene_line(r3) if r3 else '—'} | {gene_line(r4) if r4 else '—'} "
              f"| {gene_line(r5) if r5 else '—'} |")
            w("")
        w("---")
        w("")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out_path}  (phase3: {len(p3)}, phase4: {len(p4)}, phase5: {len(p5)} items)")


if __name__ == "__main__":
    main()
