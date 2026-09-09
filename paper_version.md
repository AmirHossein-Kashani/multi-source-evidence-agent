# Auditing Evidence for Pharmacogenomic Adverse Drug Reactions

## Abstract

Pharmacogenomic question answering requires combining curated gene–drug associations with research findings that may differ across populations and clinical outcomes. Reliable synthesis therefore requires traceable claims and explicit treatment of disagreement. We present an evidence-auditing framework that extends AMG-RAG to open-ended questions about adverse drug reactions. The framework integrates ClinPGx records with biomedical literature, links claims to source records or passages, and combines evidence through a fixed scoring rule. It also classifies disagreements and identifies differences in study context that may explain conflicting findings. We characterize the framework using Qwen2.5-14B-Instruct on ten development questions and a benchmark of 72 gene–drug pairs. In a development analysis using curator-derived labels that also inform the scorer, scores for the 52 reported target pairs correlate with the ordered labels at Spearman ρ = 0.721. Contradiction flagging achieves 0.95 recall among reported disputed pairs and 0.47 precision. Across the development questions, the framework identifies three possible contextual explanations for disagreement, while 83% of evaluated pairs lack sufficient comparable clinical evidence. Inspection of candidate associations reveals errors involving phenotype mismatch, drug-class matching, confusion between genetic and protein-biomarker evidence, and incorrect attribution. These findings show how explicit evidence records support inspection of pharmacogenomic answers and identify concrete limitations in extraction, evidence aggregation, and database matching.

## 1. Introduction

Pharmacogenomic evidence is available in curated databases and research papers. Curated resources such as ClinPGx/PharmGKB organize findings and summarize their evidence. New findings may appear in the literature before they are added to these resources. However, studies can reach different conclusions. A gene–drug association may be reported in children but not in adults, or for one outcome but not for a more narrowly defined outcome.

Language models can help retrieve and explain this information. They can also introduce unsupported claims or overlook differences between studies. In retrieval-augmented generation (RAG), the final answer often depends on how the model interprets the supplied evidence. This makes it important to record which sources support a claim and how disagreements are handled.

We extend AMG-RAG to make these decisions easier to inspect. The model extracts information from papers and generates the explanation. Fixed rules combine evidence and classify disagreements. Each claim retains a reference to its source. We call this process evidence auditing: readers can examine the evidence behind an answer and identify errors in how it was used.

We make three contributions:

**An evidence-auditing pipeline for open-ended ADR questions.** The pipeline combines curated records, cited abstracts, literature search, and open-access full text. It records the source of each claim and scores evidence for each gene–drug pair. We also measure overlap between information channels, because different channels may contain the same underlying evidence.

**A rule-based method for analyzing disagreements.** The method separates clinical and mechanistic evidence. It assigns one of five statuses to each gene–drug pair and identifies contextual differences that may help explain conflicting clinical findings. On our development questions, it identified differences in endpoint, population, and cancer type.

**An audit of candidates absent from the indexed database.** We examined the examples highlighted in earlier drafts. The audit exposed errors involving evidence type, phenotype, drug-class matching, and information extraction. We also designed a task that tests whether the system can recover known associations after they are removed from the indexed graph.

The current study evaluates the pipeline's behavior and documents its errors. It does not establish biological discovery, calibrated probabilities, or a general safety guarantee. Whether the ledger improves answer quality over ordinary RAG using the same evidence remains an open question. Section 6 describes the planned comparison.

## 2. System overview

AMG-RAG builds a small medical knowledge graph for each question. The model extracts entities, infers relations between them, and reasons over graph paths. The original system was evaluated on multiple-choice medical questions. We adapted it to generate open-ended answers and added evidence scoring, disagreement analysis, and source tracking.

The language model is Qwen2.5-14B-Instruct. It runs locally with greedy decoding at temperature 0. All stages use structured-output parsers.

### 2.1 Information channels

The pipeline uses five information channels:

| Channel | Role |
|---|---|
| ClinPGx/PharmGKB snapshot | Supplies curated gene–drug records and their association status. |
| Abstracts cited by the database | Provides access to papers linked to curated records. |
| Live PubMed search | Retrieves additional papers using queries based on graph relationships. |
| PMC full text | Provides passages containing study methods, outcomes, and subgroup details. |
| Model knowledge | Helps describe entities, propose graph edges, and plan searches. |

