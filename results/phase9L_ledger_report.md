# Evidence ledger — evaluation

The system now reports **every** candidate gene with a rule-computed confidence and an explicit contradiction flag, instead of naming 2–3 genes in prose. Confidence is computed in `evidence_ledger.py` from the ClinPGx evidence level, study types, the number of independent supporting sources and the weight of refuting ones — the model never emits the number, which is what makes calibration meaningful.

## Benchmark — labelled gene–drug pairs

_No benchmark results found._

## ADR question set — recall and reporting

- **116 gene–drug pairs** across 10 questions (mean 11.6 per question; previous phases named 2–3)
- **72** carry a contradiction flag
- confidence labels: low 61, moderate 40, very_low 15
- answers citing a reference: **0/10** (phase 10 scored 0/10)

| Q | pairs | disputed | highest-confidence genes |
|---|---|---|---|
| Q1 | 18 | 8 | COMT 0.59, ALDH2 0.58, ABCC3 0.56 |
| Q2 | 19 | 12 | COMT 0.64, ABCC3 0.59, SLC22A2 0.59 |
| Q3 | 19 | 12 | COMT 0.62, ABCC3 0.59, SLC22A2 0.59 |
| Q4 | 10 | 9 | SLC19A1 0.62, CYP2E1 0.59, ERCC1 0.59 |
| Q5 | 18 | 6 | SLC19A1 0.62, CYP2E1 0.59, ABCC3 0.56 |
| Q6 | 6 | 6 | GSTP1 0.56, SLC28A3 0.54, RARG 0.39 |
| Q7 | 9 | 7 | HAS3 0.58, SLC28A3 0.46, GSTP1 0.43 |
| Q8 | 8 | 8 | SLC28A3 0.44, GSTP1 0.39, RARG 0.39 |
| Q9 | 4 | 4 | SLC28A3 0.71, GSTP1 0.56, RARG 0.56 |
| Q10 | 5 | 0 | CYBA 0.62, ERCC1 0.62, BAX 0.26 |

## Caveats

- The benchmark labels come from ClinPGx, and the system also retrieves from ClinPGx, so calibration is partly self-consistent by construction. It is still informative for the `negative` and `disputed` classes, where the system must *disagree* with what its own retrieval surfaces, and for the literature-derived component of every score.
- `ClinPGx-valid %` from the earlier phase comparison is retired as a quality metric: it marks uncurated literature findings as wrong, which is the opposite of the goal here.
