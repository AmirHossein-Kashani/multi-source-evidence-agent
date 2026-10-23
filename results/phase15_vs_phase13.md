# Phase 15 vs phase 13 — first run (job 24773342, 2026-10-23)

Same 10 development questions, same model (qwen2.5:14b), same base retrieval as phase 13,
plus the phase-15 machinery (`docs/PLAN.md`): typed-path proposals, edge queue with a
6-query budget, up to 2 targeted rounds, follow-up queries from the cards, and the step-0
audit fixes. Wall time 1 h 27 min (phase 13: ~2.5 h budget); 10/10 questions, no errors.

**Caveat on this run.** The runner did not persist `path_candidates`, `search_rounds` and
`off_drug_claims` (fixed in the commit after the run); the per-question round data below is
recovered from the job log (`results/adrclin_phase15_loop.rounds_from_log.json`). The
`proposed_via` tags inside the ledger entries were persisted.

## Headline numbers

| | Phase 13 | Phase 15 |
|---|---|---|
| Ledger groups (total / per question) | 145 / 14.5 (gene+drug) | 312 / 31.2 (gene+drug+outcome) |
| References per question | 23.8 | 34.8 |
| Papers digested per question | 3.7 | 9.6 |
| Cards: INSUFFICIENT | 120 (83%) | 269 (86%) |
| Cards: CONFLICTING | 22 (15%) | 32 (10%) |
| Cards: CONTEXT-DEPENDENT | 3 (2%) | 7 (2%) |
| Cards: CURATED-LITERATURE CONFLICT | 0 | 2 |
| Cards: CONSISTENT | 0 | **2** |
| Disputed pairs | 87 (60%) | 179 (57%) |
| Candidate associations (literature-only, cohort-or-better support) | 9 | **26** |
| Candidates named in the answer | 0 | **0** |
| Answer length (chars) | 867 | 858 |

Per question (from the log): 10 path candidates proposed each; rounds ran 2/2/1/1/1/2/2/2/2/2;
each round read 6 new papers (0–4 of them cohort-or-better); 22+7, 17+3, 16, 5, 5, 9+9, 26+11, 13+6, 16+8, 12+1 edges were
written back per question. 13 claims (in 7 questions) were excluded because the paper studied another drug.

## What the original phase-13 pairs became

Best status per (question, gene, drug) in phase 13 → phase 15:

| Phase 13 | Phase 15 | n |
|---|---|---|
| INSUFFICIENT | absent (pair not retrieved this run) | 57 |
| INSUFFICIENT | INSUFFICIENT | 46 |
| INSUFFICIENT | CONFLICTING | 12 |
| INSUFFICIENT | CONTEXT-DEPENDENT | 4 |
| INSUFFICIENT | CURATED-LITERATURE CONFLICT | 1 |
| CONFLICTING | CONFLICTING | 14 |
| CONFLICTING | INSUFFICIENT | 7 |
| CONTEXT-DEPENDENT | CONFLICTING / CONTEXT-DEPENDENT | 2 / 1 |

17 of the 120 INSUFFICIENT pairs were resolved to another status; 46 stayed; **57 did not
appear at all** — the base retrieval (LLM-chosen queries, live PubMed) is not reproducible
run to run, so the two ledgers overlap only partly. The fixed-retrieval ablation (E2) is
needed before any per-pair comparison can be trusted.

## Readings

1. **The loop works mechanically** — proposals, budget, rounds, write-back, early stop
   (3 questions stopped after round 1 for lack of cohort-or-better papers) — with the real
   model and live NCBI, in less wall time than phase 13 because digests are cached.
2. **INSUFFICIENT did not fall.** More papers → more single-source groups; the absolute
   count tripled and the rate rose 83 → 86%. Follow-up queries resolved some original pairs
   (17/120) but the new groups they created are themselves single-source. Resolution has to
   be measured on a fixed set of pairs, and the follow-up filter should probably run before
   new pairs are opened.
3. **Candidates tripled (9 → 26) but none reached the answer.** The block was in the prompt;
   the answer chain was never told to report it. Fixed after the run (explicit instruction +
   `candidate_genes` output field). Several of the 26 were not gene symbols at all ("CBR",
   "AKR", "MATE1"): fixed after the run with an NCBI Gene check; such names stay in the
   ledger but cannot be candidates.
4. **Path proposals were alphabetical within a pattern** (equal priors): fixed after the run
   by ranking on the row's citation count. For a question naming a drug *class*, genes
   already curated for the class could be proposed as new: fixed.
5. **Evidence kinds matter:** of 96 digests, 25 were expression and 8 protein-biomarker
   findings — a third of the literature evidence is not inherited-variant evidence and now
   weighs half.
6. **Drug matching:** 375 claims exact, 10 class-level, 15 unstated, 13 excluded as off-drug.
7. **PubMed publication types changed the study type once in 96 digests**: the cross-check
   rarely bites; the model's own call is usually consistent with the index.
8. MeSH lookups hit NCBI's rate limit in this run (fallback to static tables); fixed.

## Next

- Re-run phase 15 with the post-run fixes (candidate reporting, symbol check, ranking).
- E1 masked recovery: hide curated pairs, measure recovery by pattern and by round.
- E2 fixed-retrieval ablation on cached evidence, so per-pair resolution is comparable.
