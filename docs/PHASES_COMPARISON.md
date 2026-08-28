# AMG-RAG phases — comparison tables

All phases: same code, same model (`qwen2.5:14b`), same 10 ADR clinical questions, differing
**only by environment variables**. Baselines A/B and the old phase-3 run cover 9 questions and
predate provenance logging.

---

## 1. Configuration matrix

| Phase | `AMG_KB_SOURCE` | Full text | Digest | Ledger | Query construction |
|---|---|---|---|---|---|
| A | — (`AMG_USE_EXTERNAL=0`) | — | — | — | none |
| B | — (`AMG_USE_EXTERNAL=1`) | — | — | — | raw question → PubMed + Wikipedia |
| 3 | `pharmgkb` | — | — | — | none (offline tables) |
| 4 | `pharmgkb+pubmed` | — | — | — | ClinPGx-cited PMIDs + raw-question top-up |
| 5 | `pharmgkb+pubmed` | ✅ | — | — | as phase 4 |
| 6 | `pharmgkb+pubmed_open` | — | — | — | LLM picks topics, one per query |
| 7 | `pharmgkb+pubmed_open` | ✅ | — | — | as phase 6 |
| 8 | `pharmgkb+pubmed_combo` | — | — | — | graph-related terms, `AND`-joined by code |
| 9 | `pharmgkb+pubmed_combo` | ✅ | — | — | as phase 8 |
| 10 | `pharmgkb+pubmed_free` | ✅ | ✅ | — | model authors the query, any arity |
| **9L** | `pharmgkb+pubmed_combo` | ✅ | ✅ | ✅ | phase-9 conjunctions |
| **11** | `pharmgkb+pubmed_free` | ✅ | ✅ | ✅ | model-authored |

---

## 2. Headline metrics

| Phase | n | Refs/q | PubMed/q | Full text | On-topic % | Loose % | Grounded % | ClinPGx-valid % | False premise | Answer chars |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline A — no external | 9 | 0.0 | 0.0 | 0 | n/a | n/a | n/a | 61% | ❌ | 698 |
| Baseline B — paper setup | 9 | 0.0 | 0.0 | 0 | n/a | n/a | n/a | 50% | ❌ | 719 |
| Phase 3 (old run) | 9 | 0.0 | 0.0 | 0 | n/a | n/a | n/a | 94% | ❌ | 679 |
| Phase 3 — ClinPGx only | 10 | 8.5 | 0.0 | 0 | n/a | n/a | 100% | 95% | ❌ | 668 |
| **Phase 4 — + cited PubMed** | 10 | 22.6 | 14.3 | 0 | 22% | 38% | 100% | 95% | **✅** | 631 |
| Phase 5 — + full text | 10 | 23.2 | 14.3 | 2 | 17% | 34% | 100% | 95% | ✅ | 653 |
| Phase 6 — open search | 10 | 25.8 | 17.7 | 0 | 20% | 50% | 100% | 94% | ❌ | 617 |
| Phase 7 — open + full text | 10 | **26.9** | **18.6** | 6 | 23% | 51% | 100% | 95% | ❌ | 628 |
| Phase 8 — combined-topic | 10 | 22.2 | 13.5 | 0 | 54% | 83% | 100% | 93% | ❌ | 628 |
| Phase 9 — combined + full text | 10 | 22.5 | 14.0 | 6 | 54% | 83% | 100% | 95% | ❌ | 602 |
| Phase 10 — free arity | 10 | 13.0 | 4.6 | 5 | 59% | 80% | 92% | 80% | ❌ | 702 |
| **Phase 9L — P9 retrieval + ledger** | 10 | 23.4 | 14.5 | **7** | 52% | 80% | 76% | 89% | ❌ | 800 |
| **Phase 11 — evidence ledger** | 10 | 13.0 | 4.8 | 4 | **65%** | 81% | 81% | 85% | **✅** | 794 |

**Metric definitions**

| Metric | Meaning |
|---|---|
| Refs/q | mean deduplicated citations per question |
| On-topic % | retrieved papers whose title+abstract mention **both** the drug **and** the adverse effect |
| Loose % | mention drug **or** effect |
| Grounded % | genes named that appear as text in the retrieval log |
| ClinPGx-valid % | genes named that ClinPGx links to that drug |
| False premise | does the Q8 answer state that no CYP2D6–doxorubicin association exists? |

> **Two metrics must not be read as quality for phases 9L/11.** *ClinPGx-valid* marks
> literature-derived genes wrong merely because ClinPGx has not curated them — the opposite of
> the goal. *Grounded* under-reports because the ledger's curated lookup bypasses
> `evidence_log`; all five "ungrounded" phase-11 genes were verified as present in the ledger
> with real sources.

