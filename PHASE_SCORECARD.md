# Phase scorecard — measurements and ranking

All phases: same 10 ADR clinical questions, same model (`qwen2.5:14b`), same code, differing
only by environment variables.

## 1. Raw measurements

| Phase | Refs/q | PubMed/q | Full-text papers | On-topic % | Gene pairs | Disputed | Paragraphs read | False premise |
|---|---|---|---|---|---|---|---|---|
| Phase 3 — ClinPGx only | 8.5 | 0 | 0 | n/a | ~2–3 | – | 0 | ❌ |
| Phase 4 — + cited PubMed | 22.6 | 14.3 | 0 | 22% | ~2–3 | – | 0 | ✅ |
| Phase 9 — combined-topic + full text | 22.5 | 14.0 | 6 | 54% | ~2–3 | – | 0 | ❌ |
| Phase 9L — P9 retrieval + ledger | 23.4 | 14.5 | 9 | 52% | **116** | 72 | 53 | ❌ |
| Phase 11 — free retrieval + ledger | 13.0 | 4.8 | 6 | **65%** | 96 | 61 | 41 | ✅ |
| Phase 12 — + expanded OA full text | 13.7 | 4.6 | 12 | 63% | 91 | 65 | 44 | ✅ |
| **Phase 13 — contradiction resolution** | **23.8** | 14.5 | **17** | 49% | **145** | 87 | **70** | ❌ |

## 2. Normalised dimensions (0–5, linear against the best observed value)

| Phase | Recall | Precision | Provenance | Reading depth | Contradiction handling | Calibration | Safety |
|---|---|---|---|---|---|---|---|
| Phase 3 | 0.9 | 0.0 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Phase 4 | 0.9 | 1.7 | 4.7 | 0.0 | 0.0 | 0.0 | **5.0** |
| Phase 9 | 0.9 | 4.2 | 4.7 | 1.8 | 0.0 | 0.0 | 0.0 |
| Phase 9L | 4.0 | 4.0 | 4.9 | 2.6 | 2.5 | 3.8 | 0.0 |
| Phase 11 | 3.3 | **5.0** | 2.7 | 1.8 | 2.5 | **5.0** | **5.0** |
| Phase 12 | 3.1 | 4.8 | 2.9 | 3.5 | 1.9 | 3.8 | **5.0** |
| **Phase 13** | **5.0** | 3.8 | **5.0** | **5.0** | **5.0** | 3.8 | 0.0 |

*Contradiction handling*: 0 = none · 2 = untyped flags · 1.5 = untyped **and** inflated by
mechanistic evidence · 4 = typed, comparability-aware.
*Calibration*: 0 = none · 3 = rule-based but not benchmarked on that configuration ·
4 = rule-based **and** benchmarked (only phase 11 was, on 72 labelled pairs).

## 3. Composite scores — the weighting is a judgment call

**Research goal** (contradictions 30%, recall 20%, calibration 15%, depth 15%, precision 10%,
provenance 5%, safety 5%):

| Rank | Phase | Score |
|---|---|---|
| 1 | **Phase 13** | **4.44** |
| 2 | Phase 11 | 3.31 |
| 3 | Phase 9L / Phase 12 | 3.16 |
| 5 | Phase 9 | 1.09 |
| 6 | Phase 4 | 0.83 |

**Clinical-safety priority** (safety 30%, precision 25%, calibration 20%, contradictions 15%):

| Rank | Phase | Score |
|---|---|---|
| 1 | **Phase 11** | **4.40** |
| 2 | Phase 12 | 4.05 |
| 3 | Phase 13 | 2.94 |
| 4 | Phase 9L | 2.54 |
| 5 | Phase 4 | 2.19 |

**The ranking flips between the two weightings.** Phase 13 leads on the research objective;
phase 11 leads if a wrong answer to a false-premise question is the dominant risk. Reproduce or
re-weight with `python score_phases.py`.

## 4. Phase 13 in detail

| Status | n | Meaning |
|---|---|---|
| INSUFFICIENT | 120 (83%) | fewer than two comparable clinical sources |
| CONFLICTING | 22 | comparable evidence supports both directions |
| CONTEXT-DEPENDENT | 3 | the conflict dissolves once context is fixed |
| CONSISTENT | 0 | never fired |
| CURATED-LITERATURE CONFLICT | 0 | never fired |

**The three resolved cases** — the capability the layer was built for:

- **TPMT × cisplatin** — *endpoint differs*: support measures "ototoxicity / hearing loss",
  refutation measures "clinically significant hearing loss"
- **SLC28A3 × anthracycline** — *population differs*: children vs adults
- **GSTM1 × doxorubicin** — *cancer type differs*: ALL/lymphoma vs mixed haematologic and solid

The TPMT endpoint split and the SLC28A3 paediatric/adult split are documented nuances of that
literature, recovered from the papers rather than asserted.

**Comparability worked**: 29 cards carry a note that the refuting or supporting evidence is
mechanistic only — the inflation phase 12 was counting as contradictions.

**Three defects**:

1. **83% INSUFFICIENT.** 48 pairs had zero comparable clinical sources, 72 had exactly one. A
   pair backed only by a curated row cannot be assessed for contradiction and falls through.
2. **CONSISTENT is unreachable.** Almost every ClinPGx pair here is marked `ambiguous`, which
   routes to CONFLICTING before the consistent branch is tested.
3. **Half the conflicts are unexplained** (11 of 22). Context extraction is uneven —
   endpoint 92%, direction 73%, population and cancer type **51%**, dose 30% — so the axis
   often cannot be named.

## 5. Caveats

- **n = 10, no gold answers** for the ADR set. Differences of a few points are not significant.
- **Only phase 11 has a calibration measurement** (72 labelled pairs: separation +0.351,
  Spearman 0.721, contradiction recall 0.95). Phases 9L/12/13 use the same formula but were
  never benchmarked, so their calibration score is assumed, not measured.
- **`ClinPGx-valid %` and `Grounded %` are excluded** from the scoring: the first penalises
  literature-derived findings, the second misses ledger-sourced genes absent from
  `evidence_log`.
- **On-topic % is a keyword proxy** and therefore a lower bound.
