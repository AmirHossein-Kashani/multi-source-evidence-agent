# Evidence ledger — evaluation

The system now reports **every** candidate gene with a rule-computed confidence and an explicit contradiction flag, instead of naming 2–3 genes in prose. Confidence is computed in `evidence_ledger.py` from the ClinPGx evidence level, study types, the number of independent supporting sources and the weight of refuting ones — the model never emits the number, which is what makes calibration meaningful.

## Benchmark — labelled gene–drug pairs

_No benchmark results found._

## ADR question set — recall and reporting

- **91 gene–drug pairs** across 10 questions (mean 9.1 per question; previous phases named 2–3)
- **65** carry a contradiction flag
- confidence labels: moderate 48, low 37, very_low 6
- answers citing a reference: **0/10** (phase 10 scored 0/10)

| Q | pairs | disputed | highest-confidence genes |
|---|---|---|---|
| Q1 | 9 | 9 | COMT 0.59, ABCC3 0.56, GSTM1 0.56 |
| Q2 | 10 | 10 | ABCC3 0.56, GSTM1 0.56, SLC16A5 0.56 |
| Q3 | 17 | 11 | COMT 0.59, HIF1A 0.57, TNF 0.57 |
| Q4 | 8 | 7 | SLC19A1 0.62, CYP2E1 0.59, ABCC3 0.56 |
| Q5 | 7 | 6 | SLC19A1 0.62, CYP2E1 0.59, GSTP1 0.59 |
| Q6 | 3 | 3 | SLC28A3 0.71, GSTP1 0.56, RARG 0.56 |
| Q7 | 11 | 6 | HAS3 0.58, RARG 0.56, SLC28A3 0.54 |
| Q8 | 4 | 4 | SLC28A3 0.71, GSTP1 0.56, RARG 0.56 |
| Q9 | 9 | 5 | GSTP1 0.56, SLC28A3 0.54, RARG 0.39 |
| Q10 | 13 | 4 | CYBA 0.62, ERCC1 0.62, TP53 0.57 |

## Caveats

- The benchmark labels come from ClinPGx, and the system also retrieves from ClinPGx, so calibration is partly self-consistent by construction. It is still informative for the `negative` and `disputed` classes, where the system must *disagree* with what its own retrieval surfaces, and for the literature-derived component of every score.
- `ClinPGx-valid %` from the earlier phase comparison is retired as a quality metric: it marks uncurated literature findings as wrong, which is the opposite of the goal here.
