# AMG-RAG on PharmGKB/ADR — Query & Answer Analysis

Analysis of the AMG-RAG system's output on the **PharmGKB / ADR** pharmacogenomics dataset
(open-ended, "Framing 1" text-QA). This run is a 15-item validation slice (ids 0–14).

## Run configuration

| | |
|---|---|
| **Dataset** | PharmGKB `var_drug_ann.tsv` → `dataset/PharmGKB/pharmgkb.jsonl` (12,173 items); this slice = ids 0–14 |
| **Task** | Question templated from *variant + gene + drug*; gold reference = the curated `Sentence` (the true effect/direction lives **only** in the reference — no leakage) |
| **Model** | Qwen2.5-14B-Instruct (`qwen2.5:14b`, Ollama Q4_K_M) |
| **Serving** | Self-hosted Ollama on one H100 MIG `2g.20gb` (~20 GB) slice — no ngrok, fully local |
| **KG mode** | `AMG_USE_EXTERNAL=0` (offline): per-question graph built from the question text alone |
| **Answer style** | `AMG_ANSWER_STYLE=pgx` (terse factual pharmacogenomic statement) |
| **Metric** | BERTScore (roberta-large, rescaled) vs. the reference sentence |

## Aggregate result

| BERTScore | Mean | Median |
|---|---|---|
| Precision | 0.2447 | 0.2260 |
| Recall | 0.3704 | 0.3259 |
| **F1** | **0.3076** | **0.2741** |

All 15 items generated successfully (`ok=15, err=0`). The headline F1 of ~0.31 is modest —
the qualitative breakdown below explains why, and shows the number is being **dragged down by
hedging and up by a factually-wrong-but-lexically-similar answer.**

## Per-item breakdown

Verdict is a manual judgement of whether the model committed to the **correct effect direction**
(the pharmacologically meaningful content), independent of BERTScore.

| id | Variant → Drug | Gold effect | Model's stated effect | Verdict | F1 |
|---|---|---|---|:--:|--:|
| 0 | CYP3A4\*17 → nifedipine | decreased metabolism | decreased metabolism, ↑ plasma conc. | ✅ | 0.511 |
| 1 | rs2909451 (DPP4) → sitagliptin | decreased response | "differential effects" (unspecified) | ⚠️ | 0.222 |
| 2 | rs706795 (FAIM2) → SSRIs | increased response | "altered response" (unspecified) | ⚠️ | 0.091 |
| 3 | rs16918842 (OPRK1) → heroin | **not associated** (null) | fabricated "↑ addiction risk" | ❌ | 0.126 |
| 4 | CYP2C9\*3 → warfarin | decreased dose | decreased metabolism → lower dose | ✅ | 0.420 |
| 5 | rs2285676 (KCNJ11) → sitagliptin | increased response | "altered efficacy" (unspecified) | ⚠️ | 0.299 |
| 6 | CYP2C9\*11 → warfarin | decreased dose | decreased metabolism → lower dose | ✅ | 0.506 |
| 7 | rs163184 (KCNQ1) → sitagliptin | decreased response | "potentially altered efficacy" | ⚠️ | 0.233 |
| 8 | CYP2B6\*18 → efavirenz | increased concentrations | increased plasma concentrations | ✅ | 0.430 |
| 9 | CYP2C19\*2 → clomipramine | increased concentration | higher plasma levels | ✅ | 0.370 |
| 10 | rs7754840 (CDKAL1) → sitagliptin | increased response | "may influence efficacy" | ⚠️ | 0.274 |
| 11 | rs371194629 (HLA-G) → methotrexate | **not associated** (null) | fabricated "↑ adverse risk" | ❌ | 0.176 |
| 12 | rs4664443 (DPP4) → sitagliptin | decreased response | "altered response" (unspecified) | ⚠️ | 0.274 |
| 13 | CYP2D6\*1xN → codeine | **increased** metabolism | **decreased** metabolism (opposite) | ❌ | 0.533 |
| 14 | rs1799853 (CYP2C9) → sitagliptin | decreased response | "minimal impact" | ❌ | 0.150 |

**Tally: 5 correct · 6 hedged · 4 wrong.**

## Mean F1 by verdict category

| Verdict | n | Mean F1 |
|---|:--:|--:|
| ✅ Correct direction | 5 | **0.447** |
| ⚠️ Hedged (no direction) | 6 | 0.232 |
| ❌ Wrong | 4 | 0.246 *(0.150 excluding the deceptive item 13)* |

BERTScore separates correct (~0.45) from hedged (~0.23) reasonably well — **except** where a
wrong answer happens to reuse the reference's vocabulary (see item 13 below).

## Query analysis — what the questions demand

