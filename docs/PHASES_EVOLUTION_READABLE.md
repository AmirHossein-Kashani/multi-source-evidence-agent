# AMG-RAG Phase Evolution: From Unsupported Answers to Contradiction-Aware Evidence

## Executive summary

All AMG-RAG phases used the same underlying model—**Qwen2.5-14B**—and were evaluated on the same ten adverse drug reaction (ADR) questions. The phases differ in how they retrieve, read, evaluate, and compare evidence.

The original system generated answers from an LLM-built knowledge graph but provided little reliable provenance. Development therefore followed four broad goals:

1. Ground gene–drug claims in a curated pharmacogenomic database.
2. Retrieve and cite the scientific literature behind those claims.
3. read relevant evidence from full papers rather than relying only on abstracts.
4. Detect and explain contradictions between studies.

The phases show steady progress toward these goals. **Phase 11 produced the most precise and best-calibrated answers**, while **Phase 13 best supports the project's central research objective: finding and explaining contradictory evidence**. For that reason, Phase 13 is the preferred research configuration, with Phase 11 retained as a precision and safety control.

## At a glance

| Stage | Main improvement | Key result | Main limitation |
|---|---|---|---|
| Baselines | Original AMG-RAG | Plausible answers | No reliable provenance |
| Phase 3 | ClinPGx grounding | Gene validity increased to 95% | No literature evidence |
| Phases 4–5 | Cited PubMed evidence and initial full text | First citable answers | Search precision remained low |
| Phases 6–7 | Broader open search | More papers retrieved | Too much irrelevant evidence |
| Phases 8–9 | Relationship-based queries | On-topic retrieval reached 54% | Papers were not fully analyzed |
| Phase 10 | Flexible search and paper digestion | Relevant paragraphs became citable | No evidence ledger |
| Phase 11 | Confidence and contradiction ledger | Best precision: 65% | Contradictions were only flagged |
| Phase 12 | More open-access full text | Full-text reading doubled | Mechanistic evidence inflated conflicts |
| Phase 13 | Context-aware contradiction resolution | Best research score: 4.44 | 83% of pairs remained insufficient |

---

## Baselines: where the project started

The two baseline configurations either used no external information or searched PubMed and Wikipedia using the original pipeline.

Only **61% of genes from Baseline A** and **50% from Baseline B** were genes that ClinPGx associated with the relevant drug. The answers sounded plausible, but the evidence could not be audited. The original PubMed component even discarded lines containing PMID identifiers, removing the information required to cite retrieved papers.

**Conclusion:** the baseline system could generate an answer, but it could not reliably demonstrate that the answer was supported.

## Phase 3: grounding answers in ClinPGx

Phase 3 replaced guessed associations with curated ClinPGx/PharmGKB gene–variant–drug records. Evidence levels from the database were used to weight knowledge-graph connections.

**Result:** gene validity increased from **50–61% to 95%**, and every reported gene appeared in retrieved evidence.

**Limitation:** the system could report a curated association but could not retrieve the scientific papers supporting it.

## Phase 4: connecting curated claims to their sources

Phase 4 retrieved the exact PubMed identifiers cited by ClinPGx for each gene–drug relationship. Live PubMed search was used only when the curated citations were insufficient.

**Result:** the system retrieved an average of **22.6 references per question** and produced the first genuinely citable evidence set. It also recovered the established ACYP2 association with cisplatin ototoxicity and correctly rejected the false CYP2D6–doxorubicin premise.

**Limitation:** open-search precision was low, and the system remained restricted largely to knowledge already curated by ClinPGx.

## Phase 5: adding full-text retrieval

Phase 5 attempted to replace abstracts with complete PubMed Central articles.

**Result:** only two full-text papers were available across the ten questions because many ClinPGx-cited papers were older or paywalled.

**Conclusion:** simply enabling full-text retrieval did not help when open copies were unavailable.

## Phases 6 and 7: searching beyond ClinPGx

These phases allowed the model to propose new PubMed search topics. Phase 7 also enabled full-text retrieval.

**Result:** Phase 7 retrieved the largest number of references among the early phases, averaging **26.9 per question**.

**Limitation:** many searches were too broad. Queries such as “cancer” or “tinnitus” retrieved recent but irrelevant papers. Only **20–23%** of results were on topic, and the excess evidence caused the model to overlook the corrective note in the false-premise question.

## Phases 8 and 9: searching for relationships

Instead of searching isolated topics, these phases searched combinations such as `cisplatin AND ACYP2 AND hearing loss`. This targeted the relationship among the drug, gene, and adverse effect.