The database snapshot is dated July 5, 2026. We index clinicalVariants.tsv and relationships.tsv. The latter contains 127,988 gene–chemical rows, including 33,100 marked "not associated" and 20,032 marked "ambiguous."

Search queries combine terms from graph relationships. For example, *tinnitus AND cisplatin AND hearing loss* narrows the search compared with *tinnitus* alone. Across development configurations, a keyword-based measure of on-topic retrieval increased from 20–23% to 49–65%. This measure is an imperfect relevance proxy.

Where open-access full text is available, the system processes papers in bounded batches. It extracts the genes supported or refuted, study type, effect direction, population, cancer type, endpoint, and dose context. Relevant passages receive paragraph-level references, such as PMID:40342074/PMC12434574#p31.

### 2.2 Separating search hypotheses from evidence

Only curated records and extracted paper findings enter the evidence ledger. Model-generated graph edges guide search and graph traversal but do not count as evidence. This distinction is implemented in the code.

The model still extracts the fields used by the scoring rules. An extraction error can therefore affect the ledger even when the scoring calculation is deterministic. Section 5 shows examples of this problem.

### 2.3 Matching answer genes to curated records

In the ungrounded baselines, 50–61% of genes named in the answers had a curated row for the relevant drug. Examples named for cisplatin ototoxicity included ABCC3, SLC15A4, and ATP7A. The database-grounded configurations scored 94–95% on this measure, and all named genes appeared in retrieved evidence.

These results require a narrow interpretation. The grounded configurations used ten questions, while the baselines used nine. The measure checks whether a row exists; it does not check whether that row supports the exact claimed relationship. It is also partly circular because the grounded configurations retrieve from the database used for evaluation. The result shows increased agreement with the indexed records, rather than establishing biological correctness.

## 3. Evidence scoring

### 3.1 Claim records

Each claim concerns a gene–drug pair. Its record includes the stance—supporting, refuting, or inconclusive—along with the study type, effect direction, phenotype, variant, contextual fields, source, and reference. Curated records also include an association status and an evidence level where available.

Although individual records contain phenotype information, the current scorer aggregates them by gene–drug pair. Section 5 describes an error caused by losing this distinction during aggregation.

### 3.2 Scoring rule

The scorer is implemented in evidence_ledger.py. It combines a base value with weighted supporting and refuting evidence:

```
score = clip(
    base × (1 + 0.18 × ln(1 + W_sup))
    − 0.30 × ln(1 + W_ref),
    0, 1
)

If the curated status is ambiguous:
    score = 0.9 × score
```

The base value depends on the curated evidence level or association status:

| Curated evidence or status | Base value |
|---|---|
| Level 1A | 0.98 |
| Level 1B | 0.90 |
| Level 2A | 0.80 |
| Level 2B | 0.70 |
| Level 3 | 0.55 |
| Level 4 | 0.40 |
| Associated, without an evidence level | 0.55 |
| Ambiguous | 0.44 |
| No curated row | 0.25 |
| Not associated | 0.15 |

W_sup and W_ref are the sums of document weights for supporting and refuting evidence. Several paragraphs from the same paper count as one document, using the maximum applicable weight.

| Evidence type | Weight |
|---|---|
| Curated record | 1.00 |
| Meta-analysis | 1.00 |
| Systematic review | 0.95 |
| Genome-wide association study (GWAS) | 0.90 |
| Cohort study or trial | 0.85 |
| Case report | 0.45 |
| Narrative review | 0.40 |
| Animal study | 0.30 |
| In-vitro study | 0.20 |
| Unknown or missing study type | 0.40 |

Scores of at least 0.75 are labelled high. Scores from 0.50 to below 0.75 are moderate, and scores from 0.25 to below 0.50 are low. Lower scores are very low.

A pair with no curated row receives the flag uncurated_literature_claim if at least one supporting source has a weight of 0.8 or higher. Otherwise, it receives unsupported_claim. These flags describe the system's evidence assessment. Their reliability depends on correct extraction and matching.

