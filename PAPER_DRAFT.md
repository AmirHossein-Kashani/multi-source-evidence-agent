# Beyond the Curated Graph: Multi-Source Evidence Integration and Literature-Grounded Discovery for Pharmacogenomic Adverse Drug Reactions

## Abstract

Systems that answer pharmacogenomics questions usually rely on a single kind of knowledge: either a curated knowledge base, or retrieved literature, or the language model's own memory. We extend AMG-RAG (EMNLP 2025 Findings), a system that builds a per-question medical knowledge graph with an LLM, and we make two claims.

**Claim 1 — multi-source evidence integration.** Our system combines five distinct sources of information in a single answer — (1) curated ClinPGx/PharmGKB tables, (2) the PubMed abstracts those tables cite, (3) live literature search conditioned on knowledge-graph relationships, (4) PMC full-text articles read paragraph by paragraph, and (5) the model's parametric knowledge — and it keeps them distinguishable end to end. Every retrieved item carries a typed provenance tag; claims are aggregated per gene by a deterministic formula in which agreement *between independent sources* raises confidence and disagreement lowers it; and conflicts across sources are resolved into typed statuses, including a dedicated status for the case where curated knowledge and current literature disagree. On a fixed set of adverse-drug-reaction (ADR) questions, integration grows from 8.5 references per question (single source) to 23.8 references drawn from all source types, with 17 full-text papers read and 70 question-relevant paragraphs kept and individually cited.

**Claim 2 — finding what is not in the knowledge graph.** Because retrieval is steered by knowledge-graph *edges* but not limited to knowledge-graph *content*, the system surfaces gene–drug associations that have no row in the curated knowledge base at all. These are flagged `uncurated_literature_claim`, scored low-confidence by formula, and tied to a specific paragraph of a specific paper. On the ADR set this channel produced candidate genes such as MLH1 and MSH3 for cisplatin toxicity and CPVL and PIGR for doxorubicin cardiotoxicity — associations absent from all 12,000+ curated annotations we index, but supported by recent human cohort studies. The system therefore does more than retrieve what curators already know: it proposes vetted-format candidates *beyond* the curated graph while labelling them honestly as unconfirmed.

The mechanisms that make both claims auditable — paragraph-level provenance, a confidence formula benchmarked on 72 hand-labelled pairs (separation +0.351, Spearman ρ = 0.721, contradiction recall 0.95), typed contradiction resolution, false-premise gating, and a citation-constrained answer contract — run fully offline on a single 20 GB GPU slice with an open 14B model (Qwen2.5-14B). We evaluate through a 13-configuration ablation on fixed questions and report negative findings alongside positive ones, including a case where adding more retrieved literature degraded safety until retrieval was made relationship-aware.

---

## 1. Introduction

Pharmacogenomics knowledge lives in three places that do not agree with each other. Curated knowledge bases (ClinPGx/PharmGKB) are reliable but lag the literature by construction — a curator must read, judge, and annotate before an association exists there. The literature itself is current but contradictory: the same gene–drug association can be supported in children and refuted in adults, or supported for "hearing loss" and refuted for "clinically significant hearing loss." And large language models hold a compressed, uncited copy of both, which they will confidently extend with plausible inventions.

A question-answering system for drug safety has to work with all three, and the standard approaches each use only one well. KB-grounded systems cannot say anything the curators have not yet approved. Retrieval-augmented systems drown in off-topic papers and have no principled way to weigh a cell-line study against a human cohort. And LLM-only systems produce answers that look like pharmacogenomics but cannot be audited.

This paper is about doing both things at once, in one auditable pipeline:

- **integrating multiple sources of information** — curated tables, cited abstracts, live search, full-text articles, and model knowledge — with the provenance, weighting, and conflict handling that integration actually requires (Claim 1), and
- **finding associations beyond the curated knowledge graph** — surfacing literature-supported candidate genes that have no curated row anywhere, without letting the model invent uncited ones (Claim 2).

The tension between the two claims is the interesting part. A system that only trusts the curated graph can never discover; a system that freely goes beyond it will hallucinate. Our answer to that tension is architectural: **anything may steer the search, but only sourced evidence may enter a claim, and a deterministic formula — never the model — decides how much confidence each claim deserves.**

We build on AMG-RAG (arXiv:2502.13010), which constructs a per-question knowledge graph with an LLM and reasons over graph paths. Everything described below is an addition made by this work.

### Contributions

