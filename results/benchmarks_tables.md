# Benchmark tables (generated 2026-10-26 22:35)

## PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl)

| metric | llm_only | amg_rag | phase15 | medrag | imedrag | paperqa2 | paperqa2_fixed | lightrag | gpt4o | gpt4turbo | llama3_70b | gpt35 | gemini | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| consult:BERTScore-F1 | 0.165 | 0.128 | 0.171 | 0.105 | 0.179 | 0.139 | 0.167 | 0.074 | - | - | - | - | - | 9 |
| d2g:F1 | 0.367 | 0.333 | 0.701 | 0.483 | 0.542 | 0.528 | 0.589 | 0.387 | 0.733 | 0.607 | 0.656 | 0.424 | 0.370 | 20 |
| d2g:P | 0.350 | 0.300 | 0.689 | 0.500 | 0.542 | 0.504 | 0.543 | 0.296 | 0.725 | 0.592 | 0.617 | 0.339 | 0.321 | 20 |
| d2g:R | 0.400 | 0.400 | 0.850 | 0.475 | 0.575 | 0.625 | 0.775 | 0.600 | 0.775 | 0.700 | 0.800 | 0.700 | 0.500 | 20 |
| g2d:F1 | 0.108 | 0.155 | 0.576 | 0.070 | 0.322 | 0.230 | 0.535 | 0.340 | 0.572 | 0.444 | 0.541 | 0.186 | 0.077 | 20 |
| g2d:P | 0.150 | 0.250 | 0.711 | 0.100 | 0.425 | 0.325 | 0.667 | 0.372 | 0.603 | 0.453 | 0.561 | 0.172 | 0.076 | 20 |
| g2d:R | 0.104 | 0.138 | 0.600 | 0.062 | 0.316 | 0.206 | 0.516 | 0.348 | 0.610 | 0.562 | 0.617 | 0.258 | 0.083 | 20 |
| refusal(misspecified):extended | 0.571 | 0.571 | 0.429 | 0.857 | 0.714 | 0.857 | 0.714 | 0.857 | 1.000 | 1.000 | 0.429 | 0.857 | 0.286 | 7 |
| refusal(misspecified):pgxqa | 0.286 | 0.286 | 0.143 | 0.857 | 0.714 | 0.286 | 0.286 | 0.857 | 1.000 | 1.000 | 0.429 | 0.857 | 0.286 | 7 |
| refusal(well-specified):extended | 0.325 | 0.475 | 0.125 | 0.850 | 0.500 | 0.550 | 0.250 | 0.575 | 0.200 | 0.325 | 0.050 | 0.575 | 0.150 | 40 |
| refusal(well-specified):pgxqa | 0.275 | 0.375 | 0.050 | 0.850 | 0.500 | 0.300 | 0.225 | 0.575 | 0.200 | 0.325 | 0.050 | 0.575 | 0.150 | 40 |
| refusal_d2g:F1 | 0.470 | 0.335 | 0.591 | 0.193 | 0.493 | 0.487 | 0.682 | 0.455 | 0.759 | 0.465 | 0.641 | 0.351 | 0.252 | 18 |
| refusal_d2g:P | 0.435 | 0.292 | 0.550 | 0.194 | 0.486 | 0.444 | 0.625 | 0.373 | 0.731 | 0.449 | 0.606 | 0.281 | 0.275 | 18 |
| refusal_d2g:R | 0.565 | 0.481 | 0.787 | 0.231 | 0.537 | 0.611 | 0.898 | 0.694 | 0.833 | 0.565 | 0.787 | 0.667 | 0.306 | 18 |

## Masked-association recovery (E1)

| system | gene | drug | proposed | via | queried_round | in_digest | in_ledger | candidate | confidence | in_answer | in_risk_genes | in_candidate_genes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| phase15 | ACYP2 | cisplatin | True | A | 1 | True | True | True | 0.54 | True | True | False |
| phase15 | TPMT | cisplatin | False |  |  | True | True | True | 0.28 | True | True | False |
| phase15 | COMT | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase15 | GSTP1 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase15 | ABCC3 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase15 | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase15 | SLC28A3 | doxorubicin | False |  |  | True | True | True | 0.38 | False | False | True |
| phase15 | RARG | doxorubicin | False |  |  | True | True | True | 0.54 | True | False | True |
| phase15 | UGT1A6 | doxorubicin | False |  |  | True | True | True | 0.28 | True | False | True |
| phase15 | CBR3 | doxorubicin | False |  |  | True | True | True | 0.09 | False | False | False |
| phase13 | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase13 | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase13 | COMT | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase13 | GSTP1 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase13 | ABCC3 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase13 | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase13 | SLC28A3 | doxorubicin | False |  |  | True | True | False | 0.07 | False | False | False |
| phase13 | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| phase13 | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| phase13 | CBR3 | doxorubicin | False |  |  | True | True | False | 0.07 | False | False | False |
| llm_only | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| llm_only | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| llm_only | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| llm_only | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | ACYP2 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | TPMT | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | RARG | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | ACYP2 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | TPMT | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | RARG | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| lightrag | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | ABCC3 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| lightrag | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| lightrag | RARG | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| lightrag | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| lightrag | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |

## Recovery rates
| system | n | proposed | in digest | in ledger | candidate | in answer | in risk/candidate genes |
|---|---|---|---|---|---|---|---|
| phase15 | 10 | 10% | 90% | 90% | 90% | 40% | 50% |
| phase13 | 10 | 0% | 50% | 50% | 30% | 0% | 0% |
| llm_only | 10 | 0% | 0% | 0% | 0% | 0% | 0% |
| medrag | 10 | 0% | 0% | 0% | 0% | 0% | 0% |
| imedrag | 10 | 0% | 0% | 0% | 0% | 0% | 0% |
| paperqa2 | 10 | 0% | 0% | 0% | 0% | 40% | 0% |
| paperqa2_fixed | 10 | 0% | 0% | 0% | 0% | 50% | 0% |
| lightrag | 10 | 0% | 0% | 0% | 0% | 40% | 0% |

## PGxCorpus extraction

| metric | pgxcorpus_llm.jsonl | pgxcorpus_dict.jsonl |
|---|---|---|
| drug:F1 | 0.818 | 0.492 |
| drug:P | 0.914 | 0.546 |
| drug:R | 0.776 | 0.468 |
| drug:microF1 | 0.807 | 0.609 |
| gene[all]:F1 | 0.599 | 0.426 |
| gene[all]:P | 0.657 | 0.486 |
| gene[all]:R | 0.573 | 0.400 |
| gene[all]:microF1 | 0.645 | 0.532 |
| gene[symbols]:F1 | 0.692 | 0.510 |
| gene[symbols]:P | 0.714 | 0.542 |
| gene[symbols]:R | 0.684 | 0.495 |
| gene[symbols]:microF1 | 0.769 | 0.649 |
| n | 874 | 874 |