---

## 3. Retrieval precision — the clearest progression

| Search shape | Phases | On-topic % |
|---|---|---|
| ClinPGx citations + raw-question top-up | 4, 5 | 17–22% |
| one LLM topic per query | 6, 7 | 20–23% |
| graph-related terms `AND`-joined | 8, 9, 9L | 52–54% |
| model-authored, free arity | 10, 11 | **59–65%** |

---

## 4. Search shape — how many items per query

| Phase | Queries | 1-term | 2-term | 3-term | 4+ | Empty | Back-offs |
|---|---|---|---|---|---|---|---|
| 8 | 160 | 0 | 85 (53%) | 75 (47%) | 0 | 12 | 19 |
| 9 | 159 | 0 | 80 (50%) | 79 (50%) | 0 | 10 | 18 |
| 9L | 160 | 0 | 85 (53%) | 75 (47%) | 0 | 11 | 18 |
| 10 | 392 | 23 | 237 | 110 | 22 | **0** | 39 |
| 11 | 392 | 31 | 246 | 103 | 12 | **0** | 39 |

Phases 8/9/9L are capped at 2–4 terms by the prompt and never produce 1 or 4. Phases 10/11
choose freely and use the whole range — including the single-item searches that were previously
impossible. Empty queries fall to zero once back-off is added.

---

## 5. Ledger phases — recall, contradictions, reading

| | Phase 9L | Phase 11 |
|---|---|---|
| Gene–drug pairs surfaced | **116** (11.6/question) | 96 (9.6/question) |
| Pairs with a contradiction flag | **72** | 61 |
| PubMed references | **145** | 48 |
| Papers digested | **35** | 29 |
| Relevant paragraphs cited | **53** | 41 |
| Full-text papers | **7** | 4 |
| Mean confidence | 0.395 | 0.414 |
| Confidence labels | moderate 40 / low 61 / very_low 15 | moderate 43 / low 36 / very_low 17 |

**Contradiction types raised**

| Flag | 9L | 11 | Meaning |
|---|---|---|---|
| `curator_ambiguous` | 62 | 61 | ClinPGx curators recorded conflicting evidence |
| `unsupported_claim` | 38 | 30 | no curated row and no strong supporting study |
| `literature_internal` | 10 | 3 | retrieved papers disagree with each other |
| `curated_vs_literature` | 5 | 0 | the tables and the papers disagree |
| `uncurated_literature_claim` | 4 | 0 | not curated, but backed by human studies — candidate novel finding |

---

## 6. Confidence calibration — 72 labelled ClinPGx pairs (phase 11)

Labels from `relationships.tsv`: `associated` (positive), `not associated` (negative),
`ambiguous` (disputed). The benchmark ran 72 of 150 pairs before its wall-clock limit.

| Label | n found | mean confidence | assigned labels |
|---|---|---|---|
| positive | 15 | **0.424** | low 8, moderate 5, very_low 2 |
| disputed | 21 | 0.351 | low 13, moderate 4, very_low 4 |
| negative | 16 | **0.073** | very_low 16 |

- **Separation (positive − negative): +0.351**
- **Spearman(confidence, label order) = 0.721** over 52 pairs
- Target-pair recall: positive 65%, negative 67%, disputed 84%

**Contradiction detection:** precision **0.47**, recall **0.95**, F1 **0.62** (20 of 21
disputed pairs caught; 23 false positives, mostly genuine literature-vs-curation disagreement).

---

## 7. Cost

| Run | Questions | Wall time |
|---|---|---|
| Phase 3 (ClinPGx only) | 10 | ~22 min |
| Phases 4+5 together | 10 | 1 h 14 |
| Phases 6+7 together | 10 | 1 h 15 |
| Phases 8+9 together | 10 | 1 h 18 |
| Phase 10 (digest) | 10 | 43 min |
| Phase 9L (digest + ledger) | 10 | 45 min |
| Phase 11 (digest + ledger) | 10 | 47 min |
| Benchmark (phase 11) | 72 of 150 | 5 h (timed out) |

---

## Caveats

- **n = 10**, no gold answers for the ADR set: differences in the 50–65% range are descriptive,
  not significant.
- **Benchmark labels come from ClinPGx**, which the system also retrieves from, so calibration
  is partly self-consistent. It remains informative for `negative` and `disputed`, where the
  system must disagree with what its own retrieval surfaces.
- **On-topic % is a keyword proxy** — a relevant paper that never repeats the drug name scores
  as off-topic, so all values are lower bounds.
