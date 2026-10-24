# Benchmark tables (generated 2026-10-23 20:03; consult BERTScore from job 24891101)

## PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl)

| metric | llm_only | amg_rag | phase15 | n |
|---|---|---|---|---|
| d2g:F1 | 0.367 | 0.333 | 0.701 | 20 |
| d2g:P | 0.350 | 0.300 | 0.689 | 20 |
| d2g:R | 0.400 | 0.400 | 0.850 | 20 |
| g2d:F1 | 0.108 | 0.155 | 0.576 | 20 |
| g2d:P | 0.150 | 0.250 | 0.711 | 20 |
| g2d:R | 0.104 | 0.138 | 0.600 | 20 |
| refusal(misspecified):extended | 0.571 | 0.571 | 0.429 | 7 |
| refusal(misspecified):pgxqa | 0.286 | 0.286 | 0.143 | 7 |
| refusal(well-specified):extended | 0.325 | 0.475 | 0.125 | 40 |
| refusal(well-specified):pgxqa | 0.275 | 0.375 | 0.050 | 40 |
| refusal_d2g:F1 | 0.470 | 0.335 | 0.591 | 18 |
| refusal_d2g:P | 0.435 | 0.292 | 0.550 | 18 |
| refusal_d2g:R | 0.565 | 0.481 | 0.787 | 18 |
| consult:BERTScore-F1 | 0.165 | 0.128 | 0.171 | 9 |

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

## Recovery rates
| system | n | proposed | in digest | in ledger | candidate | in answer | in risk/candidate genes |
|---|---|---|---|---|---|---|---|
| phase15 | 10 | 10% | 90% | 90% | 90% | 40% | 50% |
| phase13 | 10 | 0% | 50% | 50% | 30% | 0% | 0% |
| llm_only | 10 | 0% | 0% | 0% | 0% | 0% | 0% |

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