**Result:** on-topic retrieval more than doubled, reaching **54%**.

**Limitation:** Phase 9's apparent full-text processing used only the beginning of each article, which was usually background material. Much of the retrieved literature was also removed before reaching the answer stage.

## Phase 10: flexible queries and real paper reading

Phase 10 allowed the model to write complete PubMed queries using one or several concepts. It also divided papers into paragraphs, ranked sections by evidence density, and retained the paragraphs most relevant to the question.

**Result:** on-topic retrieval increased to **59%**, empty searches were eliminated through query back-off, and findings became traceable to paragraph-level references.

**Limitation:** the system could read and cite evidence but still lacked a structured method for combining claims across sources.

## Phase 11: the evidence ledger

Phase 11 organized every curated and literature-derived claim into an evidence ledger for each gene–drug pair. Confidence was calculated by a transparent rule rather than assigned by the language model. Supporting evidence, refuting evidence, and contradiction flags were preserved separately.

**Result:** Phase 11 achieved the highest retrieval precision, at **65% on topic**. It identified 96 gene–drug pairs and 61 potentially disputed pairs. On a benchmark of 72 labelled relationships, confidence correlated well with the expected evidence ordering (**Spearman 0.721**), and contradiction recall reached **0.95**. It also passed the false-premise safety test.

**Limitation:** the ledger detected that sources disagreed but did not reliably explain why. It could also treat an in-vitro result as though it directly contradicted a clinical association.

## Phase 9L: maximizing discovery

Phase 9L combined the wider relationship-based retrieval of Phase 9 with the Phase 11 evidence ledger.

**Result:** it retrieved **116 gene–drug pairs**, 145 PubMed references, and 72 contradiction flags. It was particularly useful for discovering uncurated candidates and disagreements between literature and curated data.

**Limitation:** precision fell to 52%, unsupported claims increased, and the configuration missed the false-premise test. It was useful for discovery, but less dependable for a concise clinical answer.

## Phase 12: expanding access to full papers

Phase 12 added legal open-access retrieval through Europe PMC and Unpaywall.

**Result:** open full-text coverage increased from **6% to 43%**, and the number of papers read in full doubled. Additional evidence reduced unsupported claims and revealed disagreements that were absent from abstracts.

**Limitation:** the ledger treated indirect mechanistic studies as equivalent to clinical studies. This inflated contradiction counts without necessarily identifying meaningful scientific disagreement.

## Phase 13: explaining contradictions

Phase 13 introduced a dedicated contradiction-resolution layer. Evidence was classified as **curated, clinical, mechanistic, or narrative**, and only comparable types of evidence were allowed to form a direct contradiction. Claims were also compared by population, cancer type, endpoint, dose, and effect direction.

**Result:** Phase 13 delivered the broadest and deepest analysis:

- 145 gene–drug pairs;
- 23.8 references per question;
- 17 papers read in full;
- 70 relevant paragraphs cited;
- 22 genuinely conflicting pairs;
- 3 context-dependent disagreements; and
- 29 mechanistic results correctly downgraded rather than misreported as clinical contradictions.

The three context-dependent cases show the value of this approach:

- **TPMT–cisplatin:** studies used different hearing-loss endpoints.
- **SLC28A3–anthracycline:** results differed between children and adults.
- **GSTM1–doxorubicin:** results differed across cancer types.

Phase 13 therefore does more than say that two sources disagree. It attempts to determine whether the disagreement is genuine and identify the context that explains it.

**Limitations:** 120 of 145 pairs (**83%**) had insufficient comparable clinical evidence for resolution. Half of the remaining conflicts lacked a clearly extracted explanatory factor. Retrieval precision fell to 49%, and the system missed the false-premise safety test because the wider evidence context crowded out the correction.

---

## Final assessment

There is no single best phase for every purpose:

- **Phase 11 is best for precision, calibrated confidence, and safer question answering.**
- **Phase 13 is best for broad research and contradiction resolution.**
- **Phase 4 is the most useful conservative baseline based mainly on curated evidence.**

Because this project's main contribution is the discovery and interpretation of contradictory pharmacogenomic evidence, **Phase 13 is the preferred final research configuration**. Its most important advance is not that it finds the largest number of contradictions, but that it separates genuine clinical disagreement from differences in evidence type or study context.

The strongest future system would combine **Phase 13's contradiction-resolution layer** with **Phase 11's precise free-form retrieval, calibrated confidence, and false-premise protection**. It should also improve context extraction, normalize gene symbols, preserve provenance consistently, distinguish truly insufficient evidence from curated-only evidence, and require citations in every final answer.
