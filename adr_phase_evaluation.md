# Evaluation of all ADR phases

Scored from the result files already on disk — no re-runs. **BERTScore does not apply here**: the ADR clinical questions ship with an empty `reference`, so there is no gold text to compare against (`eval_genmedgpt.py` drops such rows by design). The metrics below were chosen because they are checkable without a gold answer.

## Metric definitions

| Metric | Definition | Why it matters |
|---|---|---|
| **Refs/question** | mean `references` entries per question | evidence volume |
| **PubMed/question** | mean PubMed citations per question | literature reach |
| **On-topic %** | retrieved papers whose title+abstract mention **both** the question's drug **and** its adverse effect | retrieval precision — catches noisy search |
| **Loosely related %** | mention drug **or** adverse effect | weaker relevance bound |
| **Grounded %** | genes named in the answer that appear in the retrieved evidence | proxy for *not invented* |
| **ClinPGx-valid %** | genes named that ClinPGx actually links to that drug | pharmacogenomic correctness |
| **False premise** | Q8 asserts a CYP2D6–doxorubicin link that does not exist; does the answer say so? | hallucination resistance |

## Scores

| Phase | n | Refs/q | PubMed/q | Full text | On-topic % | Loose % | Grounded % | ClinPGx-valid % | False premise | Answer chars |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline A — no external sources | 9 | 0.0 | 0.0 | 0 | n/a | n/a | n/a | 61% | ❌ missed | 698 |
| Baseline B — paper setup (PubMed+Wiki) | 9 | 0.0 | 0.0 | 0 | n/a | n/a | n/a | 50% | ❌ missed | 719 |
| Phase 3 (old run) — ClinPGx | 9 | 0.0 | 0.0 | 0 | n/a | n/a | n/a | 94% | ❌ missed | 679 |
| Phase 3 — ClinPGx only | 10 | 8.5 | 0.0 | 0 | n/a | n/a | 100% | 95% | ❌ missed | 668 |
| Phase 4 — ClinPGx + cited PubMed | 10 | 22.6 | 14.3 | 0 | 22% | 38% | 100% | 95% | ✅ caught | 631 |
| Phase 5 — + PMC full text | 10 | 23.2 | 14.3 | 2 | 17% | 34% | 100% | 95% | ✅ caught | 653 |
| Phase 6 — open LLM search (abstracts) | 10 | 25.8 | 17.7 | 0 | 20% | 50% | 100% | 94% | ❌ missed | 617 |
| Phase 7 — open search + full text | 10 | 26.9 | 18.6 | 6 | 23% | 51% | 100% | 95% | ❌ missed | 628 |

`n/a` in **Grounded %** marks runs produced before provenance logging existed (no `evidence_log` to check against). `n/a` in **On-topic %** means the phase retrieved no PubMed papers at all.

## Genes named per question

| Q | Baseline A | Baseline B | Phase 3 (old run) | Phase 3 | Phase 4 | Phase 5 | Phase 6 | Phase 7 |
|---|---|---|---|---|---|---|---|---|
| Q1 | ABCC3, SLC15A4, SLC22A8 | ABCB1, SLC2A1 | GSTM1, TPMT | GSTM1, TPMT | ACYP2, GSTM1 | GSTM1, GSTP1 | GSTM1 | ACYP2, GSTM1 |
| Q2 | ABCB1, GSTP1, SLC2A1 | ATP7A, SLC2A1 | GSTM1, TPMT | GSTM1, TPMT | GSTM1 | GSTM1 | COMT, GSTM1, TPMT | COMT, GSTM1, TPMT |
| Q3 | TPMT | TPMT | GSTM1, TPMT | GSTM1, TPMT | ACYP2, GSTM1, TPMT | GSTM1, TPMT | TPMT | ACYP2, GSTM1, TPMT |
| Q4 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 |
| Q5 | OXR1, SLC7A11, XRCC1 | — | ERCC1, GSTP1 | ERCC1, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 |
| Q6 | ABCB1, GSTP1 | ABCB1, CYP3A4, CYP3A5 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 |
| Q7 | ABCB1, APOE, GSTP1 | ABCB1, APOE, SLCO1B1 | GSTP1, SLC28A3 | RARG, SLC28A3 | GSTP1, RARG, SLC28A3 | GSTP1, RARG, SLC28A3 | RARG, SLC28A3 | GSTP1, RARG, SLC28A3 |
| Q8 | CYP2D6 | CYP2D6 | CYP2D6, SLC28A3 | CYP2D6, SLC28A3 | CYP2D6, SLC28A3 | CYP2D6, SLC28A3 | CYP2D6 | CYP2D6 |
| Q9 | GSTM1 | GSTM1 | GSTM1, GSTP1, SLC28A3 | GSTM1, GSTP1, SLC28A3 | GSTM1, SLC28A3 | GSTM1, SLC28A3 | GSTM1 | GSTM1, SLC28A3 |
| Q10 | — | — | — | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 |