1. **A five-source evidence architecture** (Claim 1): curated ClinPGx tables, KB-cited PubMed abstracts, relationship-conditioned live PubMed search, PMC full text with paragraph-level digestion, and LLM parametric knowledge — each tagged with typed provenance (`ClinPGx:GENE/variant:L1A`, `PMID:x`, `PMID:x/PMCy#p12`, `LLM Analysis`) that survives from retrieval to the final answer.
2. **Cross-source aggregation by formula.** A deterministic per-gene evidence ledger weighs study types, rewards agreement between independent sources, penalizes disputes, and outputs calibrated confidence labels — benchmarked against 72 hand-labelled gene–drug pairs. The model never scores its own claims.
3. **Typed cross-source contradiction resolution**, including a dedicated CURATED-LITERATURE CONFLICT status and an explanation step that names the axis on which sources disagree (population, endpoint, cancer type, dose), demonstrated on three documented disagreements in the ADR literature.
4. **A discovery channel beyond the curated graph** (Claim 2): knowledge-graph edges generate conjunctive literature queries that are explicitly allowed to pursue promising *unconfirmed* leads; genes reported by retrieved human studies but absent from the curated tables enter the ledger flagged `uncurated_literature_claim`, at low confidence, with paragraph citations — candidate discoveries in a vetted format.
5. **Hallucination controls that make discovery safe**: false-premise gating (a corrective note when the question asserts a link the tables do not contain), a citation-constrained answer contract (every ledger gene reported with its confidence label and shown reference; unsupported links must be called unsupported; conflicting links may not be presented as established), greedy decoding, and a persisted per-answer evidence log that makes any uncited citation mechanically detectable.
6. **Open-ended adaptation and datasets**: a free-text answering path for the originally multiple-choice AMG-RAG; a leakage-controlled QA benchmark synthesized from 12,173 curated variant–drug annotations (the association's direction appears only in the hidden reference); and a 13-configuration ablation on fixed ADR questions with a deliberate false-premise probe.

---

## 2. Background: the base system

AMG-RAG answers a question in five LLM stages: entity extraction with relevance scores; pairwise relation extraction producing typed, confidence-scored edges; optional external evidence retrieval; entity summarization; and chain-of-thought reasoning over graph paths. The graph is rebuilt per question. The original system evaluates on multiple-choice benchmarks, uses the graph to *find* the answer, and treats retrieval as undifferentiated context: whatever is fetched is pasted into the prompt, and the model decides what to believe. Our work replaces that last property entirely.

---

## 3. Claim 1: integrating multiple sources of information

### 3.1 The five sources and their roles

| # | Source | What it contributes | Provenance tag | May be cited? |
|---|---|---|---|---|
| 1 | ClinPGx/PharmGKB tables (offline) | curated gene/variant–drug–phenotype rows with expert evidence levels 1A–4 | `ClinPGx:GENE/variant:L2B` | yes |
| 2 | KB-cited PubMed abstracts | the exact studies the curators based their rows on | `PMID:x` (`via: clinpgx_citation`) | yes |
| 3 | Relationship-conditioned live search | current literature, including work newer than the KB | `PMID:x` | yes |
| 4 | PMC full text (JATS XML; OA PDF fallback) | methods and subgroup details abstracts omit | `PMID:x/PMCy#p12` (paragraph-level) | yes |
| 5 | LLM parametric knowledge | entity descriptions, hypothesized graph edges, search strategy, mechanism narrative | `LLM Analysis` | **no** |

The design rule that makes this integration rather than accumulation: **sources 1–4 may support claims; source 5 may only steer.** LLM-hypothesized edges shape which paths are explored and which queries are issued, but a gene–drug association can only enter the evidence ledger with a row or a paper behind it.

### 3.2 Integration in the graph

The per-question knowledge graph is a hybrid of two sources kept explicitly apart. Curated rows matching the question's drug and phenotype are seeded as edges whose confidence derives from the curator's evidence level, oriented so that path exploration from question entities reaches the curated biomarkers. LLM relation extraction then runs only over LLM-extracted entities. Every edge records which source produced it, and the distinction survives to the answer.

### 3.3 Integration in retrieval

Sources 2–4 are reached through a single retrieval seam with per-source routing. The key lesson of our ablation is that *how* the literature source is queried decides whether integration helps or hurts. Single-entity queries chosen freely by the LLM (phases 6–7) retrieved the most papers but only 20–23% were on-topic, and — the serious finding — the flood of loosely related text caused a regression on our false-premise probe: with the corrective KB note still present in context, the model asserted a gene–drug link that does not exist. **More evidence from a second source made the answer less safe than one source alone.** Replacing free topics with conjunctive queries built from knowledge-graph edges (phase 9: *tinnitus AND cisplatin AND hearing loss* rather than *tinnitus*) raised on-topic retrieval to 54–65%, because a conjunction derived from an asserted relationship is nearly unambiguous. Full-text upgrading (source 4) then reads the retrieved papers in bounded batches, keeping only question-relevant paragraphs, each individually citable.

### 3.4 Integration in scoring: the evidence ledger

Every claim from sources 1–4 becomes a typed record: gene, drug, stance (supports/refutes), study type, direction, population, cancer type, endpoint, dose context, and its provenance ref. A deterministic scorer aggregates records per gene. Three properties are specifically *cross-source*:

- **Independent agreement raises confidence**: a curated row plus a concurring cohort study outranks either alone.
- **Study types are weighted**: a mechanistic (cell-line/animal) refutation cannot cancel a human cohort — an inflation we measured before fixing (29 of 145 pairs in the final configuration carry a mechanistic-only note that an earlier configuration counted as real contradictions).
- **Cross-source disagreement is a first-class outcome**: disputed pairs are flagged, and the contradiction layer assigns typed statuses including CURATED-LITERATURE CONFLICT (the KB and the literature disagree) and CONTEXT-DEPENDENT (the disagreement dissolves once population, endpoint, cancer type, or dose is fixed).

On 72 hand-labelled gene–drug pairs the formula separates supported from disputed claims by +0.351 mean confidence, correlates with labels at Spearman ρ = 0.721, and recalls 95% of contradicted pairs.

The resolution step recovered three documented cross-source disagreements from the papers themselves, naming the axis each time: TPMT × cisplatin (endpoint: "hearing loss" vs "clinically significant hearing loss"), SLC28A3 × anthracyclines (population: children vs adults), GSTM1 × doxorubicin (cancer type: ALL/lymphoma vs mixed).

### 3.5 What integration buys, measured

On ten fixed ADR questions with identical code and model, moving from one source to five changes the evidence profile from 8.5 references per question (curated only, zero literature) to 23.8 references per question spanning curated rows, cited abstracts, searched abstracts, and 17 full-text papers with 70 kept paragraphs — while gene validity against the curated KB stays at 94–95% throughout (versus 50–61% for the ungrounded baselines). Integration adds sources without diluting correctness, because correctness is enforced by the ledger, not by hoping the model weighs sources well.

---

## 4. Claim 2: finding what the knowledge graph does not contain

### 4.1 The discovery mechanism

The curated knowledge base is authoritative but incomplete by construction. Our second claim is that the system finds credible associations *beyond* it, through a chain with a guardrail at every link:

1. **The graph proposes.** Knowledge-graph edges — curated and LLM-hypothesized alike — feed a query-authoring chain that is explicitly instructed to include "promising leads in the retrieved evidence that are NOT yet confirmed." This is the sanctioned use of model creativity: choosing where to look.
2. **The literature answers.** Conjunctive PubMed queries retrieve papers, including work published after the KB's last curation pass; open-access full text is digested into per-paper structured findings (genes supported/refuted, study type, context fields).
3. **The ledger checks the KB.** For every gene a paper reports, the ledger looks for a curated row. If none exists anywhere in the 12,000+ indexed annotations, the claim is flagged **`uncurated_literature_claim`** — defined as "not in ClinPGx but backed by human studies — candidate novel finding."
4. **The formula caps the enthusiasm.** Uncurated claims score low (typically ~0.28, label `low`) because they lack the independent agreement that raises confidence. The answer contract then forces them to be reported *as* unconfirmed candidates, never as established facts.

### 4.2 What it found

On the ADR set this channel surfaced, among others:

| Candidate | Question context | Evidence behind it | In curated KB? |
|---|---|---|---|
| **MLH1**, **MSH3** | cisplatin toxicity | human cohort, `PMID:40342074/PMC12434574#p31` | no row for any drug |
| **CPVL**, **PIGR** | doxorubicin cardiotoxicity | human cohort, `PMID:42657460` | no |
| **SLCO1B1** | (thiopurine context) | systematic review, `PMID:40222694` | not for this pair |
| **KCNK17** | anthracycline cardiotoxicity | systematic review, `PMID:40413218/PMC12103300#p15` | no |

For contrast, the curators associate roughly 60 genes with cisplatin; MLH1 and MSH3 are in none of the indexed tables for any drug — yet a 2025 cohort study reports them, and the system carried them into the answer with the paragraph citation and a low-confidence label. This is the intended product for a drug-discovery audience: not a confident answer, but a ranked, cited, honestly-labelled candidate list that is *ahead of the curators or wrong* — and says which evidence would settle it.

### 4.3 Discovery without hallucination

The obvious objection to going beyond the KB is that "beyond the KB" is where hallucination lives. Three measurements address it:

- **Grounding is categorical.** 100% of genes named by the integrated system appear in actually-retrieved evidence, and 94–95% are KB-valid for the drug; the ungrounded baselines sit at 50–61%, naming plausible transporters from parametric memory. The discovery channel adds the remaining ~5% — and every one of those carries a literature citation and an `uncurated` label.
- **The false-premise probe.** One ADR question asserts a CYP2D6–doxorubicin link that does not exist in the KB. The gated, ledger-based configurations state the link is unsupported; we also report honestly that high-volume retrieval configurations failed this probe, which is precisely why claim-level structure, not context volume, is the safety mechanism.
- **Auditability.** Every answer persists its `references` and `evidence_log`; a citation in an answer that is absent from the log is mechanically detectable. Hallucination becomes a checkable event, which is what permits a discovery channel to exist at all.

---

## 5. Experimental setup

Experiments run on the Nibi cluster (Digital Research Alliance of Canada). The LLM is Qwen2.5-14B-Instruct (Q4_K_M) served by a rootless Ollama instance inside each SLURM job on one H100 MIG 2g.20gb slice (~20 GB VRAM); compute nodes have no internet, so models are staged from a login node and inference is fully offline. Literature-enabled configurations use NCBI E-utilities with per-PMID caching and ~3 req/s rate limiting. All thirteen configurations run identical code and differ only in environment variables, which is what makes the ablation clean. Datasets: 5,452 converted GenMedGPT-5k items (open-ended pilot: 73 items, mean rescaled BERTScore F1 0.20 in fully offline mode — a system-level ablation of the base paper, not a reproduction); 12,173 QA pairs synthesized from ClinPGx variant–drug annotations with direction-leakage control; and ten open-ended ADR questions including the false-premise probe.

## 6. Phase ablation (10 ADR questions, identical model and code)

| Phase | Sources active | Refs/q | Full texts | On-topic % | Ledger pairs | False premise |
|---|---|---|---|---|---|---|
| 3 | KB only | 8.5 | 0 | n/a | ~2–3 | missed |
| 4 | + cited abstracts | 22.6 | 0 | 22% | ~2–3 | **caught** |
| 9 | + edge-conditioned search + full text | 22.5 | 6 | 54% | ~2–3 | missed |
| 11 | + free query authoring + digest + ledger | 13.0 | 6 | **65%** | 96 | **caught** |
| 12 | + expanded OA full text | 13.7 | 12 | 63% | 91 | **caught** |
| 13 | + contradiction resolution | **23.8** | **17** | 49% | **145** | missed |

Under a research-oriented weighting phase 13 ranks first (4.44/5); under a clinical-safety weighting phase 11 ranks first (4.40/5). The ranking flips with the objective, and we report the flip rather than choosing: discovery-oriented and safety-oriented deployments should not run the same configuration.

## 7. Limitations

- **n = 10 for the phase comparison, no gold answers**; the metrics are checkable proxies (definitions in the repository), not significance tests. The categorical results — grounding validity, false-premise behavior, the existence and citation of uncurated candidates — are the robust ones.
- **Partial circularity**: KB-validity scores KB-retrieving phases against the same KB. It is fair against the baselines and between phases; it does not prove biological correctness. The uncurated candidates are, by definition, outside this metric — their validation would require curator review or prospective study, which is exactly the position such candidates should occupy.
- **Contradiction coverage is thin**: 83% of final-configuration pairs have fewer than two comparable clinical sources; context extraction succeeds 92% for endpoint but only ~51% for population/cancer type and 30% for dose, so half the conflicts lack a named axis. Calibration was measured on one configuration and assumed for the others.
- **Prompt guards are instructions, not constraints**; the enforceable guarantees are the deterministic ledger, the provenance log, and the detectability of uncited claims.

## 8. Novelty statement

Prior graph-RAG systems, including the one we build on, use retrieval to help the model find an answer inside what is already known. Our contribution is a system that (i) genuinely integrates five heterogeneous sources — curated tables, cited abstracts, live relationship-conditioned search, paragraph-digested full text, and model knowledge — under typed provenance, formula-based cross-source scoring, and typed cross-source contradiction resolution with named axes of disagreement; and (ii) uses that integration to *go beyond* the curated knowledge graph, surfacing literature-supported candidate associations absent from 12,000+ curated annotations, in a format that is cited, calibrated, and explicitly labelled unconfirmed. We know of no prior medical QA system built on generated knowledge graphs that does either with a benchmarked deterministic confidence formula, let alone both; and we supply the negative results (retrieval volume degrading false-premise safety; mechanistic evidence inflating contradictions) that explain *why* the structure is necessary, not merely that it works. The full stack runs offline on one 20 GB GPU slice with an open 14B model.

## 9. Reproducibility

All code, prompts, per-phase SLURM scripts, the labelled calibration pairs, evaluation scripts, and result files are in the repository. Each phase is a single `sbatch` script differing only in environment variables; `score_phases.py` regenerates the scorecard with explicit, re-weightable composites. Every answer persists its `references` and `evidence_log`, so every citation in every reported answer can be checked against what was actually retrieved.
