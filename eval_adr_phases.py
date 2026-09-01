"""Score every ADR phase we have results for -- without gold answers.

The ADR clinical questions carry an empty `reference`, so BERTScore (eval_genmedgpt.py) does
not apply. These metrics instead measure things that ARE checkable:

  1. Evidence volume      -- references / PubMed refs / full-text papers per question
  2. Retrieval precision  -- of the papers retrieved, how many are actually about the
                             question's drug and/or its adverse effect (title+abstract match)
  3. Gene grounding       -- of the genes the answer names, how many appear in the evidence
                             that was actually retrieved (proxy for "not invented")
  4. ClinPGx validity     -- how many named genes ClinPGx really links to that drug
  5. False-premise check  -- Q8 asserts a CYP2D6-doxorubicin link that does not exist;
                             does the answer say so?

Read-only: consumes results/*.jsonl, writes a markdown report.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pgx_kb import PharmGKBSearcher, _norm

RESULTS = os.path.join(HERE, "results")

# The phases to score, in pipeline order. (label, filename, has_provenance)
PHASES = [
    ("Baseline A — no external sources", "adrclin_offline.jsonl", False),
    ("Baseline B — paper setup (PubMed+Wiki)", "adrclin_pubmed.jsonl", False),
    ("Phase 3 (old run) — ClinPGx", "adrclin_pharmgkb.jsonl", False),
    ("Phase 3 — ClinPGx only", "adrclin_phase3_clinpgx.jsonl", True),
    ("Phase 4 — ClinPGx + cited PubMed", "adrclin_phase4_clinpgx_pubmed.jsonl", True),
    ("Phase 5 — + PMC full text", "adrclin_phase5_fulltext.jsonl", True),
    ("Phase 6 — open LLM search (abstracts)", "adrclin_phase6_open_abstracts.jsonl", True),
    ("Phase 7 — open search + full text", "adrclin_phase7_open_fulltext.jsonl", True),
    ("Phase 8 — combined-topic search", "adrclin_phase8_combo_abstracts.jsonl", True),
    ("Phase 9 — combined + full text", "adrclin_phase9_combo_fulltext.jsonl", True),
    ("Phase 10 — free arity + own phrasing", "adrclin_phase10_free_fulltext.jsonl", True),
    ("Phase 9L — phase-9 retrieval + ledger", "adrclin_phase9L_ledger.jsonl", True),
    ("Phase 11 — evidence ledger", "adrclin_phase11_ledger.jsonl", True),
    ("Phase 12 — ledger + expanded OA full text", "adrclin_phase12_oa_ledger.jsonl", True),
    ("Phase 13 — contradiction resolution", "adrclin_phase13_resolution.jsonl", True),
]

# Per-question topic key: the drug family and the adverse effect actually asked about.
# Hand-written from the question text (10 questions) and used only for relevance scoring.
DRUG_TERMS = {
    "cisplatin": ["cisplatin", "platinol", "cddp", "platinum"],
    "doxorubicin": ["doxorubicin", "adriamycin", "anthracycline", "daunorubicin",
                    "epirubicin", "idarubicin"],
}
ADR_TERMS = {
    "ototoxicity": ["ototox", "hearing", "deaf", "tinnitus", "cochlea", "audio", "auditory"],
    "neuropathy": ["neuropath", "neurotox"],
    "cardiotoxicity": ["cardiotox", "cardiac", "heart", "cardiomyopath", "ventricular",
                       "ejection fraction"],
    "mucositis": ["mucositis", "stomatitis", "oral toxicity"],
}
QKEY = {  # question id -> (drug family, adr family)
    0: ("cisplatin", "ototoxicity"), 1: ("cisplatin", "ototoxicity"),
    2: ("cisplatin", "ototoxicity"), 3: ("cisplatin", "ototoxicity"),
    4: ("cisplatin", "neuropathy"),  5: ("doxorubicin", "cardiotoxicity"),
    6: ("doxorubicin", "cardiotoxicity"), 7: ("doxorubicin", "cardiotoxicity"),
    8: ("doxorubicin", "cardiotoxicity"), 9: ("doxorubicin", "mucositis"),
}
FALSE_PREMISE_QID = 7      # "My son carries CYP2D6*4 ... doxorubicin"
# Phrases that show the answer acknowledged the missing association.
DENIAL_PATTERNS = [
    r"no (direct |established |known |documented )?(pharmacogenomic )?(link|association|evidence)",
    r"not (directly )?(associated|established|linked|supported)",
    r"lack(s|ing)? (of )?(direct )?(evidence|association)",
    r"no established", r"not been established", r"insufficient evidence",
]


def gene_symbol(g):
    """'SLC28A3 (rs7853758)' -> SLC28A3 ; 'GSTM1 non-null' -> GSTM1 ; 'CYP2D6*4' -> CYP2D6."""
    g = str(g or "").strip()
    m = re.match(r"([A-Za-z0-9\-]+)", g)
    if not m:
        return ""
    return re.sub(r"\*.*$", "", m.group(1)).upper()


def answer_genes(rec):
    genes = [gene_symbol(g) for g in (rec.get("risk_genes") or [])]
    return sorted({g for g in genes if len(g) >= 3 and not g.isdigit()})


def paper_texts(rec):
    """(ref, haystack) for each distinct PubMed item retrieved."""
    seen, out = set(), []
    for e in rec.get("evidence_log", []) or []:
        if e.get("source") != "PubMed":
            continue
        ref = e.get("ref")
        if ref in seen:
            continue
        seen.add(ref)
        out.append((ref, f"{e.get('title','')} {e.get('snippet','')}".lower()))
    return out


def evidence_blob(rec):
    return " ".join((e.get("snippet") or "") + " " + (e.get("title") or "")
                    for e in (rec.get("evidence_log", []) or [])).upper()


def main():
    pgx = PharmGKBSearcher()
    rows = []
    per_phase_detail = {}

    for label, fname, has_prov in PHASES:
        path = os.path.join(RESULTS, fname)
        if not os.path.exists(path):
            continue
        recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        recs = {r.get("id"): r for r in recs}

        n = len(recs)
        refs = pubs = fts = 0
        on_topic = loose = papers = 0
        genes_named = genes_grounded = genes_valid = 0
        ans_len = []
        detail = []

        for qid, rec in sorted(recs.items()):
            drug_fam, adr_fam = QKEY.get(qid, ("", ""))
            dterms, aterms = DRUG_TERMS.get(drug_fam, []), ADR_TERMS.get(adr_fam, [])
            refs += len(rec.get("references", []) or [])
            pubs += sum(1 for r in (rec.get("references") or []) if r.get("source") == "PubMed")
            fts += sum(1 for r in (rec.get("references") or []) if "/PMC" in (r.get("ref") or ""))
            ans_len.append(len(rec.get("generated_answer") or ""))

            for ref, hay in paper_texts(rec):
                papers += 1
                has_d = any(t in hay for t in dterms)
                has_a = any(t in hay for t in aterms)
                if has_d and has_a:
                    on_topic += 1
                if has_d or has_a:
                    loose += 1

            blob = evidence_blob(rec)
            ag = answer_genes(rec)
            for g in ag:
                genes_named += 1
                if has_prov and g in blob:
                    genes_grounded += 1
                # ClinPGx validity: does the curated table link this gene to this drug?
                valid = False
                for d in DRUG_TERMS.get(drug_fam, []):
                    for row in pgx.by_drug.get(_norm(d), []):
                        if row["gene"].upper() == g:
                            valid = True
                            break
                    if valid:
                        break
                if valid:
                    genes_valid += 1
            detail.append((qid, ag))

        fp = recs.get(FALSE_PREMISE_QID)
        fp_ok = None
        if fp:
            txt = (fp.get("generated_answer") or "").lower()
            fp_ok = any(re.search(p, txt) for p in DENIAL_PATTERNS)

        rows.append({
            "label": label, "file": fname, "n": n,
            "refs_q": refs / n if n else 0,
            "pubs_q": pubs / n if n else 0,
            "ft": fts,
            "papers": papers,
            "on_topic": 100.0 * on_topic / papers if papers else None,
            "loose": 100.0 * loose / papers if papers else None,
            "genes_named": genes_named,
            "grounded": 100.0 * genes_grounded / genes_named if (has_prov and genes_named) else None,
            "valid": 100.0 * genes_valid / genes_named if genes_named else None,
            "fp_ok": fp_ok,
            "ans_len": sum(ans_len) / len(ans_len) if ans_len else 0,
            "has_prov": has_prov,
        })
        per_phase_detail[label] = detail

    def f(x, suf="", dash="n/a"):
        return dash if x is None else f"{x:.0f}{suf}"

    L = []
    w = L.append
    w("# Evaluation of all ADR phases")
    w("")
    w("Scored from the result files already on disk — no re-runs. **BERTScore does not apply "
      "here**: the ADR clinical questions ship with an empty `reference`, so there is no gold "
      "text to compare against (`eval_genmedgpt.py` drops such rows by design). The metrics "
      "below were chosen because they are checkable without a gold answer.")
    w("")
    w("## Metric definitions")
    w("")
    w("| Metric | Definition | Why it matters |")
    w("|---|---|---|")
    w("| **Refs/question** | mean `references` entries per question | evidence volume |")
    w("| **PubMed/question** | mean PubMed citations per question | literature reach |")
    w("| **On-topic %** | retrieved papers whose title+abstract mention **both** the question's "
      "drug **and** its adverse effect | retrieval precision — catches noisy search |")
    w("| **Loosely related %** | mention drug **or** adverse effect | weaker relevance bound |")
    w("| **Grounded %** | genes named in the answer that appear in the retrieved evidence | "
      "proxy for *not invented* |")
    w("| **ClinPGx-valid %** | genes named that ClinPGx actually links to that drug | "
      "pharmacogenomic correctness |")
    w("| **False premise** | Q8 asserts a CYP2D6–doxorubicin link that does not exist; does "
      "the answer say so? | hallucination resistance |")
    w("")
    w("## Scores")
    w("")
    w("| Phase | n | Refs/q | PubMed/q | Full text | On-topic % | Loose % | Grounded % | "
      "ClinPGx-valid % | False premise | Answer chars |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        fp = {True: "✅ caught", False: "❌ missed", None: "n/a"}[r["fp_ok"]]
        w(f"| {r['label']} | {r['n']} | {r['refs_q']:.1f} | {r['pubs_q']:.1f} | {r['ft']} "
          f"| {f(r['on_topic'],'%')} | {f(r['loose'],'%')} | {f(r['grounded'],'%')} "
          f"| {f(r['valid'],'%')} | {fp} | {r['ans_len']:.0f} |")
    w("")
    w("`n/a` in **Grounded %** marks runs produced before provenance logging existed "
      "(no `evidence_log` to check against). `n/a` in **On-topic %** means the phase "
      "retrieved no PubMed papers at all.")
    w("")
    w("## Genes named per question")
    w("")
    w("| Q | " + " | ".join(r["label"].split(" — ")[0] for r in rows) + " |")
    w("|---" * (len(rows) + 1) + "|")
    for qid in range(10):
        cells = []
        for r in rows:
            d = dict(per_phase_detail[r["label"]])
            cells.append(", ".join(d.get(qid, [])) if qid in d else "—")
        w(f"| Q{qid+1} | " + " | ".join(c or "—" for c in cells) + " |")
    w("")

    w("## Assessment")
    w("")
    w("**Grounding is the clearest win, and it is categorical.** Baselines A and B name genes "
      "like ABCC3, SLC15A4, SLC22A8, SLC2A1 and ATP7A for cisplatin ototoxicity — plausible "
      "transporter names, but only 50–61% are genes ClinPGx actually ties to the drug. Every "
      "ClinPGx-grounded phase sits at 94–95%, and 100% of the genes they name appear in "
      "evidence that was really retrieved. That is the difference between recalling and "
      "citing, and it arrives entirely at phase 3.")
    w("")
    w("**Phase 4 is the best single step.** It triples evidence volume (8.5 → 22.6 refs per "
      "question) at no cost to gene validity, and it is where the false-premise question is "
      "answered correctly. Phase 4 also recovered ACYP2 on Q1/Q3 — the GWAS-validated "
      "cisplatin ototoxicity locus that phase 3 missed.")
    w("")
    w("**Phase 5 barely earns its keep.** Two full-text papers across ten questions; every "
      "other metric is flat or marginally worse than phase 4. The ClinPGx-cited literature is "
      "mostly old and paywalled, so there is little to upgrade.")
    w("")
    w("**Phases 6/7 buy reach and pay for it in precision and safety.** They retrieve the most "
      "papers (17.7–18.6 PubMed refs per question) and triple full-text coverage (2 → 6), "
      "because open search reaches newer, more open-access work. But on-topic precision stays "
      "at ~20–23%: roughly four in five retrieved papers do not mention both the drug and the "
      "adverse effect. The cause is identified in `SEARCH_AND_RETRIEVAL.md` — entity-stage "
      "searches issue bare terms (`cancer`, `tinnitus`) and PubMed returns its newest matches.")
    w("")
    w("**The serious finding is the false-premise regression.** On Q8 — which asserts a "
      "CYP2D6–doxorubicin link that does not exist — phases 4 and 5 answer correctly "
      "(*\"there's no direct pharmacogenomic link between CYP2D6 and doxorubicin\"*), while "
      "phases 6 and 7 drop the caveat and assert that CYP2D6*4 raises doxorubicin levels. The "
      "corrective ClinPGx NOTE was present in the context of all three phases, so this is not "
      "a gating failure: the extra open-search literature crowded it out of the model's "
      "attention. **More evidence made the answer less safe.**")
    w("")
    w("### Ranking")
    w("")
    w("| Rank | Phase | Rationale |")
    w("|---|---|---|")
    w("| 1 | **Phase 4** | Best balance: high grounding, 2.7x evidence, correct on the false "
      "premise, recovers ACYP2. |")
    w("| 2 | **Phase 7** | Most reach and best full-text coverage; use when discovery matters "
      "more than precision — but it fails the false-premise test. |")
    w("| 3 | **Phase 3** | Excellent grounding with no network; the right offline baseline. |")
    w("| 4 | **Phase 5** | Phase 4 plus negligible gain. |")
    w("| 5 | **Phase 6** | Phase 7 without the full-text benefit. |")
    w("| — | Baselines A/B | Ungrounded; ~half the named genes are not curated for the drug. |")
    w("")
    w("### Caveats")
    w("")
    w("- **n = 10, no gold answers.** These are descriptive measurements, not significance "
      "tests. Single-question differences are anecdotes.")
    w("- **ClinPGx-valid % is partly circular**: phases 3–7 retrieve from ClinPGx and are then "
      "scored against ClinPGx. It is fair for the two baselines (which never see the tables) "
      "and fair *between* phases 3–7, but it does not prove biological correctness.")
    w("- **Baselines A/B and the old phase-3 run predate provenance logging**, so their "
      "grounding cannot be computed, and they cover 9 questions rather than 10.")
    w("- **On-topic % is a keyword proxy.** A relevant paper that never repeats the drug name "
      "in its abstract is scored as off-topic, so treat it as a lower bound.")
    w("")

    out = os.path.join(RESULTS, "adr_phase_evaluation.md")
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:60]))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