### 3.3 Validation with curator-derived labels

We assembled a benchmark of 72 gene–drug pairs by sampling rows from relationships.tsv. The labels came from the table's association status: 23 positive pairs, 24 negative pairs, and 25 disputed pairs. Positive, negative, and disputed correspond to "associated," "not associated," and "ambiguous," respectively.

These labels were assembled automatically from curator-provided data. They were not newly created human annotations. They also share a source with an input to the scoring rule. We therefore treat this analysis as development-stage validation. Excluding the labels from question text does not remove that dependence.

In the phase-11 configuration, the system reported 52 of the 72 target pairs:

| Benchmark class | Total pairs | Target pairs reported | Reporting rate | Mean score among reported pairs |
|---|---|---|---|---|
| Positive | 23 | 15 | 65% | 0.42 |
| Negative | 24 | 16 | 67% | 0.07 |
| Disputed | 25 | 21 | 84% | 0.35 |

Among reported pairs, the mean score difference between positive and negative cases was 0.351. Spearman correlation between scores and ordered labels was 0.721 across the 52 reported pairs. These results describe score separation and ranking. Probability calibration has not been measured.

The binary disputed flag produced 20 true positives, one false negative, and 23 false positives among reported pairs. Recall within the reported disputed pairs was 0.95, while precision was 0.47. This recall does not include the four disputed target pairs that the system did not report.

The flag therefore identifies many disputed cases but also generates many false alarms. Weak or dependent literature often triggers the curated_vs_literature or literature_internal flags. One proposed improvement is to require comparable clinical evidence from independent underlying studies. This proposal is described in Section B4 of evaluation_results_or_plan.md and has not yet been established as an effective repair.

### 3.4 Dependence between information channels

Different channels can contain the same evidence. We examined two forms of dependence in the final configuration's 145 ledger pairs.

First, a curated row can contribute to both base and W_sup. This occurred in 53 pairs. When no other supporting weight is present, adding one weight-1.0 source changes the base multiplier from 1 to 1 + 0.18 × ln(2), or approximately 1.125. The 12.5% change applies to this multiplier. It is not a bound on the relative increase in the final score after refutation penalties.

Second, a paper in the ledger can also be cited by a curated row for the same pair. Among 96 literature support sources remaining after document deduplication, two had this overlap.

We cannot identify shared cohorts across different publications with the current data. Their dependence remains unresolved. The analysis is implemented in eval_lineage.py.

## 4. Disagreement analysis

The evidence ledger flags disagreements. A separate component, implemented in contradiction_layer.py, classifies them and looks for contextual differences that may help explain them.

The component groups evidence into four tiers:

| Tier | Evidence types |
|---|---|
| Curated | Database records |
| Clinical | Meta-analyses, systematic reviews, GWAS, cohorts, trials, and case reports |
| Mechanistic | Animal and in-vitro studies |
| Narrative | Other reviews and evidence with an unknown study type |

Under the current comparability rule, mechanistic findings are recorded as notes rather than counted as direct contradictions of clinical associations. This is a design choice intended to separate different kinds of evidence.

Each gene–drug pair receives a status: CONSISTENT, CONFLICTING, CONTEXT-DEPENDENT, CURATED-LITERATURE CONFLICT, or INSUFFICIENT. The method requires at least two comparable clinical sources for its clinical comparison. Pairs with too little comparable evidence are labelled INSUFFICIENT.

For conflicting clinical claims, the component compares population, cancer type, dose, and endpoint, in that order. If supporting and refuting claims have non-overlapping values on an axis, it reports that difference as a possible explanation. This heuristic identifies differences between studies; it does not prove that those differences explain the conflicting findings.

Across the ten development questions, the component produced 145 disagreement cards:

| Status | Number of cards |
|---|---|
| INSUFFICIENT | 120 |
| CONFLICTING | 22 |
| CONTEXT-DEPENDENT | 3 |
| CONSISTENT | 0 |
| CURATED-LITERATURE CONFLICT | 0 |

