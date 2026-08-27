# Evidence ledger — evaluation

The system now reports **every** candidate gene with a rule-computed confidence and an explicit contradiction flag, instead of naming 2–3 genes in prose. Confidence is computed in `evidence_ledger.py` from the ClinPGx evidence level, study types, the number of independent supporting sources and the weight of refuting ones — the model never emits the number, which is what makes calibration meaningful.

## Benchmark — labelled gene–drug pairs

72 pairs: **disputed** 25, **negative** 24, **positive** 23

### Did the system surface the target pair at all?

| Label | pairs | target found | recall |
|---|---|---|---|
| positive | 23 | 15 | 65% |
| negative | 24 | 16 | 67% |
| disputed | 25 | 21 | 84% |

### Confidence calibration

Mean confidence should be highest for `positive`, lowest for `negative`.

| Label | n | mean confidence | median | label distribution |
|---|---|---|---|---|
| positive | 15 | 0.424 | 0.471 | low:8, moderate:5, very_low:2 |
| negative | 16 | 0.073 | 0.054 | very_low:16 |
| disputed | 21 | 0.351 | 0.329 | low:13, moderate:4, very_low:4 |

**Separation (positive − negative): +0.351** — positive above negative is the property that makes the score usable.

**Spearman(confidence, label order) = 0.721** over 52 pairs.

### Contradiction detection

`disputed=True` should fire on `disputed` pairs (ClinPGx `ambiguous`) and stay quiet on clean positives.

| | flagged disputed | not flagged |
|---|---|---|
| **is disputed** | 20 | 1 |
| **is not** | 23 | 8 |

precision **0.47** · recall **0.95** · F1 **0.62**

Flag types raised: `curated_vs_literature` 21, `curator_ambiguous` 20, `literature_internal` 18, `uncurated_literature_claim` 2, `unsupported_claim` 2

## ADR question set — recall and reporting

- **96 gene–drug pairs** across 10 questions (mean 9.6 per question; previous phases named 2–3)
- **61** carry a contradiction flag
- confidence labels: moderate 43, low 36, very_low 17
- answers citing a reference: **1/10** (phase 10 scored 0/10)

| Q | pairs | disputed | highest-confidence genes |
|---|---|---|---|
| Q1 | 19 | 10 | COMT 0.59, XPC 0.59, ABCC3 0.56 |
| Q2 | 10 | 10 | ABCC3 0.56, GSTM1 0.56, SLC16A5 0.56 |
| Q3 | 18 | 10 | COMT 0.59, ABCC3 0.56, GSTM1 0.56 |
| Q4 | 16 | 7 | SLC19A1 0.62, CYP2E1 0.59, ABCC3 0.56 |
| Q5 | 7 | 6 | SLC19A1 0.62, CYP2E1 0.59, GSTP1 0.59 |
| Q6 | 3 | 3 | SLC28A3 0.71, GSTP1 0.56, RARG 0.56 |
| Q7 | 8 | 7 | HAS3 0.58, SLC28A3 0.44, GSTP1 0.39 |
| Q8 | 7 | 3 | SLC28A3 0.71, GSTP1 0.56, RARG 0.56 |
| Q9 | 6 | 5 | GSTP1 0.56, SLC28A3 0.54, RARG 0.39 |
| Q10 | 2 | 0 | CYBA 0.62, ERCC1 0.62 |

## Caveats

- The benchmark labels come from ClinPGx, and the system also retrieves from ClinPGx, so calibration is partly self-consistent by construction. It is still informative for the `negative` and `disputed` classes, where the system must *disagree* with what its own retrieval surfaces, and for the literature-derived component of every score.
- `ClinPGx-valid %` from the earlier phase comparison is retired as a quality metric: it marks uncurated literature findings as wrong, which is the opposite of the goal here.