Every query has the same shape: *"What is the known pharmacogenomic effect of the {variant}
({gene}) variant on {drug}?"* Answering correctly requires one specific fact — the **direction**
of the effect (increased/decreased metabolism, dose, response, or a null association). This is a
**recall task**, not a reasoning task: the direction cannot be derived from the entity names; it
must be known. That framing is what exposes the system's core limitation below.

The questions split into two difficulty tiers:
- **Well-characterised pharmacogenes** (CYP3A4, CYP2C9, CYP2B6, CYP2C19, CYP2D6): canonical
  metabolism facts Qwen has seen in training → mostly answered correctly (items 0, 4, 6, 8, 9).
- **Obscure GWAS SNPs** (rs-IDs in DPP4, KCNJ11, KCNQ1, CDKAL1, FAIM2, HLA-G, OPRK1): niche
  efficacy findings the model has **not** memorised → hedged or fabricated (items 1, 2, 3, 5, 7,
  10, 11, 12, 14). Note almost all of these are `…→ sitagliptin` efficacy SNPs.

## Answer analysis — three behaviours

**1. Correct (5).** When the drug–gene pair is a textbook metabolism fact, the model commits to the
right direction and adds correct mechanism. Example (id 0):
> Gold: *"CYP3A4 \*17 is associated with decreased metabolism of nifedipine…"*
> Model: *"…decreased metabolism of nifedipine due to reduced expression and activity of the CYP3A4 enzyme, potentially increasing plasma concentrations…"* ✅

**2. Hedged (6).** For SNPs it doesn't know, the model preserves the correct entities but refuses to
commit to a direction, emitting filler like "differential effects" or "may influence efficacy."
Example (id 1):
> Gold: *"Genotype TT is associated with **decreased** response to sitagliptin…"*
> Model: *"…associated with **differential** pharmacogenomic effects on sitagliptin, **potentially** influencing drug response…"* ⚠️

**3. Wrong (4).** Two distinct error types:
- **Fabricated effect for a null result** (ids 3, 11). The reference says *"not associated,"* but
  the model can't infer a null finding from the question, so it invents a plausible risk.
  > id 3 — Gold: *"…**not** associated with dose of heroin…"* → Model: *"…associated with an **increased risk** of heroin use and adverse outcomes…"* ❌
- **Flipped direction** (id 13). `CYP2D6*1xN` is a gene **duplication** = ultra-rapid metaboliser =
  *increased* metabolism, but the model applied the generic "CYP2D6 variant ⇒ reduced function"
  prior and stated the **opposite**.
  > id 13 — Gold: *"…**increased** metabolism of codeine."* → Model: *"…**reduced** codeine metabolism…"* ❌

## Metric caveat — BERTScore ≠ factual correctness

**Item 13 is the highest-scoring answer in the whole run (F1 = 0.533) and is factually the most
dangerous** — it states the exact opposite of the truth. BERTScore rewards lexical/semantic
overlap ("CYP2D6\*1xN", "codeine", "metabolism", "adverse effects" all match the reference) and is
**blind to the flipped direction**. Conversely, a *correctly hedged* answer that shares little
vocabulary (id 2, F1 = 0.091) scores near the bottom. **Takeaway: for this directional task,
BERTScore should be read alongside a direction-accuracy check, not on its own.**

## Root cause

Both failure modes are direct consequences of the **offline knowledge-graph mode**. The per-question
graph is built from the question text alone (`CYP2D6*1xN`, `codeine` and their LLM-guessed relations),
so it contains **no evidence of the actual effect direction**. The system therefore falls back on the
generator's parametric memory — which is strong for canonical pharmacogenes and empty (→ hedge) or
mis-primed (→ flip) for everything else. The KG is currently decorative for this dataset: it supplies
entities, not the answer-bearing edges.

## Recommendations

1. **Ground the KG in the real PharmGKB triples.** Load `relationships.tsv` /
   `var_drug_ann.tsv` edges (`associated` / `not associated` / `increased` / `decreased`) into
   `MedicalKnowledgeGraph` so the answer-bearing fact is *retrieved*, not recalled. This directly
   targets all 10 hedged/wrong items — including the null-association fabrications (ids 3, 11),
   which only a real "not associated" edge can fix.
2. **Add a direction-accuracy metric.** Parse increased/decreased/not-associated from gold and
   candidate and report exact-match alongside BERTScore, so factually-inverted answers (id 13)
   are penalised instead of rewarded.
3. **Consider the MCQ framing** (predict the direction from a fixed option set) for a clean,
   leak-free accuracy number that is directly comparable to the AMG-RAG paper's MedQA results.
4. **Scale the evaluation** beyond 15 items once (1)–(2) are in, to get a stable F1 + accuracy over
   a larger, stratified slice (well-characterised genes vs. obscure SNPs).

---
*Generated from `results/pharmgkb_results.jsonl` and `results/pharmgkb_scores.csv` (job 18478947).*