The three context-dependent cases concerned TPMT and cisplatin, SLC28A3 and anthracyclines, and GSTM1 and doxorubicin. The extracted differences were endpoint, population, and cancer type, respectively. For TPMT, the distinction was between hearing loss and clinically significant hearing loss. For SLC28A3, it was between children and adults. These explanations were generated from fields extracted from the retrieved papers.

The component also attached mechanistic-only notes to 29 cards. An earlier configuration had counted these findings as direct contradictions. The revised rule separates them from clinical disagreements.

Several limitations remain. Most pairs—120 of 145, or 83%—lack enough comparable evidence. The current rule ordering prevents a CONSISTENT result on these data because nearly all relevant curated rows are ambiguous and are routed to CONFLICTING first. Eleven of the 22 conflicting cases have no named contextual axis. Reported extraction rates vary by field: 92% for endpoint, 73% for direction, approximately 51% for population and cancer type, and 30% for dose. We do not yet have ground-truth labels for the accuracy of the proposed contextual explanations.

## 5. Auditing candidates outside the indexed database

### 5.1 Defining database absence

We distinguish three forms of absence:

| Definition | Meaning |
|---|---|
| D1: gene absent | The gene appears in neither indexed table. |
| D2: gene–drug pair absent | No row links the gene to the drug using literal name matching. |
| D3: context absent | The pair exists, but not for the relevant phenotype or context. |

These definitions apply to the two indexed tables in our July 5, 2026 snapshot. They do not establish absence from ClinPGx as a whole.

### 5.2 Candidate audit

We reviewed the candidate examples highlighted in earlier drafts using their cached paper digests and the indexed tables. The examples below show why database absence and citation presence are insufficient to establish a valid pharmacogenomic claim.

**KCNK17 and anthracycline cardiotoxicity: retained with qualifications.** KCNK17 was absent from both indexed tables, satisfying D1. The digest of a systematic review (PMID:40413218/PMC12103300) reports an association involving variant rs2815063-A and left-ventricular ejection fraction in childhood cancer survivors. The specific endpoint is a change in ejection fraction, which is related to but not identical with clinical cardiotoxicity. The digest also records the effect direction ambiguously. We retain this candidate with those qualifications.

**CPVL and PIGR with doxorubicin: reclassified as protein biomarkers.** Both genes were absent from the indexed tables, satisfying D1. However, the cited cohort study (PMID:42657460) identifies plasma proteins rather than inherited genetic variants. Although the reported endpoint matches the cardiotoxicity question, the evidence belongs to proteomics rather than the pharmacogenomic evidence class considered here. The claim schema lacked a field to distinguish these types of findings.

**MLH1 and MSH3 with cisplatin: endpoint mismatch and missed drug-class records.** The supporting cohort paper (PMID:40342074) concerns kidney injury. Its digest explicitly states that it does not directly address inner-ear damage. Nevertheless, the associations appeared in an ototoxicity answer because the ledger aggregated evidence by gene and drug without preserving phenotype.

The database lookup also missed relevant class-level records. The snapshot contains MLH1–"Platinum compounds" and MSH3–"Platinum compounds" rows marked "not associated." Literal matching against cisplatin did not find them. These cases therefore require comparison at both phenotype and drug-class level. They may represent a curated–literature disagreement, but the available matching procedure cannot establish that interpretation. We do not retain them as uncurated candidates.

**SLCO1B1 and cisplatin: removed because of an extraction error.** The digest states that the cited paper concerns methotrexate and does not directly address cisplatin-induced hearing loss. The supporting record nevertheless attributes the finding to cisplatin. SLCO1B1 also appears in 664 relationship rows for other drugs, so gene-level absence, D1, does not apply. We removed this candidate.

Among these grouped examples, only KCNK17 remains a candidate, subject to the qualifications above. The audit demonstrates the practical value of retaining source references: errors in the extracted claim can be traced to the corresponding evidence record. It does not yet establish an advantage over another RAG system that also provides checkable citations.

### 5.3 Implications for the pipeline

The audit identifies three areas for improvement. First, aggregation should preserve phenotype where it is available, so evidence about kidney injury is not merged into a claim about hearing loss. Second, database lookup should account for aliases and drug classes. A class-level match must still be checked for relevance to the specific claim. Third, extraction should distinguish inherited variants from expression or protein-biomarker findings and verify that the paper concerns the claimed drug and endpoint.

