# Auditing the Evidence: Provenance-Preserving Integration of Curated and Literature Knowledge for Pharmacogenomic Adverse Drug Reactions

*(Phase 14 revision. Every number in this draft was re-verified against the repository's code and cached outputs; see `claim_evidence_audit.md` for the audit and `evaluation_results_or_plan.md` for the supporting analyses.)*

## Abstract

Question-answering systems for drug safety must combine a curated knowledge base, the primary literature, and a language model — three resources that routinely disagree, and whose disagreements matter clinically. We extend AMG-RAG, a system that builds a per-question medical knowledge graph with an LLM, into an **evidence-auditing** pipeline for pharmacogenomic adverse drug reactions (ADRs). The pipeline preserves provenance from retrieval to answer: every claim about a gene–drug pair carries a typed reference (a curated ClinPGx row or a paragraph of a specific paper), claims are aggregated by a fixed scoring rule rather than by the model, and disagreements are classified into typed statuses with a heuristic that proposes the contextual axis — population, cancer type, dose, or endpoint — on which conflicting studies differ. Because retrieval is steered by the knowledge graph but not limited to it, the pipeline also identifies literature-supported candidate associations absent from its indexed knowledge-base snapshot; we audit each such candidate against its source and report the failure modes this audit revealed alongside the successes. On a benchmark of 72 gene–drug pairs with curator-derived labels, the evidence score separates supported from unsupported pairs (+0.351 mean difference; Spearman 0.721 over 52 surfaced pairs), while contradiction flagging shows high recall but low precision (0.95 / 0.47) — a result we report as a target for improvement. A manual re-adjudication of a false-premise probe shows that our earlier automatic scoring of it was unreliable in both directions, and that the fully audited configuration gives the most appropriate answer: it denies the unsupported link and redirects action to clinical risk factors. All inference runs on a single 20 GB GPU slice with an open 14B model; literature retrieval requires network access to NCBI. We release the scoring rules, audit scripts, and a controlled association-recovery task design.

---

## 1. Introduction

Pharmacogenomics knowledge is split across three resources. Curated databases such as ClinPGx/PharmGKB are reliable but lag the literature, because a curator must read and annotate a study before it exists there. The literature is current but conflicting: the same gene–drug association can be supported in children and refuted in adults, or supported for one endpoint and refuted for a stricter one. Language models compress both into parametric memory and extend them with plausible but uncited claims.

Most retrieval-augmented systems paste retrieved text into a prompt and let the model decide what to believe. For drug safety this is the wrong division of labor: the decisions that need to be trustworthy — which claims have support, how much, and where sources disagree — are exactly the ones a model makes opaquely. We take the opposite approach. The model extracts and explains; fixed rules score and adjudicate; and every claim keeps a reference that a reader can check.

We make three contributions:

1. **A provenance-preserving evidence-auditing pipeline** for open-ended ADR questions, built on AMG-RAG's per-question knowledge graphs. Retrieval spans a curated knowledge base and the literature (KB-cited abstracts, graph-conditioned search, and open-access full text digested to paragraph level); each resulting claim is typed, sourced, and aggregated per gene–drug pair by a deterministic scoring rule (Section 3). Contribution includes the measured dependence structure of these channels — they are *information channels*, not independent evidence, and we quantify where they overlap (Section 3.4).
2. **Typed disagreement analysis with contextual explanation.** Conflicting claims are resolved into one of five statuses; a comparability rule prevents mechanistic (cell-line/animal) evidence from counting against clinical associations, and a context-comparison heuristic proposes the axis on which conflicting clinical studies differ. On our development questions this recovered three documented splits in the ADR literature (endpoint, population, and cancer type) from the retrieved papers themselves (Section 4).
3. **Candidate identification beyond the indexed snapshot, with a full audit.** The pipeline flags gene–drug claims that human studies support but the indexed KB snapshot does not contain. We audit every flagged candidate from our runs against its source paper and report the outcome honestly: one verified variant-level candidate, one protein-biomarker finding mislabelled as pharmacogenomic, one endpoint mismatch combined with a drug-class normalization miss, and one outright extraction error (Section 5). We provide a controlled masked-association recovery task to evaluate this capability properly (Section 6.3).

We state explicitly what this paper does not claim: no biological discovery, no measured probability calibration, no general safety guarantee, and no controlled proof yet that the ledger improves answer accuracy over ordinary RAG on identical evidence — that comparison is designed and pending (Section 6.2).

## 2. System overview

The base system (AMG-RAG) builds a small knowledge graph per question — LLM entity extraction, pairwise relation extraction, chain-of-thought over graph paths — and was evaluated on multiple-choice medical QA. We adapted it to open-ended generation and added the components below. The LLM is Qwen2.5-14B-Instruct served locally on the allocated GPU; decoding is greedy (temperature 0); all stages use structured-output parsing.

**Information channels.** (1) An offline snapshot of ClinPGx/PharmGKB (bulk download dated 2026-07-05; we index `clinicalVariants.tsv` and `relationships.tsv`, the latter with 127,988 gene–chemical rows of which 33,100 are marked "not associated" and 20,032 "ambiguous"). (2) The PubMed abstracts those tables cite. (3) Live PubMed search whose queries are conjunctions built from knowledge-graph edges (a single term like *tinnitus* retrieves mostly unrelated recent papers; the edge-conjunction *tinnitus AND cisplatin AND hearing loss* is nearly unambiguous — on-topic retrieval rose from 20–23% to 49–65% across our configurations, by a keyword proxy). (4) PMC full text where open access allows, digested in bounded batches into per-paper structured records: genes supported/refuted, study type, direction, population, cancer type, endpoint, dose context, each with a paragraph-level reference such as `PMID:40342074/PMC12434574#p31`. (5) The model's parametric knowledge, which contributes entity descriptions, hypothesized graph edges, and search strategy.

**Role separation.** Channels 1–4 produce claims; channel 5 does not. We verified in code that ledger claims originate only from curated rows and paper digests; model-hypothesized edges steer search and path exploration but never enter the ledger. The model does, however, *extract* the structured fields the rules operate on, so extraction errors propagate (Section 5.3).

**Grounding effect.** Ungrounded baselines (the original architecture) name genes for cisplatin ototoxicity such as ABCC3, SLC15A4 and ATP7A; only 50–61% of their named genes have any curated row for that drug. Every KB-grounded configuration scores 94–95% on this proxy, and 100% of named genes appear in retrieved evidence. Caveats: n = 10 questions (9 for baselines), the proxy checks row existence rather than relationship correctness, and it is partly circular for configurations that retrieve from the same KB. Its clean interpretation is the baseline number: without grounding, roughly half of the named genes have no curated support at all.

## 3. Evidence scoring

### 3.1 Claims

Every assertion about a (gene, drug) pair becomes a typed record: stance (supports/refutes/inconclusive), study type, direction, phenotype, variant, context fields, source (`ClinPGx` or `PubMed`), and reference. Curated rows carry the curator's evidence level (1A–4) and association status.

### 3.2 The scoring rule

Scoring is a fixed function with no LLM involvement (implemented in `evidence_ledger.py`):

```
score = clip[0,1]( base · (1 + 0.18 · ln(1 + W_sup)) − 0.30 · ln(1 + W_ref) )
        × 0.9 if the curators mark the pair "ambiguous"
```

- **base** encodes the curated status: evidence level 1A→0.98, 1B→0.90, 2A→0.80, 2B→0.70, 3→0.55, 4→0.40; "associated" without a level → 0.55; "ambiguous" → 0.44; **no curated row → 0.25**; "not associated" → 0.15.
- **W_sup / W_ref** sum study-type weights over *distinct documents* (several paragraphs of one paper count once; the maximum weight per document is used): curated 1.0, meta-analysis 1.0, systematic review 0.95, GWAS 0.9, cohort/trial 0.85, case report 0.45, review 0.4, animal 0.3, in-vitro 0.2, unknown/missing 0.4.
- Labels: ≥0.75 high, ≥0.50 moderate, ≥0.25 low, else very-low.
- A pair with no curated row is flagged `uncurated_literature_claim` only if some supporting source has weight ≥ 0.8 (GWAS, cohort, trial, review-of-trials tier); otherwise `unsupported_claim`.

The rule operates on model-extracted fields; its guarantees are therefore conditional on extraction being correct. We separate these two failure sources in evaluation (Sections 5.3, 6.2).

### 3.3 Validation on curator-derived labels

We built a 72-pair benchmark by sampling `relationships.tsv` rows by their Association status: positive (associated; 23), negative (not associated; 24), disputed (ambiguous — the curators themselves found conflicting reports; 25). These labels are **curator-derived and machine-assembled**, not human annotations created for this project, and they share their origin with one input of the scoring rule, so this is in-development validation, not held-out performance. The label is never present in the question text.

Results (phase-11 configuration): the system surfaced the target pair for 65% / 67% / 84% of positive/negative/disputed items. Over surfaced pairs, mean scores order correctly — positive 0.42, disputed 0.35, negative 0.07; separation +0.351 (15 vs 16 pairs); Spearman(score, label order) 0.721 over 52 pairs. We use the term *evidence-score validation*: no probability calibration (reliability curves, Brier scores) has been measured.

The binary `disputed` flag reached **recall 0.95 but precision 0.47** (20 TP, 1 FN, 23 FP). The flag over-fires, mainly where weak or dependent literature triggers `curated_vs_literature` or `literature_internal`. We report this as a defect with a concrete repair path (require clinical-tier, lineage-independent sources before flagging; see `evaluation_results_or_plan.md` B4), not as a success.

### 3.4 Channel dependence, measured

The channels are not independent evidence, and the scoring rule has two known dependence effects, which we quantified on the final configuration's 145 ledger pairs:

1. The curated row contributes to both `base` and `W_sup` (53 of 145 pairs). Bounded effect: one weight-1.0 source multiplies base by 1 + 0.18·ln 2 ≈ 1.125, i.e. at most ~12.5% inflation.
2. A digested paper can be the same document a curated row cites: 2 of 96 document-deduplicated literature support sources were PMIDs the KB cites for the same pair.

Shared cohorts across distinct publications remain undetectable with our data and are acknowledged as unresolved. Scripts: `eval_lineage.py`.

## 4. Disagreement analysis

The ledger flags *that* sources disagree; a separate deterministic layer (`contradiction_layer.py`) classifies *why*. Claims are first grouped into comparability tiers — curated, clinical (meta-analysis, systematic review, GWAS, cohort, trial, case report), mechanistic (animal, in-vitro), narrative (reviews, unknown). Mechanistic results never count as contradicting clinical associations; they are attached as notes. Each (gene, drug) group with at least two comparable clinical sources is resolved to one status: CONSISTENT, CONFLICTING, CONTEXT-DEPENDENT, CURATED-LITERATURE CONFLICT, or INSUFFICIENT. For conflicting clinical claims, the layer compares context fields in a fixed order (population, cancer type, dose, endpoint) and, when the two sides' values do not overlap on some axis, reports that axis as a **possible explanation** of the disagreement. This is a heuristic: non-overlapping context values suggest the studies measured different things; they do not prove the conflict is resolved.

On the ten development questions the layer produced 145 cards: 120 INSUFFICIENT (83%), 22 CONFLICTING, 3 CONTEXT-DEPENDENT, 0 CONSISTENT, 0 CURATED-LITERATURE CONFLICT. The three contextual explanations match documented splits in those literatures — TPMT × cisplatin (endpoint: "hearing loss" vs "clinically significant hearing loss"), SLC28A3 × anthracyclines (population: children vs adults), GSTM1 × doxorubicin (cancer type) — and were recovered from the retrieved papers, not asserted from memory. The comparability rule also attached mechanistic-only notes to 29 cards; an earlier configuration had counted these as real contradictions, so the rule removes a measured inflation.

We report the layer's weaknesses with equal weight: 83% of pairs lack enough comparable evidence to classify; CONSISTENT is unreachable on this data because nearly all curated rows here are marked ambiguous, which routes to CONFLICTING first; 11 of 22 conflicts get no named axis, driven by uneven context extraction (endpoint 92%, direction 73%, population and cancer type ~51%, dose 30%); and no ground truth exists yet for axis-assignment accuracy.

## 5. Beyond the indexed snapshot: candidates, audited

### 5.1 Definitions

"Absent from the KB" needs precision. We distinguish: **D1** — the gene appears in neither indexed table; **D2** — no row links the gene to this drug (by literal name); **D3** — the pair exists but not for this phenotype or context. All claims below name their definition. All are relative to *our indexed snapshot* (2026-07-05; two tables), not to ClinPGx as a whole.

### 5.2 The audit

We audited every `uncurated_literature_claim` candidate that our earlier draft cited, against the cached digests and the snapshot tables:

- **KCNK17 × anthracycline cardiotoxicity — verified (D1).** Absent from both tables (0 rows). The digested systematic review (PMID:40413218/PMC12103300) reports variant rs2815063-A associated with left-ventricular ejection fraction effects in childhood cancer survivors. Qualifiers: the endpoint is LVEF change, related to but not identical with clinical cardiotoxicity, and the digest records the direction ambiguously.
- **CPVL and PIGR × doxorubicin — reclassified (D1, wrong evidence class).** Absent from both tables, endpoint matches, but the source cohort study (PMID:42657460) identifies them as **plasma proteins** — proteomic biomarkers, not inherited pharmacogenomic variants. Our claim schema had no field for this distinction; it does now appear as a limitation. The finding is real but belongs to a different evidence class than the pipeline claims to audit.
- **MLH1 and MSH3 × cisplatin — reclassified (fails D2 at class level; endpoint mismatch).** The supporting cohort paper (PMID:40342074) concerns cisplatin **kidney injury** — the digest itself notes it "does not directly address inner ear damage" — yet the pair surfaced in an ototoxicity question because aggregation is per (gene, drug) and drops the phenotype. Moreover the snapshot is not silent: `relationships.tsv` contains MLH1– and MSH3–**"Platinum compounds"** rows explicitly marked **"not associated"**, which our literal drug-name lookup missed. The honest classification is a *potential curated-vs-literature disagreement at drug-class granularity that the system failed to detect because it lacks alias/class normalization* — an instructive failure, not a candidate.
- **SLCO1B1 × cisplatin — removed (extraction error).** The digest's own summary states the cited paper concerns methotrexate and "does not directly address cisplatin-induced hearing loss." The supporting record misattributes the paper. (SLCO1B1 also has 664 relationship rows for other drugs, so at most D2 ever applied.)

The audit outcome is itself a result: of five headline candidates, one survives with qualifiers. The pipeline's value is that the audit was *possible* — every candidate carried a resolvable reference, so each error was found by reading one cited passage. Ordinary RAG output offers no equivalent handle.

### 5.3 What the failures teach

The three failure modes map to specific components: per-(gene, drug) aggregation discards phenotype (fix: aggregate per gene–drug–phenotype where extraction supplies it); literal drug-name matching misses curated class-level rows (fix: normalize drug classes and aliases at lookup); and digest extraction can misattribute papers or evidence classes (measure: the extraction-fidelity audit proposed in `evaluation_results_or_plan.md` B3). None of these was visible before the per-candidate audit.

## 6. Safety probing and pending evaluations

### 6.1 The false-premise probe, re-adjudicated

One development question asserts a CYP2D6*4–doxorubicin cardiotoxicity link that has no supporting row in the snapshot; a corrective note is injected into the context when the premise check fails (D2). Our earlier drafts scored this probe with regex patterns; a manual re-adjudication of all twelve configurations' cached answers (table in `evaluation_results_or_plan.md`) showed the automatic labels were wrong in both directions. Under manual reading: six configurations assert the false link; five deny it in one sentence while still endorsing the mechanism or recommending CYP2D6 screening; and the fully audited configuration (contradiction layer on) gives the most appropriate answer — it states that "the evidence does not support an established association", withholds CYP2D6-based recommendations, and redirects attention to clinical risk factors. Every configuration still opens by restating the premise sympathetically.

This is one probe: a diagnostic case, not a safety measurement. Database absence is also not proof of falsity — a limitation with particular force in a system built to surface uncurated associations; the premise gate fires only on pairs the KB actively lacks, and its note says "no curated support," not "false."

### 6.2 The pending controlled comparison

The central unanswered question is whether the ledger and cards change *answer quality* relative to ordinary RAG given identical evidence. Our configuration comparisons cannot answer it, because retrieval differs across configurations by design (the nearest controlled contrast, ledger off/on at fixed retrieval, changes only the reporting surface: 2–3 genes in prose become 116 scored pairs with flags). We designed a three-condition replay experiment — cached evidence, identical model and questions; plain-context RAG vs ledger vs ledger+cards — with claim-support and compliance metrics; it requires ~30 inference calls and is specified, with its runner plan, in `evaluation_results_or_plan.md` B1. No results are claimed here.

### 6.3 Controlled association recovery

To evaluate recovery beyond the graph without conflating it with biological novelty, we provide a masked-association task (`make_masked_recovery.py`): remove selected well-curated pairs from the KB copies, keep the literature reachable, and test whether the pipeline resurfaces the masked pairs as uncurated candidates with resolving citations — comparing against ordinary RAG on the same questions. Design and script are released; the experiment is pending.

## 7. Limitations

Development questions number ten, without gold answers; all phase-level numbers are descriptive. The evidence-score validation uses curator-derived labels that share provenance with a scorer input; surfacing recall (65–84%) precedes all score metrics; whether the benchmark influenced weight tuning is not recorded. Contradiction flagging has precision 0.47. The scoring rule consumes model-extracted fields; extraction fidelity is only spot-checked, and one audited candidate was an outright extraction error. Aggregation drops phenotype; drug-class rows escape literal matching. Keyword-based on-topic and validity metrics are imperfect proxies in both directions. Inference is offline, but literature retrieval requires NCBI access. Related work on conflict-aware retrieval and KB evidence scoring has not yet been compared against primary sources; until then we make no priority claims.

## 8. Conclusion

We turned a knowledge-graph QA system into an evidence auditor for pharmacogenomic ADRs: typed provenance end to end, rule-based scoring with its dependence structure measured, typed disagreement analysis that proposes contextual explanations, and candidate identification beyond an explicitly specified KB snapshot. The strongest evidence for the approach is reflexive: the audit that this revision performed — which corrected our own candidate list, probe scores, and independence assumptions — was only possible because every claim in the system's output carries a reference that can be checked. That property, not any single score, is what we argue drug-safety QA systems need.

---

## Appendix A. Configuration history (development record)

Thirteen configurations were explored on the same ten questions, model, and code, differing in environment-variable settings that control retrieval and auditing. Headline counts (fuller tables in `PHASE_SCORECARD.md` and `adr_phase_evaluation.md`): KB-only retrieval yields 8.5 refs/question and no literature; adding KB-cited abstracts yields 22.6; free LLM-chosen search maximizes volume but drops on-topic precision to 20–23%; edge-conjunctive search raises it to 49–65%; the digest/ledger configurations read 6–17 full-text papers per run and keep 41–70 question-relevant paragraphs; the final configuration's ledger holds 145 scored pairs of which 87 carry a dispute flag. Composite rankings under research-weighted and safety-weighted schemes appear in `PHASE_SCORECARD.md`; the weights are judgment calls, and the two schemes rank different configurations first, so we do not headline them.

## Appendix B. GenMedGPT-5k pilot (development note)

The open-ended adaptation was first exercised on GenMedGPT-5k (5,452 converted items). A 73-item pilot in fully offline mode (graph from question text alone, no retrieval) scored mean rescaled BERTScore F1 0.20 against reference replies — a system-level ablation of the base architecture's reasoning scaffold, not a reproduction of its published results, and not comparable to the ADR experiments.

## Appendix C. Reproducibility

Each configuration is one SLURM script; the KB snapshot is dated inside the dataset (`CREATED_2026-07-05`); every answer's `references` and `evidence_log` are persisted in the results JSONL; `eval_lineage.py`, `eval_ledger.py`, `eval_adr_phases.py`, and `score_phases.py` regenerate the reported analyses from those files. The scoring rule's constants appear in Section 3.2 and in `evidence_ledger.py`.
