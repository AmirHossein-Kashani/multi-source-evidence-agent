"""Side-by-side outputs of the best configurations for the 10 ADR questions.

Renders, per question: each best phase's answer, and for the ledger phases the full per-gene
table (confidence, label, contradiction flags, supporting/refuting refs) plus the paragraphs the
system actually read.

    python make_best_phases_report.py
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

PHASES = [
    ("Phase 4 — ClinPGx + its cited literature", "adrclin_phase4_clinpgx_pubmed.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed`"),
    ("Phase 9L — widest net + ledger", "adrclin_phase9L_ledger.jsonl",
     "`pharmgkb+pubmed_combo` + digest + ledger"),
    ("Phase 11 — most precise + ledger", "adrclin_phase11_ledger.jsonl",
     "`pharmgkb+pubmed_free` + digest + ledger"),
    ("Phase 12 — as phase 11, with expanded open-access full text",
     "adrclin_phase12_oa_ledger.jsonl",
     "`pharmgkb+pubmed_free` + digest + ledger + PMC/EuropePMC/Unpaywall"),
    ("Phase 13 — contradiction resolution", "adrclin_phase13_resolution.jsonl",
     "`pharmgkb+pubmed_combo` + digest + ledger + resolution layer"),
]


def load(path):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out[r.get("id")] = r
    return out


def ledger_table(w, led, limit=14):
    if not led:
        return
    w("| Gene | Conf | Label | Disputed | Supporting | Refuting |")
    w("|---|---|---|---|---|---|")
    for e in led[:limit]:
        sup = "<br>".join(f"`{s['ref']}` ({s['study_type']})" for s in e["supporting"][:2]) or "—"
        ref = "<br>".join(f"`{s['ref']}` ({s['study_type']})" for s in e["refuting"][:2]) or "—"
        flags = ", ".join(f["type"] for f in e.get("contradictions", [])) or "—"
        var = f" ({e['variants'][0]})" if e.get("variants") else ""
        w(f"| **{e['gene']}**{var} | {e['confidence']:.2f} | {e['label']} | {flags} | {sup} | {ref} |")
    if len(led) > limit:
        w(f"| _… {len(led)-limit} more pairs_ | | | | | |")
    w("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default=os.path.join(HERE, "results"))
    ap.add_argument("--input", default=os.path.join(HERE, "dataset", "PharmGKB", "adr_clinical.jsonl"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--only", default="",
                    help="render a single configuration, e.g. --only 'Phase 12'")
    args = ap.parse_args()

    phases = [p for p in PHASES if not args.only or p[0].startswith(args.only)]
    if args.only and not phases:
        raise SystemExit(f"no configuration matches --only {args.only!r}")
    data = [(lab, load(os.path.join(args.results_dir, fn)), cfg) for lab, fn, cfg in phases]
    data = [d for d in data if d[1]]
    questions = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    out_path = args.out or os.path.join(args.results_dir, "best_phases_10_questions.md")

    L, w = [], None
    w = L.append
    if args.only:
        lab, recs, cfg = data[0]
        npairs = sum(len(r.get("gene_ledger", []) or []) for r in recs.values())
        ndisp = sum(1 for r in recs.values() for e in (r.get("gene_ledger") or []) if e["disputed"])
        nft = sum(1 for r in recs.values() for d in (r.get("paper_digests") or [])
                  if d.get("source") != "abstract")
        ndig = sum(len(r.get("paper_digests") or []) for r in recs.values())
        w(f"# {lab} — outputs for the 10 ADR questions")
        w("")
        w(f"Configuration: {cfg}")
        w("")
        w(f"**{npairs} gene–drug pairs** across {len(recs)} questions "
          f"({npairs/max(len(recs),1):.1f} per question), **{ndisp}** carrying a contradiction "
          f"flag. {ndig} papers read, {nft} of them as full text.")
        w("")
    else:
        w("# Best configurations — outputs for the 10 ADR questions")
        w("")
        w("Five configurations, same questions, same model. Phase 4 is the conservative curated "
          "baseline; phases 9L, 11 and 12 add per-paper reading and the evidence ledger, which "
          "reports **every** candidate gene with a rule-computed confidence and explicit "
          "contradictions; phase 13 additionally resolves each pair to a status and explains "
          "**why** the sources disagree.")
        w("")
        w("| Configuration | Setup | Genes/question | On-topic | Catches false premise |")
        w("|---|---|---|---|---|")
        w("| Phase 4 | `pharmgkb+pubmed` | 2–3 | 22% | ✅ |")
        w("| Phase 9L | `pharmgkb+pubmed_combo` + digest + ledger | 11.6 | 52% | ❌ |")
        w("| Phase 11 | `pharmgkb+pubmed_free` + digest + ledger | 9.6 | 65% | ✅ |")
        w("| Phase 12 | as phase 11 + Europe PMC / Unpaywall full text | 9.1 | 63% | ✅ |")
        w("| Phase 13 | wide retrieval + digest + ledger + resolution | 14.5 | 49% | ❌ |")
        w("")
    w("Confidence is computed by formula in `evidence_ledger.py` — the model never emits it. "
      "`disputed` means at least one contradiction flag fired.")
    w("")
    w("---")
    w("")

    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        w(f"## Q{i}. {q['question']}")
        w("")
        for lab, recs, cfg in data:
            rec = recs.get(qid)
            if not rec:
                continue
            led = rec.get("gene_ledger") or []
            if not args.only:
                w(f"### {lab}")
                w("")
            if led:
                disputed = sum(1 for e in led if e["disputed"])
                w(f"*{len(led)} gene–drug pairs, {disputed} disputed*")
            else:
                genes = ", ".join(str(g) for g in (rec.get("risk_genes") or [])) or "—"
                w(f"*Genes named: {genes}*")
            w("")
            w((rec.get("generated_answer") or "").strip() or "_(no answer)_")
            w("")
            cards = [c for c in (rec.get("contradiction_cards") or [])
                     if c["status"] != "INSUFFICIENT"]
            if cards:
                w("**Resolved pairs** (INSUFFICIENT ones omitted)")
                w("")
                w("| Gene | Status | Conf | Why | Supporting | Refuting |")
                w("|---|---|---|---|---|---|")
                for c in cards[:10]:
                    why = "; ".join(r["detail"] for r in c.get("reasons", [])) or "—"
                    note = "; ".join(c.get("notes", []))
                    if note:
                        why += f" — *{note[:90]}*"
                    sup = "<br>".join(f"`{x['ref']}` ({x['study_type']})"
                                      for x in c["supporting"][:2]) or "—"
                    ref = "<br>".join(f"`{x['ref']}` ({x['study_type']})"
                                      for x in c["refuting"][:2]) or "—"
                    w(f"| **{c['gene']}** | {c['status']} | {c['confidence']:.2f} | {why} "
                      f"| {sup} | {ref} |")
                w("")
                for c in cards[:3]:
                    w(f"> {c['conclusion']}")
                    w("")
            if led:
                ledger_table(w, led)
                digests = rec.get("paper_digests") or []
                cited = [(d, p) for d in digests for p in d.get("paragraphs", [])]
                if cited:
                    w("<details><summary>Paragraphs the system read and kept "
                      f"({len(cited)} from {len(digests)} papers)</summary>")
                    w("")
                    for d, p in cited[:6]:
                        sec = p.get("section") or "?"
                        w(f"- `{p['ref']}` — *{d.get('title','')[:80]}* — section **{sec}**")
                        w(f"  - {p['text'][:230]}…")
                    w("")
                    w("</details>")
                    w("")
        w("---")
        w("")

    w("## How to read the confidence")
    w("")
    w("```")
    w("base    = ClinPGx evidence level (1A .98 … 4 .40) | absent .25 | 'not associated' .15")
    w("support = sum of study-type weights over DISTINCT sources (meta 1.0, GWAS .9, animal .3)")
    w("conf    = base·(1 + 0.18·log1p(support)) − 0.30·log1p(refute),  ×0.9 if curators disagree")
    w("```")
    w("")
    w("Labels: high ≥0.75 · moderate ≥0.50 · low ≥0.25 · very_low below. On 72 labelled ClinPGx "
      "pairs the score separated positives from negatives by **+0.351** (Spearman 0.721), and "
      "every negative landed in `very_low`.")
    w("")
    w("**Contradiction flags**")
    w("")
    w("| Flag | Meaning |")
    w("|---|---|")
    w("| `curator_ambiguous` | ClinPGx curators recorded conflicting evidence for the pair |")
    w("| `curated_vs_literature` | the curated tables and the retrieved papers disagree |")
    w("| `literature_internal` | retrieved papers disagree with each other |")
    w("| `uncurated_literature_claim` | not in ClinPGx but backed by human studies — candidate novel finding |")
    w("| `unsupported_claim` | no curated row and no strong supporting study |")
    w("")
    w("**Known limitation:** the prose answers rarely cite their references (0–1 of 10) even "
      "though the ledger carries paragraph-level refs. Read the ledger table, not the prose.")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {out_path} ({len(data)} configurations, {len(questions)} questions)")


if __name__ == "__main__":
    main()