These changes require evaluation. Section B3 of evaluation_results_or_plan.md describes a proposed extraction-fidelity audit. The current examples identify failure modes but do not measure their frequency across the full set of outputs.

## 6. Diagnostic probing and planned evaluations

### 6.1 Reassessing a question with an unsupported premise

One development question asserts a link between CYP2D6*4 and doxorubicin cardiotoxicity. The indexed snapshot contains no supporting row for this pair. When the premise check finds no matching curated support, the system adds a corrective note to the context.

Earlier drafts evaluated this question using regular-expression patterns. A subsequent reassessment of cached answers from twelve configurations found mistakes in both directions: the automatic evaluator sometimes accepted problematic answers and sometimes rejected appropriate ones. The detailed judgments are recorded in evaluation_results_or_plan.md.

In that reassessment, six configurations asserted the proposed link. Five denied it in one sentence but still endorsed the mechanism or recommended CYP2D6 screening. One configuration, with the contradiction layer enabled, stated that the evidence did not support an established association. It also withheld CYP2D6-based recommendations and discussed clinical risk factors instead. All twelve answers began by sympathetically restating the question's premise.

This is a single diagnostic case. It does not measure general safety. Absence from the indexed database also does not prove that an association is false. The premise-check note therefore reports a lack of curated support. This distinction matters because the pipeline is also intended to identify associations outside the database.

### 6.2 Comparing answer quality with the same evidence

The central unanswered question is whether the ledger and disagreement cards improve answers when the evidence is held constant. The development configurations cannot establish this because their retrieval procedures differ.

The nearest existing comparison keeps retrieval fixed while enabling or disabling the ledger. Its clearest change is in reporting: answers containing two or three genes become ledgers containing 116 scored pairs and associated flags. A larger reporting surface does not by itself demonstrate better answer quality.

We have designed a replay experiment using cached evidence, the same model, and the same questions. It compares three conditions: ordinary RAG with the evidence supplied as context, RAG with the ledger, and RAG with both the ledger and disagreement cards. The proposed measures assess claim support and compliance with evidence labels. The experiment requires approximately 30 inference calls. Section B1 of evaluation_results_or_plan.md describes the runner plan. The experiment has not yet been completed.

### 6.3 Recovering associations removed from the graph

We also designed a controlled association-recovery task, implemented in make_masked_recovery.py. Selected well-curated gene–drug pairs are removed from copies of the database, while their supporting literature remains accessible. The task tests whether the pipeline recovers these pairs as uncurated candidates with checkable citations. Ordinary RAG is evaluated on the same questions as a baseline.

This task measures recovery of known associations under controlled database absence. It does not measure biological discovery. The task design and script are provided, but the experiment remains pending.

## 7. Limitations

The main development set contains ten questions without gold answers. Configuration-level results are therefore descriptive. The ungrounded baselines use nine questions, which further limits direct comparison.

The 72-pair score benchmark uses curator-derived labels that share a source with a scoring input. It is not an independent held-out evaluation. The system reports only 65–84% of target pairs, depending on class, and the score metrics are conditional on those pairs being reported. The record does not establish whether this benchmark influenced weight selection. Contradiction precision is 0.47, and probability calibration has not been measured.

The scoring and disagreement rules depend on model-extracted information. Extraction fidelity has only been checked in selected examples. The audit found a misattributed association, lost phenotype information, missed drug-class records, and confusion between genetic and protein-biomarker evidence. The current disagreement rule also prevents a CONSISTENT classification on these data.

The keyword-based retrieval measure and the curated-row matching measure can produce both false positives and false negatives. Source references allow inspection, but they do not guarantee that the associated claims are correct. Shared cohorts across publications remain unresolved, and the supporting audit must distinguish checks of extracted digests from checks of original source passages.

Inference runs locally, while literature retrieval requires network access to NCBI. The controlled answer-quality and association-recovery experiments remain pending. A detailed comparison with primary work on conflict-aware retrieval and database evidence scoring also remains to be completed. We therefore make no claim to be the first system with these capabilities.

