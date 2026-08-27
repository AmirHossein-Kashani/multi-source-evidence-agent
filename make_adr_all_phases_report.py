"""ONE file with the results of every ADR phase we have.

Consolidates all phases that exist in results/ into a single markdown document:
phase catalogue (exact config), scores, combined-query search shape, and -- per question --
the answer produced by every phase side by side with its evidence counts.

    python make_adr_all_phases_report.py [--tag adrclin]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pgx_kb import PharmGKBSearcher, _norm

# (short, long label, filename, env configuration, has provenance)
PHASES = [
    ("A", "Baseline A — no external sources", "adrclin_offline.jsonl",
     "`AMG_USE_EXTERNAL=0`", False),
    ("B", "Baseline B — paper setup", "adrclin_pubmed.jsonl",
     "`AMG_USE_EXTERNAL=1` (PubMed + Wikipedia)", False),
    ("3-old", "Phase 3 (old run) — ClinPGx", "adrclin_pharmgkb.jsonl",
     "`AMG_KB_SOURCE=pharmgkb` (pre-provenance)", False),
    ("3", "Phase 3 — ClinPGx only", "adrclin_phase3_clinpgx.jsonl",
     "`AMG_KB_SOURCE=pharmgkb`", True),
    ("4", "Phase 4 — ClinPGx + cited PubMed", "adrclin_phase4_clinpgx_pubmed.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed`", True),
    ("5", "Phase 5 — + PMC full text", "adrclin_phase5_fulltext.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed` `AMG_PUBMED_FULLTEXT=1`", True),
    ("6", "Phase 6 — open LLM search", "adrclin_phase6_open_abstracts.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed_open`", True),
    ("7", "Phase 7 — open search + full text", "adrclin_phase7_open_fulltext.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed_open` `AMG_PUBMED_FULLTEXT=1`", True),
    ("8", "Phase 8 — combined-topic search", "adrclin_phase8_combo_abstracts.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed_combo`", True),
    ("9", "Phase 9 — combined + full text", "adrclin_phase9_combo_fulltext.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed_combo` `AMG_PUBMED_FULLTEXT=1`", True),
    ("10", "Phase 10 — free arity + own phrasing", "adrclin_phase10_free_fulltext.jsonl",
     "`AMG_KB_SOURCE=pharmgkb+pubmed_free` `AMG_PUBMED_FULLTEXT=1`", True),
    ("11", "Phase 11 — evidence ledger", "adrclin_phase11_ledger.jsonl",
     "`+ AMG_PAPER_DIGEST=1` `AMG_EVIDENCE_LEDGER=1`", True),
]

DRUG_TERMS = {"cisplatin": ["cisplatin", "platinol", "cddp", "platinum"],
              "doxorubicin": ["doxorubicin", "adriamycin", "anthracycline", "daunorubicin",
                              "epirubicin", "idarubicin"]}
ADR_TERMS = {"ototoxicity": ["ototox", "hearing", "deaf", "tinnitus", "cochlea", "audi", "auditory"],
             "neuropathy": ["neuropath", "neurotox"],
             "cardiotoxicity": ["cardiotox", "cardiac", "heart", "cardiomyopath", "ventricular"],
             "mucositis": ["mucositis", "stomatitis", "oral toxicity"]}
QKEY = {0: ("cisplatin", "ototoxicity"), 1: ("cisplatin", "ototoxicity"),
        2: ("cisplatin", "ototoxicity"), 3: ("cisplatin", "ototoxicity"),
        4: ("cisplatin", "neuropathy"), 5: ("doxorubicin", "cardiotoxicity"),
        6: ("doxorubicin", "cardiotoxicity"), 7: ("doxorubicin", "cardiotoxicity"),
        8: ("doxorubicin", "cardiotoxicity"), 9: ("doxorubicin", "mucositis")}
FALSE_PREMISE_QID = 7
DENIAL = [r"no (direct |established |known |documented )?(pharmacogenomic )?(link|association|evidence)",
          r"not (directly )?(associated|established|linked|supported)",
          r"lack(s|ing)? (of )?(direct )?(evidence|association)",
          r"no established", r"not been established", r"insufficient evidence"]


def load(path):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out[r.get("id")] = r
    return out


def gene_symbol(g):
    m = re.match(r"([A-Za-z0-9\-]+)", str(g or "").strip())
    return re.sub(r"\*.*$", "", m.group(1)).upper() if m else ""


def genes(rec):
    return sorted({g for g in (gene_symbol(x) for x in (rec.get("risk_genes") or []))
                   if len(g) >= 3 and not g.isdigit()})


def papers(rec):
    seen, out = set(), []
    for e in rec.get("evidence_log", []) or []:
        if e.get("source") == "PubMed" and e.get("ref") not in seen:
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

    pgx = PharmGKBSearcher()
    data = [(sh, lab, load(os.path.join(args.results_dir, fn)), cfg, prov)
            for sh, lab, fn, cfg, prov in PHASES]
    data = [d for d in data if d[2]]
    questions = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    out_path = args.out or os.path.join(args.results_dir, f"{args.tag}_ALL_phases_results.md")

    L, w = [], None
    w = L.append
    w("# AMG-RAG — results of all phases (ADR clinical set)")
    w("")
    w(f"Every phase currently on disk, over the same {len(questions)} questions, same model "
      "(`qwen2.5:14b`), same code — the phases differ **only by environment variables**.")
    w("")

    # ---- catalogue -----------------------------------------------------------
    w("## Phase catalogue")
    w("")
    w("| Phase | Configuration | Retrieval behaviour | n |")
    w("|---|---|---|---|")
    behaviour = {
        "A": "no external evidence; LLM knowledge only",
        "B": "the paper's setup: live PubMed + Wikipedia",
        "3-old": "offline ClinPGx tables (before provenance logging)",
        "3": "offline ClinPGx tables",
        "4": "ClinPGx, then the exact PMIDs ClinPGx cites for those pairs",
        "5": "as phase 4, abstracts upgraded to PMC full text",
        "6": "LLM picks search topics freely from question + graph; one topic per query",
        "7": "as phase 6, plus PMC full text",
        "8": "graph-related terms combined into ONE conjunctive query; LLM picks the arity",
        "9": "as phase 8, plus PMC full text",
        "10": "model chooses the arity (1, 2, 3, …) AND writes the PubMed query string itself",
        "11": "as phase 10, plus a per-gene ledger: confidence by rule + source contradictions",
    }
    for sh, lab, recs, cfg, prov in data:
        w(f"| **{lab}** | {cfg} | {behaviour.get(sh,'')} | {len(recs)} |")
    w("")

    # ---- scores --------------------------------------------------------------
    w("## Scores")
    w("")
    w("No gold answers exist for these questions (`reference` is empty), so BERTScore does not "
      "apply. These metrics are computable without one:")
    w("")
    w("- **On-topic %** — retrieved papers mentioning *both* the question's drug *and* its adverse effect")
    w("- **Grounded %** — genes named in the answer that appear in evidence actually retrieved")
    w("- **ClinPGx-valid %** — genes named that ClinPGx really links to that drug")
    w("- **False premise** — Q8 asserts a CYP2D6–doxorubicin link that does not exist; is it caught?")
    w("")
    w("| Phase | Refs/q | PubMed/q | Full text | On-topic % | Grounded % | ClinPGx-valid % | False premise |")
    w("|---|---|---|---|---|---|---|---|")
    for sh, lab, recs, cfg, prov in data:
        n = len(recs)
        refs = sum(len(r.get("references", []) or []) for r in recs.values())
        pubs = sum(1 for r in recs.values() for x in (r.get("references") or [])
                   if x.get("source") == "PubMed")
        fts = sum(1 for r in recs.values() for x in (r.get("references") or [])
                  if "/PMC" in (x.get("ref") or ""))
        hit = tot = 0
        gnamed = gground = gvalid = 0
        for qid, rec in recs.items():
            d, a = QKEY.get(qid, ("", ""))
            dt, at = DRUG_TERMS.get(d, []), ADR_TERMS.get(a, [])
            for e in papers(rec):
                hay = f"{e.get('title','')} {e.get('snippet','')}".lower()
                tot += 1
                if any(t in hay for t in dt) and any(t in hay for t in at):
                    hit += 1
            blob = " ".join((e.get("snippet") or "") + " " + (e.get("title") or "")
                            for e in (rec.get("evidence_log") or [])).upper()
            for g in genes(rec):
                gnamed += 1
                if prov and g in blob:
                    gground += 1
                if any(row["gene"].upper() == g
                       for dd in DRUG_TERMS.get(d, []) for row in pgx.by_drug.get(_norm(dd), [])):
                    gvalid += 1
        fp = recs.get(FALSE_PREMISE_QID)
        fpv = ("✅" if any(re.search(p, (fp.get("generated_answer") or "").lower()) for p in DENIAL)
               else "❌") if fp else "n/a"
        w(f"| {lab} | {refs/n:.1f} | {pubs/n:.1f} | {fts} "
          f"| {f'{100*hit/tot:.0f}%' if tot else 'n/a'} "
          f"| {f'{100*gground/gnamed:.0f}%' if (prov and gnamed) else 'n/a'} "
          f"| {f'{100*gvalid/gnamed:.0f}%' if gnamed else 'n/a'} | {fpv} |")
    w("")

    # ---- search shape (8/9) ---------------------------------------------------
    shp_rows = [(lab, [c for r in recs.values() for c in (r.get("search_shape") or [])])
                for sh, lab, recs, cfg, prov in data]
    shp_rows = [(l, s) for l, s in shp_rows if s]
    if shp_rows:
        w("## Search shape — how many items were searched together (phases 8/9/10)")
        w("")
        w("| Phase | Queries | 1-term | 2-term | 3-term | 4+-term | Mean arity | Back-offs | Empty |")
        w("|---|---|---|---|---|---|---|---|---|")
        for lab, st in shp_rows:
            req = Counter(c["requested_arity"] for c in st)
            n4 = sum(v for k, v in req.items() if k >= 4)
            w(f"| {lab} | {len(st)} | "
              + " | ".join(f"{req.get(k,0)} ({100*req.get(k,0)/len(st):.0f}%)" for k in (1, 2, 3))
              + f" | {n4} ({100*n4/len(st):.0f}%)"
              + f" | {sum(c['requested_arity'] for c in st)/len(st):.2f} "
                f"| {sum(1 for c in st if c['backoffs'] > 0)} "
                f"| {sum(1 for c in st if c['hits'] == 0)} |")
        w("")

    # ---- genes matrix ---------------------------------------------------------
    w("## Genes surfaced, by phase")
    w("")
    w("| Q | " + " | ".join(sh for sh, *_ in data) + " |")
    w("|---" * (len(data) + 1) + "|")
    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        cells = [", ".join(genes(recs[qid])) if qid in recs else "—" for _, _, recs, _, _ in data]
        w(f"| Q{i} | " + " | ".join(c or "—" for c in cells) + " |")
    w("")
    w("---")
    w("")

    # ---- per question ---------------------------------------------------------
    for i, q in enumerate(questions, start=1):
        qid = q.get("id")
        w(f"## Q{i}. {q['question']}")
        w("")
        for sh, lab, recs, cfg, prov in data:
            rec = recs.get(qid)
            if not rec:
                continue
            pp = papers(rec)
            nft = sum(1 for e in pp if "/PMC" in (e.get("ref") or ""))
            w(f"### {lab}")
            w("")
            w(f"**Genes:** {', '.join(genes(rec)) or '—'}  ·  "
              f"**Evidence:** {len(rec.get('references', []) or [])} refs, {len(pp)} papers"
              + (f", {nft} full text" if nft else ""))
            w("")
            w((rec.get("generated_answer") or "").strip() or "_(no answer)_")
            w("")
            shp = rec.get("search_shape") or []
            if shp:
                w("<details><summary>Queries issued (combined terms)</summary>")
                w("")
                for c in shp:
                    w(f"- `{' AND '.join(c['terms'])}` — {c['used_arity']} terms, "
                      f"{c['backoffs']} back-off(s), {c['hits']} hit(s)")
                w("")
                w("</details>")
                w("")
            if pp:
                w("<details><summary>Papers retrieved</summary>")
                w("")
                for e in pp:
                    meta = " · ".join(x for x in (e.get("journal",""), str(e.get("year",""))) if x)
                    w(f"- `{e.get('ref')}` — **{e.get('title','')}**" + (f" — *{meta}*" if meta else ""))
                    w(f"  - via `{e.get('via','-')}`")
                w("")
                w("</details>")
                w("")
        w("---")
        w("")

    w("## Caveats")
    w("")
    w("- **n = 10, no gold answers.** Descriptive measurements, not significance tests.")
    w("- **ClinPGx-valid % is partly circular** for phases 3–9: they retrieve from ClinPGx and "
      "are then scored against it. Fair for baselines A/B and fair *between* grounded phases.")
    w("- **Baselines A/B and phase 3-old predate provenance logging** (no grounding column) and "
      "cover 9 questions rather than 10.")
    w("- **On-topic % is a keyword proxy** — a relevant paper that never repeats the drug name "
      "in its abstract scores as off-topic, so treat it as a lower bound.")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"wrote {out_path}  ({len(data)} phases, {len(questions)} questions)")


if __name__ == "__main__":
    main()