## Assessment

**Grounding is the clearest win, and it is categorical.** Baselines A and B name genes like ABCC3, SLC15A4, SLC22A8, SLC2A1 and ATP7A for cisplatin ototoxicity — plausible transporter names, but only 50–61% are genes ClinPGx actually ties to the drug. Every ClinPGx-grounded phase sits at 94–95%, and 100% of the genes they name appear in evidence that was really retrieved. That is the difference between recalling and citing, and it arrives entirely at phase 3.

**Phase 4 is the best single step.** It triples evidence volume (8.5 → 22.6 refs per question) at no cost to gene validity, and it is where the false-premise question is answered correctly. Phase 4 also recovered ACYP2 on Q1/Q3 — the GWAS-validated cisplatin ototoxicity locus that phase 3 missed.

**Phase 5 barely earns its keep.** Two full-text papers across ten questions; every other metric is flat or marginally worse than phase 4. The ClinPGx-cited literature is mostly old and paywalled, so there is little to upgrade.

**Phases 6/7 buy reach and pay for it in precision and safety.** They retrieve the most papers (17.7–18.6 PubMed refs per question) and triple full-text coverage (2 → 6), because open search reaches newer, more open-access work. But on-topic precision stays at ~20–23%: roughly four in five retrieved papers do not mention both the drug and the adverse effect. The cause is identified in `SEARCH_AND_RETRIEVAL.md` — entity-stage searches issue bare terms (`cancer`, `tinnitus`) and PubMed returns its newest matches.

**The serious finding is the false-premise regression.** On Q8 — which asserts a CYP2D6–doxorubicin link that does not exist — phases 4 and 5 answer correctly (*"there's no direct pharmacogenomic link between CYP2D6 and doxorubicin"*), while phases 6 and 7 drop the caveat and assert that CYP2D6*4 raises doxorubicin levels. The corrective ClinPGx NOTE was present in the context of all three phases, so this is not a gating failure: the extra open-search literature crowded it out of the model's attention. **More evidence made the answer less safe.**

### Ranking

| Rank | Phase | Rationale |
|---|---|---|
| 1 | **Phase 4** | Best balance: high grounding, 2.7x evidence, correct on the false premise, recovers ACYP2. |
| 2 | **Phase 7** | Most reach and best full-text coverage; use when discovery matters more than precision — but it fails the false-premise test. |
| 3 | **Phase 3** | Excellent grounding with no network; the right offline baseline. |
| 4 | **Phase 5** | Phase 4 plus negligible gain. |
| 5 | **Phase 6** | Phase 7 without the full-text benefit. |
| — | Baselines A/B | Ungrounded; ~half the named genes are not curated for the drug. |

### Caveats

- **n = 10, no gold answers.** These are descriptive measurements, not significance tests. Single-question differences are anecdotes.
- **ClinPGx-valid % is partly circular**: phases 3–7 retrieve from ClinPGx and are then scored against ClinPGx. It is fair for the two baselines (which never see the tables) and fair *between* phases 3–7, but it does not prove biological correctness.
- **Baselines A/B and the old phase-3 run predate provenance logging**, so their grounding cannot be computed, and they cover 9 questions rather than 10.
- **On-topic % is a keyword proxy.** A relevant paper that never repeats the drug name in its abstract is scored as off-topic, so treat it as a lower bound.