## 8. Conclusion

We extended a knowledge-graph question-answering system to support evidence auditing for pharmacogenomic ADRs. The pipeline links claims to source records, combines evidence with fixed scoring rules, and proposes contextual explanations for disagreements. It also identifies candidate associations absent from an explicitly defined database snapshot.

The audit revealed errors that were not apparent from citation presence alone. These included mismatched endpoints, missed drug-class records, an incorrect evidence type, and a misattributed association. Retaining source references allowed us to inspect and revise the affected claims.

The current results support further development of the auditing approach. They do not yet establish improved answer quality over ordinary RAG using the same evidence. The planned controlled experiments will test that question and assess whether the pipeline can reliably recover associations outside its indexed graph.

## Appendix A. Development configurations

Thirteen configurations were explored using the same question set, model, and code base. Environment variables controlled retrieval and auditing components. These runs form a development record rather than a controlled ablation of every component.

Database-only retrieval produced 8.5 references per question. Adding database-cited abstracts increased this to 22.6. Free-form search retrieved more papers but yielded only 20–23% on-topic results under the keyword proxy. Queries based on graph relationships achieved 49–65% across the relevant configurations.

Configurations with paper digestion and a ledger read 6–17 full-text papers per run and retained 41–70 relevant paragraphs. The final configuration contained 145 scored pairs, of which 87 carried a dispute flag.

Further counts are available in PHASE_SCORECARD.md and adr_phase_evaluation.md. The scorecard also includes composite rankings using research-oriented and safety-oriented weights. These weights reflect judgment choices and produce different rankings, so we do not use the composites as headline results.

## Appendix B. GenMedGPT-5k pilot

We first tested the open-ended adaptation using 5,452 converted GenMedGPT-5k items. A pilot run evaluated 73 items without retrieval. The graph was constructed from the question text alone. Mean rescaled BERTScore F1 against the reference replies was 0.20.

This pilot tests the reasoning scaffold without external retrieval. It is not a reproduction of the original system's published results and is not directly comparable with the ADR experiments.

## Appendix C. Reproducibility materials

Each configuration is defined by a SLURM script. The database snapshot carries the marker CREATED_2026-07-05. Each answer is stored in JSONL format with its references and evidence_log fields.

The analyses are implemented in eval_lineage.py, eval_ledger.py, eval_adr_phases.py, and score_phases.py. Section 3.2 states the scoring constants used in evidence_ledger.py. The files claim_evidence_audit.md and evaluation_results_or_plan.md document the reported audit and supporting analyses. Proposed evaluations are identified separately from completed results.

---

## Editorial notes for the authors — remove before submission

This document is a language revision of the supplied Phase 14 draft. The reported results have not been independently reproduced during this edit. References to repository files describe materials named in the source draft; those files were not supplied for this revision.

Shorter sentences, clearer transitions, standard Markdown, and simpler terminology replace the earlier dense formatting. The methodological limitations and pending-experiment status are retained.

The 0.95 contradiction recall is explicitly conditional on reported disputed pairs. The four unreported disputed pairs remain outside that denominator. If the intended end-to-end metric counts them as misses, report 20/25 = 0.80 separately; this is a calculation from the manuscript counts, not a new experiment.

The statement about 12.5% inflation now refers to the base multiplier. It no longer implies a bound on the relative change in the final score.

The phrase "five headline candidates" has been removed because the displayed examples contain four groups involving six gene–drug pairs. Confirm the intended counting unit before reporting a survival rate.

The candidate section follows the draft's stated audit inputs: cached digests and indexed tables. Confirm which judgments were also checked against original source passages. The retained KCNK17 example still needs an unambiguous effect direction and precise endpoint description.

The diagnostic-question section uses "reassessment" because the supplied draft does not identify the adjudicator. Add whether judgments came from a human, a model, or a combined process, along with the rubric and configuration IDs. Explain why twelve configurations were reassessed while the development history lists thirteen.

Confirm whether the reported context-extraction rates measure field availability or extraction accuracy. These are different quantities.

Complete the related-work section and bibliographic references before submission. The language edit does not supply or verify missing literature comparisons.
