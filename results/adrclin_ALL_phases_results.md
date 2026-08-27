# AMG-RAG — results of all phases (ADR clinical set)

Every phase currently on disk, over the same 10 questions, same model (`qwen2.5:14b`), same code — the phases differ **only by environment variables**.

## Phase catalogue

| Phase | Configuration | Retrieval behaviour | n |
|---|---|---|---|
| **Baseline A — no external sources** | `AMG_USE_EXTERNAL=0` | no external evidence; LLM knowledge only | 9 |
| **Baseline B — paper setup** | `AMG_USE_EXTERNAL=1` (PubMed + Wikipedia) | the paper's setup: live PubMed + Wikipedia | 9 |
| **Phase 3 (old run) — ClinPGx** | `AMG_KB_SOURCE=pharmgkb` (pre-provenance) | offline ClinPGx tables (before provenance logging) | 9 |
| **Phase 3 — ClinPGx only** | `AMG_KB_SOURCE=pharmgkb` | offline ClinPGx tables | 10 |
| **Phase 4 — ClinPGx + cited PubMed** | `AMG_KB_SOURCE=pharmgkb+pubmed` | ClinPGx, then the exact PMIDs ClinPGx cites for those pairs | 10 |
| **Phase 5 — + PMC full text** | `AMG_KB_SOURCE=pharmgkb+pubmed` `AMG_PUBMED_FULLTEXT=1` | as phase 4, abstracts upgraded to PMC full text | 10 |
| **Phase 6 — open LLM search** | `AMG_KB_SOURCE=pharmgkb+pubmed_open` | LLM picks search topics freely from question + graph; one topic per query | 10 |
| **Phase 7 — open search + full text** | `AMG_KB_SOURCE=pharmgkb+pubmed_open` `AMG_PUBMED_FULLTEXT=1` | as phase 6, plus PMC full text | 10 |
| **Phase 8 — combined-topic search** | `AMG_KB_SOURCE=pharmgkb+pubmed_combo` | graph-related terms combined into ONE conjunctive query; LLM picks the arity | 10 |
| **Phase 9 — combined + full text** | `AMG_KB_SOURCE=pharmgkb+pubmed_combo` `AMG_PUBMED_FULLTEXT=1` | as phase 8, plus PMC full text | 10 |
| **Phase 10 — free arity + own phrasing** | `AMG_KB_SOURCE=pharmgkb+pubmed_free` `AMG_PUBMED_FULLTEXT=1` | model chooses the arity (1, 2, 3, …) AND writes the PubMed query string itself | 10 |
| **Phase 11 — evidence ledger** | `+ AMG_PAPER_DIGEST=1` `AMG_EVIDENCE_LEDGER=1` | as phase 10, plus a per-gene ledger: confidence by rule + source contradictions | 10 |

## Scores

No gold answers exist for these questions (`reference` is empty), so BERTScore does not apply. These metrics are computable without one:

- **On-topic %** — retrieved papers mentioning *both* the question's drug *and* its adverse effect
- **Grounded %** — genes named in the answer that appear in evidence actually retrieved
- **ClinPGx-valid %** — genes named that ClinPGx really links to that drug
- **False premise** — Q8 asserts a CYP2D6–doxorubicin link that does not exist; is it caught?

| Phase | Refs/q | PubMed/q | Full text | On-topic % | Grounded % | ClinPGx-valid % | False premise |
|---|---|---|---|---|---|---|---|
| Baseline A — no external sources | 0.0 | 0.0 | 0 | n/a | n/a | 61% | ❌ |
| Baseline B — paper setup | 0.0 | 0.0 | 0 | n/a | n/a | 50% | ❌ |
| Phase 3 (old run) — ClinPGx | 0.0 | 0.0 | 0 | n/a | n/a | 94% | ❌ |
| Phase 3 — ClinPGx only | 8.5 | 0.0 | 0 | n/a | 100% | 95% | ❌ |
| Phase 4 — ClinPGx + cited PubMed | 22.6 | 14.3 | 0 | 22% | 100% | 95% | ✅ |
| Phase 5 — + PMC full text | 23.2 | 14.3 | 2 | 17% | 100% | 95% | ✅ |
| Phase 6 — open LLM search | 25.8 | 17.7 | 0 | 20% | 100% | 94% | ❌ |
| Phase 7 — open search + full text | 26.9 | 18.6 | 6 | 23% | 100% | 95% | ❌ |
| Phase 8 — combined-topic search | 22.2 | 13.5 | 0 | 54% | 100% | 93% | ❌ |
| Phase 9 — combined + full text | 22.5 | 14.0 | 6 | 54% | 100% | 95% | ❌ |
| Phase 10 — free arity + own phrasing | 13.0 | 4.6 | 5 | 59% | 92% | 80% | ❌ |
| Phase 11 — evidence ledger | 13.0 | 4.8 | 4 | 65% | 81% | 85% | ✅ |

## Search shape — how many items were searched together (phases 8/9/10)

| Phase | Queries | 1-term | 2-term | 3-term | 4+-term | Mean arity | Back-offs | Empty |
|---|---|---|---|---|---|---|---|---|
| Phase 8 — combined-topic search | 160 | 0 (0%) | 85 (53%) | 75 (47%) | 0 (0%) | 2.47 | 19 | 12 |
| Phase 9 — combined + full text | 159 | 0 (0%) | 80 (50%) | 79 (50%) | 0 (0%) | 2.50 | 18 | 10 |
| Phase 10 — free arity + own phrasing | 392 | 23 (6%) | 237 (60%) | 110 (28%) | 22 (6%) | 2.34 | 39 | 0 |
| Phase 11 — evidence ledger | 392 | 31 (8%) | 246 (63%) | 103 (26%) | 12 (3%) | 2.25 | 39 | 0 |

## Genes surfaced, by phase

| Q | A | B | 3-old | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | ABCC3, SLC15A4, SLC22A8 | ABCB1, SLC2A1 | GSTM1, TPMT | GSTM1, TPMT | ACYP2, GSTM1 | GSTM1, GSTP1 | GSTM1 | ACYP2, GSTM1 | GSTM1, TPMT | ACYP2, GSTM1, TPMT | COMT, GSTM1, GSTT1, NFE2L2, TPMT | GADD45A, GSTM1, GSTT1, NFE2L2 |
| Q2 | ABCB1, GSTP1, SLC2A1 | ATP7A, SLC2A1 | GSTM1, TPMT | GSTM1, TPMT | GSTM1 | GSTM1 | COMT, GSTM1, TPMT | COMT, GSTM1, TPMT | GSTM1 | GSTM1, TPMT | COMT, GSTM1, TPMT | COMT, GSTM1, TPMT |
| Q3 | TPMT | TPMT | GSTM1, TPMT | GSTM1, TPMT | ACYP2, GSTM1, TPMT | GSTM1, TPMT | TPMT | ACYP2, GSTM1, TPMT | TPMT | ACYP2, GSTM1, TPMT | GSTM1, NFE2L2, TPMT | GSTT1, NFE2L2, TPMT |
| Q4 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 | GSTT1 |
| Q5 | OXR1, SLC7A11, XRCC1 | — | ERCC1, GSTP1 | ERCC1, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTM3, GSTP1 | ERCC1, GSTP1 | ERCC1, GSTM3, GSTP1 | ABCC3, AKT1, ERCC1, GSTM3, GSTP1, SLC19A1 |
| Q6 | ABCB1, GSTP1 | ABCB1, CYP3A4, CYP3A5 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 | GSTP1, SLC28A3 |
| Q7 | ABCB1, APOE, GSTP1 | ABCB1, APOE, SLCO1B1 | GSTP1, SLC28A3 | RARG, SLC28A3 | GSTP1, RARG, SLC28A3 | GSTP1, RARG, SLC28A3 | RARG, SLC28A3 | GSTP1, RARG, SLC28A3 | SLC28A3 | RARG, SLC28A3 | RARG, SLC28A3 | GSTP1, SLC28A3 |
| Q8 | CYP2D6 | CYP2D6 | CYP2D6, SLC28A3 | CYP2D6, SLC28A3 | CYP2D6, SLC28A3 | CYP2D6, SLC28A3 | CYP2D6 | CYP2D6 | CYP2D6 | CYP2D6 | CYP2D6 | CYP2D6, SLC28A3 |
| Q9 | GSTM1 | GSTM1 | GSTM1, GSTP1, SLC28A3 | GSTM1, GSTP1, SLC28A3 | GSTM1, SLC28A3 | GSTM1, SLC28A3 | GSTM1 | GSTM1, SLC28A3 | GSTM1 | GSTM1, SLC28A3 | GSTM1 | GSTM1 |
| Q10 | — | — | — | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1 | CYBA, ERCC1, RS11615, RS4673 | CYBA, ERCC1 |

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

### Baseline A — no external sources

**Genes:** ABCC3, SLC15A4, SLC22A8  ·  **Evidence:** 0 refs, 0 papers

The development of hearing loss and tinnitus in a child receiving cisplatin for cancer treatment is likely influenced by genetic variants such as SLC22A8, ABCC3, and SLC15A4. Variants in these genes can affect the transport and efflux of cisplatin within auditory cells, leading to increased intracellular concentrations and subsequent ototoxicity. Understanding these genetic factors could guide personalized treatment strategies by enabling pre-treatment biomarker screening to identify patients at higher risk for ototoxicity, potentially allowing dose adjustments or the use of alternative agents like carboplatin.

### Baseline B — paper setup

**Genes:** ABCB1, SLC2A1  ·  **Evidence:** 0 refs, 0 papers

The ototoxicity experienced by a child receiving cisplatin for cancer treatment is likely influenced by genetic variants such as those in the SLC2A1 and ABCB1 genes. Variants in these transporters can affect cisplatin's cellular uptake, distribution, and clearance, thereby impacting its toxicity on auditory cells. Genetic testing for these variants could help identify patients at higher risk of ototoxicity, enabling personalized treatment strategies such as dose adjustment or the use of alternative agents to mitigate adverse effects.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTM1, TPMT  ·  **Evidence:** 0 refs, 0 papers

The genetic variants GSTM1 non-null and TPMT*1 are implicated in cisplatin-induced ototoxicity, though the evidence is moderate (PharmGKB level 3) and described as ambiguous by ClinPGx. The biological mechanism likely involves impaired detoxification of cisplatin's toxic metabolites due to reduced glutathione S-transferase activity for GSTM1 non-null and possibly altered thiopurine metabolism for TPMT*1, leading to increased ototoxicity risk. For drug discovery and patient safety, pre-treatment genetic screening for these variants could inform dose adjustments or the use of protective agents like amifostine to mitigate ototoxic effects.

### Phase 3 — ClinPGx only

**Genes:** GSTM1, TPMT  ·  **Evidence:** 9 refs, 0 papers

The genetic variants GSTM1 non-null and TPMT*1 are implicated in cisplatin-induced ototoxicity, though the evidence is moderate (PharmGKB level 3) and described as ambiguous by ClinPGx. The biological mechanism likely involves impaired detoxification of cisplatin's toxic metabolites due to reduced glutathione S-transferase activity for GSTM1 non-null and possibly altered thiopurine metabolism for TPMT*1, leading to increased ototoxicity risk. For drug discovery and patient safety, pre-treatment genetic screening for these variants could inform dose adjustments or the use of protective agents like amifostine to mitigate ototoxic effects.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** ACYP2, GSTM1  ·  **Evidence:** 24 refs, 15 papers

The genetic variants ACYP2 (rs1872328) and GSTM1 are implicated in cisplatin-induced ototoxicity, with stronger evidence supporting the role of rs1872328. The biological mechanism likely involves impaired cellular detoxification or increased sensitivity to cisplatin's cytotoxic effects due to these genetic variations. For drug discovery and patient safety, pre-treatment screening for ACYP2 (rs1872328) could help identify patients at higher risk of ototoxicity, potentially allowing dose adjustments or the use of alternative agents such as carboplatin, which has a lower incidence of this side effect.

<details><summary>Papers retrieved</summary>

- `PMID:25665007` — **Common variants in ACYP2 influence susceptibility to cisplatin-induced hearing loss.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:26928270` — **Replication of a genetic variant in ACYP2 associated with cisplatin-induced hearing loss in patients with osteosarcoma.** — *Pharmacogenetics and genomics · 2016*
  - via `clinpgx_citation`
- `PMID:28445188` — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:42599282` — **Three-dimensional Clay Model to Process Eyelid, Ear, and Urethral Mohs Layers.** — *Dermatologic surgery : official publication for American Society for Dermatologic Surgery [et al.] · 2026*
  - via `-`
- `PMID:42599278` — **Histopathology and Clinical Features of SPARK Nevi in a Multi-Institutional Cohort.** — *International journal of surgical pathology · 2026*
  - via `-`
- `PMID:12127547` — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - via `clinpgx_citation`
- `PMID:18830133` — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - via `clinpgx_citation`
- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:10376773` — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - via `clinpgx_citation`
- `PMID:10734022` — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - via `clinpgx_citation`
- `PMID:12209976` — **Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation.** — *International journal of cancer · 2002*
  - via `clinpgx_citation`
- `PMID:17000685` — **Pharmacogenetics of capecitabine in advanced breast cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTM1, GSTP1  ·  **Evidence:** 22 refs, 13 papers

The genetic variants GSTM1 null and GSTP1 Ile/Val or Val/Val genotypes are implicated in increased susceptibility to cisplatin-induced hearing loss and tinnitus. The biological mechanism involves the role of glutathione S-transferases (GSTs) in detoxifying reactive metabolites generated by cisplatin, which can lead to ototoxicity if these enzymes are less effective due to genetic polymorphisms. For drug discovery and patient safety, pre-treatment screening for GSTM1 null status and GSTP1 genotypes could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents such as carboplatin.

<details><summary>Papers retrieved</summary>

- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:23274376` — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:12127547` — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - via `clinpgx_citation`
- `PMID:18830133` — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - via `clinpgx_citation`
- `PMID:10376773` — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - via `clinpgx_citation`
- `PMID:10734022` — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - via `clinpgx_citation`
- `PMID:19451915` — **Candidate-gene association analysis of response to risperidone in African-American and white patients with schizophrenia.** — *The pharmacogenomics journal · 2009*
  - via `clinpgx_citation`
- `PMID:22935916` — **Association between a COMT polymorphism and clinical response to risperidone treatment: a pharmacogenetic study.** — *Psychiatric genetics · 2012*
  - via `clinpgx_citation`
- `PMID:42597480` — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `-`
- `PMID:42577562` — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `-`

</details>

### Phase 6 — open LLM search

**Genes:** GSTM1  ·  **Evidence:** 23 refs, 16 papers

The genetic variants GSTM1 non-null are implicated in cisplatin-induced ototoxicity, including hearing loss and tinnitus. Individuals lacking the null variant of GSTM1 (GSTM1 non-null) have reduced detoxification capacity due to lower glutathione S-transferase activity, leading to increased oxidative stress and inflammation in the cochlea. This highlights the need for pre-treatment genetic screening for GSTM1 status to identify patients at higher risk of ototoxicity, potentially allowing for dose adjustments or the use of alternative agents such as carboplatin, which has a lower incidence of ototoxic side effects.

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin ototoxicity genetics`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 hearing loss`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:TPMT ototoxicity variants`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635394` — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635355` — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635501` — **Normative Ranges for Auditory Brainstem Response Wave I Amplitude: A Potential Diagnostic Indicator of Cochlear Deafferentation.** — *American journal of audiology · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42634562` — **Assessment of Transverse-sigmoid Sinus Dural Arteriovenous Fistula using Transcranial Doppler Ultrasonography: A Case Report.** — *Current medical imaging · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42091970` — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 non-null`
- `PMID:36672743` — **Molecular Characterization of Tropomyosin and Its Potential Involvement in Muscle Contraction in Pacific Abalone.** — *Genes · 2022*
  - via `llm_topic:TPMT*1`
- `PMID:18775689` — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT*1`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:rs4646316`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:rs4646316`
- `PMID:42621050` — **Integrating multi-omics and deep learning to explore the active ingredients and molecular mechanisms of Cinnamomum migao volatile oil in the treatment of coronary heart disease.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:Gadd45a`
- `PMID:42532387` — **Comparative transcriptomic analysis reveals immune regulation in mandarin fish (Siniperca chuatsi) under high- and low-temperature.** — *Developmental and comparative immunology · 2026*
  - via `llm_topic:CXCL family protein expression`

</details>

### Phase 7 — open search + full text

**Genes:** ACYP2, GSTM1  ·  **Evidence:** 27 refs, 20 papers, 1 full text

The development of hearing loss and tinnitus due to cisplatin treatment is associated with genetic variants in ACYP2 (acylphosphatase 2) and GSTM1 (glutathione S-transferase mu 1). Specifically, the variant rs1872328 in ACYP2 has been linked to increased susceptibility to ototoxicity. The biological mechanisms underlying these associations are not fully understood but may involve altered cellular processes such as DNA repair or stress kinase signaling that affect cell survival during cisplatin exposure. For drug discovery and patient safety, pre-treatment genetic screening for variants like rs1872328 in ACYP2 could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents to mitigate these side effects.

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin ototoxicity genetics`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:GSTM1 cisplatin deafness`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:TPMT variant ototoxicity`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635634` — **CORRIGENDUM: Curcumin nanoparticles combined with 3D printed bionic tumor models for breast cancer treatment (2023Biofabrication 15 014105).** — *Biofabrication · 2026*
  - via `llm_topic:cancer`
- `PMID:42635633` — **Mesoporous-Shell Monolayer Plasmonic Architecture Enables Quantitative and Decision-Guided SERS.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `llm_topic:cancer`
- `PMID:42635394` — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635355` — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635501` — **Normative Ranges for Auditory Brainstem Response Wave I Amplitude: A Potential Diagnostic Indicator of Cochlear Deafferentation.** — *American journal of audiology · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42634562` — **Assessment of Transverse-sigmoid Sinus Dural Arteriovenous Fistula using Transcranial Doppler Ultrasonography: A Case Report.** — *Current medical imaging · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42631829` — **Inner Ear Organoids: Recent Progress and Challenges.** — *Stem cell reviews and reports · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:31666714` — **Genetic variation of cisplatin-induced ototoxicity in non-cranial-irradiated pediatric patients using a candidate gene approach: The International PanCareLIFE Study.** — *The pharmacogenomics journal · 2020*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:18775689` — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:16621695` — **Cloning and characterization of a new multi-stress inducible metallothionein gene in Tetrahymena pyriformis.** — *Protist · 2006*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin ototoxicity genetics+pmc_xml`
- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `llm_topic:ACYP2 hearing loss`

</details>

### Phase 8 — combined-topic search

**Genes:** GSTM1, TPMT  ·  **Evidence:** 15 refs, 8 papers

The development of hearing loss and tinnitus in a child receiving cisplatin for cancer treatment implicates genetic variants such as GSTM1 non-null, which is associated with reduced detoxification capacity leading to increased ototoxicity risk. TPMT*1 has also been linked to this adverse effect but with less consistent evidence. The biological mechanism involves impaired metabolism and detoxification of cisplatin's reactive metabolites, causing oxidative stress and cellular damage in the auditory system. For drug discovery and patient safety, genetic screening for GSTM1 status could inform personalized dosing strategies or alternative agents with lower ototoxic potential to mitigate these risks.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `COMT AND drug toxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)
- `cancer AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `tinnitus AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 non-null AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `TPMT*1 AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `rs4646316 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `Gadd45a AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 1 hit(s)
- `cisplatin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `combo2:cisplatin + ototoxicity`
- `PMID:39386217` — **GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-triggered ferroptosis.** — *Frontiers in immunology · 2024*
  - via `combo2:GSTM1 + cisplatin`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `combo2:TPMT + ototoxicity`
- `PMID:42617317` — **Honokiol-mediated reversal of cisplatin-induced transcriptomic changes in outer hair cells.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `combo3:cancer + cisplatin + hearing loss`
- `PMID:42497611` — **Exploring the usability of a point-of-care hearing screening by oncology registered nurses with adult cancer patients during Cisplatin chemotherapy - A convergent mixed methods study.** — *European journal of oncology nursing : the official journal of European Oncology Nursing Society · 2026*
  - via `combo3:tinnitus + cisplatin + hearing loss`
- `PMID:30113582` — **[The analysis of the association of the polymorphic variants of the TPMT, COMT, and ABCC3 genes with the development of hearing disorders induced by the cisplatin treatment].** — *Vestnik otorinolaringologii · 2018*
  - via `combo3:rs4646316 + cisplatin + hearing loss`
- `PMID:28445188` — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - via `combo3:rs4646316 + cisplatin + hearing loss`

</details>

### Phase 9 — combined + full text

**Genes:** ACYP2, GSTM1, TPMT  ·  **Evidence:** 17 refs, 10 papers

Cisplatin-induced ototoxicity, leading to hearing loss and tinnitus, is associated with genetic variants in ACYP2 (rs1872328), GSTM1, and TPMT. These variants likely influence the metabolism or cellular uptake of cisplatin, affecting its toxicity profile within auditory tissues. For drug discovery and patient safety, pre-treatment screening for these risk variants could enable personalized dosing strategies to mitigate ototoxicity risks in pediatric patients receiving cisplatin.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ACYP2` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTM1 AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing_loss AND tinnitus AND pharmacogenomics` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)
- `cancer AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `tinnitus AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `ototoxicity AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `ACYP2 rs1872328 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 GSTM1 non-null AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `TPMT TPMT*1 AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `cisplatin AND ACYP2` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `COMT AND rs4646316 AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `combo2:cisplatin + ACYP2`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `combo3:cisplatin + GSTM1 + ototoxicity`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `combo2:TPMT + ototoxicity`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:42617317` — **Honokiol-mediated reversal of cisplatin-induced transcriptomic changes in outer hair cells.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `combo3:cancer + cisplatin + hearing loss`
- `PMID:42497611` — **Exploring the usability of a point-of-care hearing screening by oncology registered nurses with adult cancer patients during Cisplatin chemotherapy - A convergent mixed methods study.** — *European journal of oncology nursing : the official journal of European Oncology Nursing Society · 2026*
  - via `combo3:tinnitus + cisplatin + hearing loss`
- `PMID:31666714` — **Genetic variation of cisplatin-induced ototoxicity in non-cranial-irradiated pediatric patients using a candidate gene approach: The International PanCareLIFE Study.** — *The pharmacogenomics journal · 2020*
  - via `combo3:ACYP2 rs1872328 + cisplatin + hearing loss`
- `PMID:30837596` — **The genetic vulnerability to cisplatin ototoxicity: a systematic review.** — *Scientific reports · 2019*
  - via `combo3:ACYP2 rs1872328 + cisplatin + hearing loss`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `combo2:GSTM1 + ototoxicity`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** COMT, GSTM1, GSTT1, NFE2L2, TPMT  ·  **Evidence:** 12 refs, 5 papers, 1 full text

The genetic variants GSTM1 null, GSTT1 null, TPMT*1, COMT rs4646316 and rs9332377, and NFE2L2 rs6721961 are implicated in cisplatin-induced ototoxicity. These variants likely influence the detoxification of reactive metabolites generated by cisplatin, cellular stress response pathways, and antioxidant defense mechanisms, thereby affecting susceptibility to ototoxic side effects such as hearing loss and tinnitus. For drug discovery and patient safety, pre-treatment genetic screening for these risk alleles can help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents like carboplatin, which may have a lower risk profile for ototoxicity in genetically susceptible individuals.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/TPMT AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND tinnitus` — 1 terms, 0 back-off(s), 2 hit(s)
- `COMT/GSTM1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT*1 AND ototoxicity AND cisplatin` — 1 terms, 2 back-off(s), 2 hit(s)
- `COMT/rs4646316 AND ototoxicity AND cisplatin` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(GSTM1 OR TPMT) AND cisplatin AND hearing loss`
- `PMID:42566269` — **Author Reply to Letter to the Editor Regarding "Intratympanic Dexamethasone Efficacy in Preventing Cisplatin-Induced Tinnitus: A Randomized Controlled Phase IIIB Clinical Trial".** — *Ear and hearing · 2026*
  - via `free2:"cisplatin induced tinnitus"`
- `PMID:41532599` — **The association between DNA repair genes polymorphisms and cisplatin-induced ototoxicity in cancer patients: a systematic review.** — *Personalized medicine · 2025*
  - via `free2:ERCC1[gene] AND ototoxicity`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity+pmc_xml`

</details>

### Phase 11 — evidence ledger

**Genes:** GADD45A, GSTM1, GSTT1, NFE2L2  ·  **Evidence:** 12 refs, 5 papers, 1 full text

The ototoxicity you experienced after receiving cisplatin may be influenced by genetic variants such as GSTT1 null genotype, NFE2L2 rs6721961 (G-allele), and possibly variations in GADD45A. The GSTT1 null genotype is associated with reduced detoxification capabilities, leading to increased susceptibility to ototoxicity. Similarly, the G-allele of NFE2L2 rs6721961 affects antioxidant defense mechanisms crucial for protecting against cisplatin-induced oxidative stress. Variations in GADD45A may influence cellular responses to stress and inflammation, further contributing to ototoxic risk. These findings suggest that genetic screening could help identify patients at higher risk of hearing loss and tinnitus before initiating cisplatin therapy, allowing for dose adjustments or alternative treatment strategies.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/TPMT AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND tinnitus` — 1 terms, 0 back-off(s), 2 hit(s)
- `COMT/GSTM1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `hearing loss/tinnitus AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT*1 AND ototoxicity AND cisplatin` — 1 terms, 2 back-off(s), 2 hit(s)
- `COMT/rs4646316 AND ototoxicity AND cisplatin` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(GSTM1 OR TPMT) AND cisplatin AND hearing loss`
- `PMID:42566269` — **Author Reply to Letter to the Editor Regarding "Intratympanic Dexamethasone Efficacy in Preventing Cisplatin-Induced Tinnitus: A Randomized Controlled Phase IIIB Clinical Trial".** — *Ear and hearing · 2026*
  - via `free2:"cisplatin induced tinnitus"`
- `PMID:41532599` — **The association between DNA repair genes polymorphisms and cisplatin-induced ototoxicity in cancer patients: a systematic review.** — *Personalized medicine · 2025*
  - via `free2:ERCC1[gene] AND ototoxicity`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity+pmc_xml`

</details>

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

### Baseline A — no external sources

**Genes:** ABCB1, GSTP1, SLC2A1  ·  **Evidence:** 0 refs, 0 papers

Based on existing literature, several genes have been linked to cisplatin-induced ototoxicity risk in pediatric cancer patients, including SLC2A1, ABCB1, and GSTP1. These genetic variants likely influence the pharmacokinetics and pharmacodynamics of cisplatin, affecting its uptake, distribution, metabolism, or excretion. For drug discovery and patient safety, pre-treatment biomarker screening for these risk genes could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents to mitigate adverse effects.

### Baseline B — paper setup

**Genes:** ATP7A, SLC2A1  ·  **Evidence:** 0 refs, 0 papers

The genes SLC2A1 and ATP7A have been linked to cisplatin-induced ototoxicity risk in pediatric cancer patients. Variants within the SLC2A1 gene, which encodes for glucose transporter protein type 1 (GLUT1), may impair energy metabolism in cochlear hair cells, making them more susceptible to cisplatin toxicity. Mutations or reduced function of ATP7A, a copper-transporting ATPase involved in detoxifying platinum-based drugs like cisplatin by facilitating their efflux from cells, can increase the cytotoxic effects on auditory hair cells. These findings suggest that pre-treatment genetic screening for these variants could help identify patients at higher risk and potentially guide dose adjustments or alternative therapeutic strategies to mitigate ototoxicity.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTM1, TPMT  ·  **Evidence:** 0 refs, 0 papers

The genes/variants GSTM1 (non-null) and TPMT (TPMT*1) have been suggested to be associated with an increased risk of cisplatin-induced ototoxicity, particularly deafness, in pediatric cancer patients. The biological mechanism is likely related to the reduced detoxification capacity or altered metabolism of cisplatin by these genetic variants, leading to higher levels of reactive metabolites that damage auditory hair cells. However, due to the moderate evidence level and ambiguous clinical guidelines, further validation studies are needed before these associations can be used definitively in patient care. For drug discovery and patient safety, pre-treatment biomarker screening for these variants could help identify patients at risk, allowing for dose adjustments or consideration of alternative agents with a lower ototoxicity profile.

### Phase 3 — ClinPGx only

**Genes:** GSTM1, TPMT  ·  **Evidence:** 12 refs, 0 papers

The genes/variants GSTM1 (non-null) and TPMT (TPMT*1) have been suggested to be associated with an increased risk of cisplatin-induced ototoxicity, particularly deafness, in pediatric cancer patients. The biological mechanism is likely related to the reduced detoxification capacity or altered metabolism of cisplatin by these genetic variants, leading to higher levels of reactive metabolites that damage auditory hair cells. However, due to the moderate evidence level and ambiguous clinical guidelines, further validation studies are needed before these associations can be used definitively in patient care. For drug discovery and patient safety, pre-treatment biomarker screening for these variants could help identify patients at risk, allowing for dose adjustments or consideration of alternative agents with a lower ototoxicity profile.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** GSTM1  ·  **Evidence:** 25 refs, 17 papers

The non-null genotype of GSTM1 is strongly associated with an increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, suggesting a critical role for glutathione S-transferase activity in the detoxification process. The biological mechanism likely involves impaired cellular defense against oxidative stress and reduced ability to mitigate cisplatin's toxic effects on auditory hair cells. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could inform personalized dosing strategies or alternative therapeutic options to minimize ototoxicity risk in susceptible patients.

<details><summary>Papers retrieved</summary>

- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:23274376` — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:12127547` — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - via `clinpgx_citation`
- `PMID:18830133` — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - via `clinpgx_citation`
- `PMID:10376773` — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - via `clinpgx_citation`
- `PMID:10734022` — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - via `clinpgx_citation`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `-`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `-`
- `PMID:42542098` — **Proteomic profiling of root microsomal membrane fractions reveals distinct RBOHC- and RBOHF-associated responses to cadmium in Arabidopsis.** — *Ecotoxicology and environmental safety · 2026*
  - via `-`
- `PMID:42529344` — **Integrative transcriptomic and proteomic analysis reveals the regulatory mechanisms underlying oilseed rape resistance to Leptosphaeria biglobosa.** — *Frontiers in plant science · 2026*
  - via `-`
- `PMID:42033883` — **Post-treatment paternity in testicular cancer survivors: Do demographic variables matter?** — *Cancer epidemiology · 2026*
  - via `-`
- `PMID:40324110` — **Key Updates in Testicular Cancer: Optimizing Survivorship and Survival.** — *American Society of Clinical Oncology educational book. American Society of Clinical Oncology. Annual Meeting · 2025*
  - via `-`
- `PMID:11990381` — **UGT1A1*28 polymorphism as a determinant of irinotecan disposition and toxicity.** — *The pharmacogenomics journal · 2002*
  - via `clinpgx_citation`
- `PMID:15007088` — **Genetic variants in the UDP-glucuronosyltransferase 1A1 gene predict the risk of severe neutropenia of irinotecan.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2004*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTM1  ·  **Evidence:** 25 refs, 17 papers

The non-null genotype of GSTM1 is strongly associated with an increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, suggesting a critical role for glutathione S-transferase activity in the detoxification process. The biological mechanism likely involves impaired cellular defense against oxidative stress and reduced ability to mitigate cisplatin's toxic effects on auditory hair cells. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could inform personalized dosing strategies or alternative therapeutic options to minimize ototoxicity risk in susceptible patients.

<details><summary>Papers retrieved</summary>

- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:23274376` — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:12127547` — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - via `clinpgx_citation`
- `PMID:18830133` — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - via `clinpgx_citation`
- `PMID:10376773` — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - via `clinpgx_citation`
- `PMID:10734022` — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - via `clinpgx_citation`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `-`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `-`
- `PMID:42542098` — **Proteomic profiling of root microsomal membrane fractions reveals distinct RBOHC- and RBOHF-associated responses to cadmium in Arabidopsis.** — *Ecotoxicology and environmental safety · 2026*
  - via `-`
- `PMID:42529344` — **Integrative transcriptomic and proteomic analysis reveals the regulatory mechanisms underlying oilseed rape resistance to Leptosphaeria biglobosa.** — *Frontiers in plant science · 2026*
  - via `-`
- `PMID:42033883` — **Post-treatment paternity in testicular cancer survivors: Do demographic variables matter?** — *Cancer epidemiology · 2026*
  - via `-`
- `PMID:40324110` — **Key Updates in Testicular Cancer: Optimizing Survivorship and Survival.** — *American Society of Clinical Oncology educational book. American Society of Clinical Oncology. Annual Meeting · 2025*
  - via `-`
- `PMID:11990381` — **UGT1A1*28 polymorphism as a determinant of irinotecan disposition and toxicity.** — *The pharmacogenomics journal · 2002*
  - via `clinpgx_citation`
- `PMID:15007088` — **Genetic variants in the UDP-glucuronosyltransferase 1A1 gene predict the risk of severe neutropenia of irinotecan.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2004*
  - via `clinpgx_citation`

</details>

### Phase 6 — open LLM search

**Genes:** COMT, GSTM1, TPMT  ·  **Evidence:** 30 refs, 19 papers

Cisplatin-induced ototoxicity risk in pediatric cancer patients is primarily associated with the GSTM1 (non-null) genotype, which has been linked to an increased susceptibility to hearing damage due to cisplatin. Other genes such as TPMT and COMT also play a role but require further validation. The biological mechanism likely involves impaired detoxification of reactive metabolites generated by cisplatin, leading to oxidative stress and cellular damage in the auditory system. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could help identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower ototoxicity profile.

<details><summary>Papers retrieved</summary>

- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity gstm1`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `llm_topic:tpmt cisplatin ototoxicity`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:comt variant ototoxicity`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42631829` — **Inner Ear Organoids: Recent Progress and Challenges.** — *Stem cell reviews and reports · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:18775689` — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:16621695` — **Cloning and characterization of a new multi-stress inducible metallothionein gene in Tetrahymena pyriformis.** — *Protist · 2006*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:COMT rs4646316`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:COMT rs4646316`
- `PMID:42597480` — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42577562` — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42634570` — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2`
- `PMID:42634542` — **Mumio Potentiates Temozolomide by Inducing Apoptosis and Ferroptosis in Glioblastoma Cells.** — *Current pharmaceutical design · 2026*
  - via `llm_topic:NRF2`
- `PMID:42635394` — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`
- `PMID:42635355` — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`

</details>

### Phase 7 — open search + full text

**Genes:** COMT, GSTM1, TPMT  ·  **Evidence:** 30 refs, 19 papers

Cisplatin-induced ototoxicity risk in pediatric cancer patients is primarily associated with the GSTM1 (non-null) genotype, which has been linked to an increased susceptibility to hearing damage due to cisplatin. Other genes such as TPMT and COMT also play a role but require further validation. The biological mechanism likely involves impaired detoxification of reactive metabolites generated by cisplatin, leading to oxidative stress and cellular damage in the auditory system. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could help identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower ototoxicity profile.

<details><summary>Papers retrieved</summary>

- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity gstm1`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `llm_topic:tpmt cisplatin ototoxicity`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:comt variant ototoxicity`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42631829` — **Inner Ear Organoids: Recent Progress and Challenges.** — *Stem cell reviews and reports · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:18775689` — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:16621695` — **Cloning and characterization of a new multi-stress inducible metallothionein gene in Tetrahymena pyriformis.** — *Protist · 2006*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:COMT rs4646316`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:COMT rs4646316`
- `PMID:42597480` — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42577562` — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42634570` — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2`
- `PMID:42634542` — **Mumio Potentiates Temozolomide by Inducing Apoptosis and Ferroptosis in Glioblastoma Cells.** — *Current pharmaceutical design · 2026*
  - via `llm_topic:NRF2`
- `PMID:42635394` — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`
- `PMID:42635355` — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`

</details>

### Phase 8 — combined-topic search

**Genes:** GSTM1  ·  **Evidence:** 22 refs, 11 papers

GSTM1 non-null is the primary genetic variant linked to cisplatin-induced ototoxicity in pediatric cancer patients, with moderate evidence (PharmGKB Level 3). The biological mechanism likely involves impaired glutathione metabolism, as GSTM1 encodes a protein involved in detoxifying reactive metabolites of cisplatin. This impairment may lead to increased cellular damage and subsequent hearing loss. For drug discovery and patient safety, pre-treatment screening for the GSTM1 non-null variant could help identify patients at higher risk of ototoxicity, potentially allowing dose adjustments or consideration of alternative agents such as carboplatin.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND COMT AND rs4646316` — 3 terms, 0 back-off(s), 2 hit(s)
- `ototoxicity AND children` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ototoxicity AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric cancer patients AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 GSTM1 non-null AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `TPMT TPMT*1 AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `COMT rs4646316 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `ROS-triggered ferroptosis AND cisplatin` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity AND children` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND COMT AND rs4646316` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:39386217` — **GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-triggered ferroptosis.** — *Frontiers in immunology · 2024*
  - via `combo2:cisplatin + GSTM1`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `combo2:cisplatin + TPMT`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `combo3:cisplatin + COMT + rs4646316`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `combo2:cisplatin + ototoxicity`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `combo2:cisplatin + ototoxicity`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `combo3:pediatric cancer patients + cisplatin + ototoxicity`
- `PMID:42443713` — **Longitudinal Audiological and Vestibular Follow-up in Adult Cancer Patients Receiving Platinum-Based Chemotherapy.** — *Journal of the Association for Research in Otolaryngology : JARO · 2026*
  - via `combo3:pediatric cancer patients + cisplatin + ototoxicity`
- `PMID:30113582` — **[The analysis of the association of the polymorphic variants of the TPMT, COMT, and ABCC3 genes with the development of hearing disorders induced by the cisplatin treatment].** — *Vestnik otorinolaringologii · 2018*
  - via `combo3:COMT rs4646316 + cisplatin + ototoxicity`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `combo3:GSTT1 + cisplatin + ototoxicity`
- `PMID:36980643` — **Association of Clinical Aspects and Genetic Variants with the Severity of Cisplatin-Induced Ototoxicity in Head and Neck Squamous Cell Carcinoma: A Prospective Cohort Study.** — *Cancers · 2023*
  - via `combo3:GSTT1 + cisplatin + ototoxicity`
- `PMID:42476462` — **Bioinspired platelet membrane-cloaked ROS-responsive nanozymes enable synergistic therapy of acute kidney injury via immunomodulation and ferroptosis suppression.** — *Journal of controlled release : official journal of the Controlled Release Society · 2026*
  - via `combo2:ROS-triggered ferroptosis + cisplatin`

</details>

### Phase 9 — combined + full text

**Genes:** GSTM1, TPMT  ·  **Evidence:** 23 refs, 12 papers, 1 full text

GSTM1 non-null is the primary genetic variant associated with increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, although evidence linking TPMT variants to this adverse effect is also present but less reliable. The biological mechanism likely involves GSTM1's role in glutathione metabolism, which may influence the detoxification and cellular damage caused by cisplatin. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could help identify patients at higher risk of ototoxicity, potentially guiding dose adjustments or alternative therapeutic strategies to mitigate this side effect.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND COMT AND rs4646316` — 3 terms, 0 back-off(s), 2 hit(s)
- `ototoxicity AND children` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ototoxicity AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric cancer patients AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 GSTM1 non-null AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `TPMT TPMT*1 AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `COMT rs4646316 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `ROS-triggered ferroptosis AND cisplatin` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity AND children` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND COMT AND rs4646316` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:39386217` — **GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-triggered ferroptosis.** — *Frontiers in immunology · 2024*
  - via `combo2:cisplatin + GSTM1`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `combo2:cisplatin + TPMT`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `combo3:cisplatin + COMT + rs4646316`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `combo2:cisplatin + ototoxicity`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `combo2:cisplatin + ototoxicity`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `combo3:pediatric cancer patients + cisplatin + ototoxicity`
- `PMID:42443713` — **Longitudinal Audiological and Vestibular Follow-up in Adult Cancer Patients Receiving Platinum-Based Chemotherapy.** — *Journal of the Association for Research in Otolaryngology : JARO · 2026*
  - via `combo3:pediatric cancer patients + cisplatin + ototoxicity`
- `PMID:30113582` — **[The analysis of the association of the polymorphic variants of the TPMT, COMT, and ABCC3 genes with the development of hearing disorders induced by the cisplatin treatment].** — *Vestnik otorinolaringologii · 2018*
  - via `combo3:COMT rs4646316 + cisplatin + ototoxicity`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `combo3:GSTT1 + cisplatin + ototoxicity`
- `PMID:36980643` — **Association of Clinical Aspects and Genetic Variants with the Severity of Cisplatin-Induced Ototoxicity in Head and Neck Squamous Cell Carcinoma: A Prospective Cohort Study.** — *Cancers · 2023*
  - via `combo3:GSTT1 + cisplatin + ototoxicity`
- `PMID:42476462` — **Bioinspired platelet membrane-cloaked ROS-responsive nanozymes enable synergistic therapy of acute kidney injury via immunomodulation and ferroptosis suppression.** — *Journal of controlled release : official journal of the Controlled Release Society · 2026*
  - via `combo2:ROS-triggered ferroptosis + cisplatin`
- `PMID:39386217/PMC11461197` — **GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-triggered ferroptosis.** — *Frontiers in immunology · 2024*
  - via `combo2:cisplatin + GSTM1+pmc_xml`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** COMT, GSTM1, TPMT  ·  **Evidence:** 17 refs, 5 papers

The genes/variants implicated in cisplatin-induced ototoxicity risk in pediatric cancer patients include GSTM1 non-null, TPMT*1, and COMT (rs4646316). The biological mechanism likely involves genetic polymorphisms affecting drug metabolism and detoxification pathways. For instance, GSTM1 non-null may indicate reduced ability to metabolize cisplatin efficiently, leading to increased ototoxicity risk. However, the evidence for TPMT*1 is conflicting, while COMT (rs4646316) shows a consistent association with increased ototoxicity risk. These findings suggest that pre-treatment biomarker screening could help identify patients at higher risk and potentially guide dose adjustments or alternative agent selection to mitigate adverse effects.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND TPMT AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `COMT AND cisplatin ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND deafness AND pediatric AND cancer` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity AND pediatric` — 3 terms, 0 back-off(s), 2 hit(s)
- `COMT/rs4646316 AND cisplatin AND ear toxicity` — 2 terms, 1 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `free1:cisplatin ototoxicity[mh]`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `free3:(GSTM1 OR TPMT) AND cisplatin`
- `PMID:28445188` — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - via `free2:COMT AND "cisplatin ototoxicity"`
- `PMID:42637664` — **Non-invasive colorectal cancer screening in cystic fibrosis: Promise, pitfalls, and future directions.** — *Journal of cystic fibrosis : official journal of the European Cystic Fibrosis Society · 2026*
  - via `free2:(pediatric OR child*) AND cancer`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(GSTM1 OR GSTT1) AND cisplatin AND hearing loss`

</details>

### Phase 11 — evidence ledger

**Genes:** COMT, GSTM1, TPMT  ·  **Evidence:** 17 refs, 5 papers

The risk of cisplatin-induced ototoxicity in pediatric cancer patients is associated with genetic variants such as GSTM1 non-null, TPMT *1, and COMT rs4646316. The biological mechanism underlying these associations likely involves the role of these genes in drug metabolism and detoxification pathways, which can influence how cisplatin is processed and its subsequent effects on auditory function. For instance, GSTM1 and TPMT are involved in glutathione conjugation and thiopurine S-methyltransferase activity respectively, both critical for detoxifying reactive metabolites of drugs like cisplatin. The COMT variant may affect dopamine metabolism, which could indirectly influence ototoxicity through neuroprotective pathways. These findings have implications for drug development by highlighting the need to consider genetic factors in clinical trials and patient safety by suggesting that biomarker screening for these variants could help identify patients at higher risk of ototoxicity, potentially guiding dose adjustments or alternative therapeutic strategies.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND TPMT AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `COMT AND cisplatin ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND deafness AND pediatric AND cancer` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pediatric AND cancer` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics AND ototoxicity` — 2 terms, 1 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity AND pediatric` — 3 terms, 0 back-off(s), 2 hit(s)
- `COMT/rs4646316 AND cisplatin AND ear toxicity` — 2 terms, 1 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `free1:cisplatin ototoxicity[mh]`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `free3:(GSTM1 OR TPMT) AND cisplatin`
- `PMID:28445188` — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - via `free2:COMT AND "cisplatin ototoxicity"`
- `PMID:42644840` — **Organization of skin ulcer outpatient clinics in Italy: results from a survey of the Study Group on Ulcers of the Italian Society of Dermatology and Venereology.** — *Italian journal of dermatology and venereology · 2026*
  - via `free2:(pediatric OR child*) AND cancer`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(GSTM1 OR GSTT1) AND cisplatin AND hearing loss`

</details>

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

### Baseline A — no external sources

**Genes:** TPMT  ·  **Evidence:** 0 refs, 0 papers

The TPMT variant is not directly implicated in the ototoxicity associated with cisplatin treatment for Neuroblastoma. However, it highlights individual variability in drug response and emphasizes the need to monitor patients closely for side effects like hearing loss due to cisplatin's inherent ototoxic properties. The primary biological mechanism involves cisplatin-induced damage to auditory hair cells, leading to irreversible hearing impairment. For patient safety, pre-treatment screening for genetic variants that may influence drug metabolism or toxicity is recommended, alongside careful dose adjustment and regular audiometric monitoring during treatment.

### Baseline B — paper setup

**Genes:** TPMT  ·  **Evidence:** 0 refs, 0 papers

The TPMT variant is implicated in the increased risk of ototoxicity associated with cisplatin treatment for Neuroblastoma. The reduced activity of the TPMT enzyme due to this genetic variation leads to impaired metabolism and clearance of toxic metabolites, potentially exacerbating side effects such as hearing loss. For drug discovery and patient safety, pre-treatment screening for TPMT variants is crucial to identify patients at higher risk. Dose adjustments or alternative agents with a lower ototoxicity profile should be considered in these cases to mitigate adverse reactions.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTM1, TPMT  ·  **Evidence:** 0 refs, 0 papers

The TPMT variant is implicated in the high risk for hearing loss associated with cisplatin treatment in your daughter's case. This genetic variation affects drug metabolism, potentially increasing susceptibility to ototoxicity from cisplatin. Other genetic factors like GSTM1 may also modulate this response. For patient safety and effective drug discovery, pre-treatment biomarker screening for TPMT variants is crucial to identify patients at higher risk of adverse effects. Dose adjustment or alternative agents should be considered based on the identified genetic profile.

### Phase 3 — ClinPGx only

**Genes:** GSTM1, TPMT  ·  **Evidence:** 7 refs, 0 papers

The TPMT variant is implicated in the high risk for hearing loss associated with cisplatin treatment in your daughter's case. This genetic variation affects drug metabolism, potentially increasing susceptibility to ototoxicity from cisplatin. Other genetic factors like GSTM1 may also modulate this response. For patient safety and effective drug discovery, pre-treatment biomarker screening for TPMT variants is crucial to identify patients at higher risk of adverse effects. Dose adjustment or alternative agents should be considered based on the identified genetic profile.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** ACYP2, GSTM1, TPMT  ·  **Evidence:** 24 refs, 17 papers

The high risk of hearing loss in your daughter while on cisplatin for Neuroblastoma is likely influenced by genetic factors including TPMT, ACYP2 (rs1872328), and GSTM1. The biological mechanism involves altered drug metabolism and detoxification pathways that may exacerbate ototoxicity due to these variants. For patient safety, pre-treatment biomarker screening for these variants should be considered to identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower risk of ototoxicity.

<details><summary>Papers retrieved</summary>

- `PMID:25665007` — **Common variants in ACYP2 influence susceptibility to cisplatin-induced hearing loss.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:26928270` — **Replication of a genetic variant in ACYP2 associated with cisplatin-induced hearing loss in patients with osteosarcoma.** — *Pharmacogenetics and genomics · 2016*
  - via `clinpgx_citation`
- `PMID:28445188` — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - via `clinpgx_citation`
- `PMID:10376773` — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - via `clinpgx_citation`
- `PMID:10734022` — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:42598616` — **Prenatally detected fetus in fetu with progressive imaging organization: Multimodality radiology-pathology correlation.** — *Radiology case reports · 2026*
  - via `-`
- `PMID:42595252` — **URG7-Driven Homeostatic Adaptation Protects SH-SY5Y Cells from 6-OHDA Neurotoxicity.** — *Journal of molecular biology · 2026*
  - via `-`
- `PMID:42592166` — **Over-the-counter hearing aids and integrated health-monitoring sensors: a review of clinical evidence and implementation.** — *Frontiers in digital health · 2026*
  - via `-`
- `PMID:42581014` — **Goal-setting in audiology: where practice aligns with, or falls short of, best practice.** — *International journal of audiology · 2026*
  - via `-`
- `PMID:12127547` — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - via `clinpgx_citation`
- `PMID:18830133` — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - via `clinpgx_citation`
- `PMID:42598053` — **The road from standardized to personalized medicine: the difficult-to-treat framework as a critical waystation.** — *Frontiers in medicine · 2026*
  - via `-`
- `PMID:42597842` — **HIPK4 is a novel gene associated with teratozoospermia and male infertility.** — *Human reproduction open · 2026*
  - via `-`
- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTM1, TPMT  ·  **Evidence:** 25 refs, 15 papers

The TPMT variant and GSTM1 polymorphism are implicated in the increased risk of cisplatin-induced hearing loss. The biological mechanism involves altered drug metabolism due to reduced TPMT activity, leading to higher levels of toxic metabolites that can cause ototoxicity. Additionally, GSTM1 variants may impair detoxification pathways, further exacerbating this risk. For patient safety and drug discovery, pre-treatment genetic screening for these variants is crucial to identify high-risk patients who might benefit from dose adjustments or alternative agents with lower ototoxic potential.

<details><summary>Papers retrieved</summary>

- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:23274376` — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - via `clinpgx_citation`
- `PMID:10376773` — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - via `clinpgx_citation`
- `PMID:10734022` — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:42598616` — **Prenatally detected fetus in fetu with progressive imaging organization: Multimodality radiology-pathology correlation.** — *Radiology case reports · 2026*
  - via `-`
- `PMID:42595252` — **URG7-Driven Homeostatic Adaptation Protects SH-SY5Y Cells from 6-OHDA Neurotoxicity.** — *Journal of molecular biology · 2026*
  - via `-`
- `PMID:12127547` — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - via `clinpgx_citation`
- `PMID:18830133` — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - via `clinpgx_citation`
- `PMID:21435719` — **Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide.** — *Leukemia research · 2011*
  - via `clinpgx_citation`
- `PMID:25188725` — **Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia.** — *Clinical pharmacology and therapeutics · 2014*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`

</details>

### Phase 6 — open LLM search

**Genes:** TPMT  ·  **Evidence:** 26 refs, 19 papers

The TPMT variant is implicated in the increased risk of cisplatin-induced ototoxicity in your daughter. This genetic variation affects drug metabolism, leading to reduced detoxification and potentially higher levels of cisplatin in her system, thereby increasing the likelihood of hearing loss. For patient safety, pre-treatment screening for TPMT variants should be conducted to identify patients at high risk. Dose adjustments or alternative agents such as carboplatin may need to be considered based on genetic profiles.

<details><summary>Papers retrieved</summary>

- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `llm_topic:cisplatin ototoxicity tpmt`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `llm_topic:neuroblastoma hearing loss risk`
- `PMID:28406961` — **Pharmacogenetic variants in TPMT alter cellular responses to cisplatin in inner ear cell lines.** — *PloS one · 2017*
  - via `llm_topic:tpmt variant cisplatin toxicity`
- `PMID:42560154` — **Clinical Functional Assignment of TPMT and NUDT15 Alleles by the Clinical Pharmacogenetics Implementation Consortium Pharmacogene Curation Expert Panel.** — *Clinical pharmacology and therapeutics · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42560047` — **Pharmacogenomic biomarkers in oncology: evidence, clinical utility, and barriers to implementation.** — *Journal of chemotherapy (Florence, Italy) · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634987` — **Unveiling the neurodevelopmental toxicity of PFOA and PFOS: evidence from integration of in silico and in vitro study.** — *Toxicology mechanisms and methods · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42634612` — **Radiographic overestimation of inferior vena cava involvement in pediatric neuroblastoma: a case report.** — *Journal of surgical case reports · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42634792` — **Hearing Aids Use Preferences Among Older Adults with Hearing Loss: A Discrete Choice Experiment.** — *Patient preference and adherence · 2026*
  - via `llm_topic:audiologist`
- `PMID:42625608` — **Factors influencing the professional quality of life in South African audiologists.** — *Frontiers in psychology · 2026*
  - via `llm_topic:audiologist`
- `PMID:42635394` — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635355` — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635234` — **Discovering reference-missing cell types in bulk transcriptomics.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic reason`
- `PMID:42634009` — **Immune-Enriched Versus Matrix-Remodeling Microenvironments in Psammoma Body-Rich and Psammoma Body-Poor WHO Grade I Meningiomas: An Exploratory Transcriptomic Study.** — *Neuropathology : official journal of the Japanese Society of Neuropathology · 2026*
  - via `llm_topic:genetic reason`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:36672743` — **Molecular Characterization of Tropomyosin and Its Potential Involvement in Muscle Contraction in Pacific Abalone.** — *Genes · 2022*
  - via `llm_topic:TPMT*1`
- `PMID:18775689` — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT*1`

</details>

### Phase 7 — open search + full text

**Genes:** ACYP2, GSTM1, TPMT  ·  **Evidence:** 28 refs, 19 papers

The TPMT variant is a key genetic factor implicated in the ototoxicity associated with cisplatin treatment for Neuroblastoma. This variant affects drug metabolism, potentially leading to higher levels of cisplatin and increased risk of hearing loss due to impaired detoxification pathways. Additionally, other genetic variants such as ACYP2 (rs1872328) and GSTM1 also modulate the response to cisplatin, further exacerbating ototoxic effects. For drug discovery and patient safety, pre-treatment biomarker screening for TPMT and related genes is crucial to identify high-risk patients who may benefit from dose adjustments or alternative agents with lower ototoxic potential.

<details><summary>Papers retrieved</summary>

- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:TPMT variant ototoxicity`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `llm_topic:cisplatin neuroblastoma hearing`
- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `llm_topic:ACYP2 cisplatin ototoxicity`
- `PMID:42560154` — **Clinical Functional Assignment of TPMT and NUDT15 Alleles by the Clinical Pharmacogenetics Implementation Consortium Pharmacogene Curation Expert Panel.** — *Clinical pharmacology and therapeutics · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42560047` — **Pharmacogenomic biomarkers in oncology: evidence, clinical utility, and barriers to implementation.** — *Journal of chemotherapy (Florence, Italy) · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634987` — **Unveiling the neurodevelopmental toxicity of PFOA and PFOS: evidence from integration of in silico and in vitro study.** — *Toxicology mechanisms and methods · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42634612` — **Radiographic overestimation of inferior vena cava involvement in pediatric neuroblastoma: a case report.** — *Journal of surgical case reports · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42635394` — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing loss`
- `PMID:42635355` — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing loss`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:31666714` — **Genetic variation of cisplatin-induced ototoxicity in non-cranial-irradiated pediatric patients using a candidate gene approach: The International PanCareLIFE Study.** — *The pharmacogenomics journal · 2020*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42634458` — **[Perioperative Safety Analysis of Preoperative Targeted Therapy in Patients with ALK-positive Non-small Cell Lung Cancer].** — *Zhongguo fei ai za zhi = Chinese journal of lung cancer · 2026*
  - via `llm_topic:Brain Neoplasms`
- `PMID:42634231` — **Refractory Hyperammonemic Encephalopathy as a Paraneoplastic Presentation of Fibrolamellar Hepatocellular Carcinoma: A Case Report.** — *The American journal of case reports · 2026*
  - via `llm_topic:Brain Neoplasms`
- `PMID:42635414` — **The Ergonomics of Endoscopic Ear Surgery: An International Survey.** — *Otology & neurotology : official publication of the American Otological Society, American Neurotology Society [and] European Academy of Otology and Neurotology · 2026*
  - via `llm_topic:Deafness`
- `PMID:42633998` — **Transcanal Cochlear Implantation Under Endoscopic Guidance with Canal Closure in a Pediatric Patient with CHARGE Syndrome: A Case Report and Surgical Technique.** — *Acta medica Okayama · 2026*
  - via `llm_topic:Deafness`

</details>

### Phase 8 — combined-topic search

**Genes:** TPMT  ·  **Evidence:** 22 refs, 13 papers

The TPMT variant is implicated in the increased risk of ototoxicity when a patient undergoes cisplatin treatment for Neuroblastoma. The reduced activity of the TPMT enzyme due to genetic variation leads to higher levels of toxic metabolites, which can damage auditory hair cells and cause hearing loss. For drug discovery and patient safety, pre-treatment biomarker screening for TPMT variants should be considered to identify patients at high risk of ototoxicity. Dose adjustment or alternative agents with lower ototoxic potential may also need to be explored.

<details><summary>Queries issued (combined terms)</summary>

- `TPMT AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity AND children` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND neuroblastoma AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `COMT AND drug toxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)
- `Neuroblastoma AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 non-null AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `COMT rs4646316 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `ototoxicity AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `Deafness AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND hearing loss AND children` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT*1 AND neuroblastoma` — 2 terms, 0 back-off(s), 0 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `combo3:TPMT + cisplatin + ototoxicity`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `combo3:GSTM1 + ototoxicity + children`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `combo3:cisplatin + neuroblastoma + hearing loss`
- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `combo3:TPMT variant + cisplatin + hearing loss`
- `PMID:36917731` — **Role of Cisplatin Dose Intensity and TPMT Variation in the Development of Hearing Loss in Children.** — *Therapeutic drug monitoring · 2023*
  - via `combo3:TPMT variant + cisplatin + hearing loss`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:42617317` — **Honokiol-mediated reversal of cisplatin-induced transcriptomic changes in outer hair cells.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:40128126` — **Feasibility and Safety of Intratympanic Administration of Sustained-Exposure Dexamethasone Thermosensitive Gel (OTO-104) for Prevention of Cisplatin-Induced Hearing Loss in Children: A Multisite Phase 2 Randomized Clinical Trial.** — *Pediatric blood & cancer · 2025*
  - via `combo3:Neuroblastoma + cisplatin + hearing loss`
- `PMID:30113582` — **[The analysis of the association of the polymorphic variants of the TPMT, COMT, and ABCC3 genes with the development of hearing disorders induced by the cisplatin treatment].** — *Vestnik otorinolaringologii · 2018*
  - via `combo3:COMT rs4646316 + cisplatin + hearing loss`
- `PMID:28445188` — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - via `combo3:COMT rs4646316 + cisplatin + hearing loss`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `combo3:ototoxicity + cisplatin + hearing loss`
- `PMID:42203086` — **Poly(amino acid) nanoprodrugs mitigate cisplatin-induced ototoxicity.** — *Journal of controlled release : official journal of the Controlled Release Society · 2026*
  - via `combo3:Deafness + cisplatin + hearing loss`
- `PMID:41469892` — **Cisplatin Differentially Damages Mammalian Vestibular End Organs.** — *Ear and hearing*
  - via `combo3:Deafness + cisplatin + hearing loss`

</details>

### Phase 9 — combined + full text

**Genes:** ACYP2, GSTM1, TPMT  ·  **Evidence:** 21 refs, 14 papers

The TPMT variant is a key genetic factor implicated in the increased risk of cisplatin-induced hearing loss. The TPMT enzyme's reduced function due to the variant can lead to higher levels of toxic metabolites that may exacerbate ototoxicity. Additionally, other genetic factors such as ACYP2 and GSTM1 further modulate this response. For drug discovery and patient safety, pre-treatment biomarker screening for these variants is crucial to identify patients at high risk. Dose adjustment or alternative agents with lower ototoxic potential should be considered in TPMT variant carriers.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `ACYP2 AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND neuroblastoma AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)
- `Neuroblastoma AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `Hearing loss AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `Audiologist AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `ACYP2 rs1872328 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 GSTM1 non-null AND cisplatin` — 2 terms, 1 back-off(s), 0 hit(s)
- `Ototoxicity AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND TPMT` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND neuroblastoma AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `combo2:cisplatin + TPMT`
- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `combo2:ACYP2 + hearing loss`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `combo2:GSTM1 + ototoxicity`
- `PMID:36917731` — **Role of Cisplatin Dose Intensity and TPMT Variation in the Development of Hearing Loss in Children.** — *Therapeutic drug monitoring · 2023*
  - via `combo3:TPMT variant + cisplatin + hearing loss`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:42617317` — **Honokiol-mediated reversal of cisplatin-induced transcriptomic changes in outer hair cells.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo2:cisplatin + hearing loss`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `combo3:Neuroblastoma + cisplatin + hearing loss`
- `PMID:40128126` — **Feasibility and Safety of Intratympanic Administration of Sustained-Exposure Dexamethasone Thermosensitive Gel (OTO-104) for Prevention of Cisplatin-Induced Hearing Loss in Children: A Multisite Phase 2 Randomized Clinical Trial.** — *Pediatric blood & cancer · 2025*
  - via `combo3:Neuroblastoma + cisplatin + hearing loss`
- `PMID:41239162` — **Where are audiologists in the room of wizards? Oncology patient experiences with audiology in an Australian public hospital.** — *Journal of cancer survivorship : research and practice · 2025*
  - via `combo3:Audiologist + cisplatin + hearing loss`
- `PMID:37887850` — **Practice of Monitoring Cisplatin-Induced Ototoxicity by Audiology, ENT, and Oncology Specialists: A Survey-Based Study in a Single Italian Medical Center.** — *Audiology research · 2023*
  - via `combo3:Audiologist + cisplatin + hearing loss`
- `PMID:31666714` — **Genetic variation of cisplatin-induced ototoxicity in non-cranial-irradiated pediatric patients using a candidate gene approach: The International PanCareLIFE Study.** — *The pharmacogenomics journal · 2020*
  - via `combo3:ACYP2 rs1872328 + cisplatin + hearing loss`
- `PMID:30837596` — **The genetic vulnerability to cisplatin ototoxicity: a systematic review.** — *Scientific reports · 2019*
  - via `combo3:ACYP2 rs1872328 + cisplatin + hearing loss`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `combo3:Ototoxicity + cisplatin + hearing loss`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `combo3:GSTM1 + cisplatin + ototoxicity`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** GSTM1, NFE2L2, TPMT  ·  **Evidence:** 15 refs, 7 papers, 1 full text

Your daughter's TPMT variant is a key genetic factor implicated in her high risk for cisplatin-induced hearing loss. The TPMT enzyme metabolizes thiopurine drugs, but its role in cisplatin metabolism and ototoxicity remains debated; however, recent studies suggest that TPMT variants may influence susceptibility to cisplatin's neurotoxic effects through inflammatory pathways. For drug discovery and patient safety, pre-treatment genetic screening for TPMT variants is crucial to identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents like carboplatin if feasible.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `TPMT/TPMT variant AND cisplatin AND neuroblastoma` — 2 terms, 1 back-off(s), 2 hit(s)
- `hearing loss AND pharmacogenomics` — 2 terms, 1 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `TPMT/GSTM1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `Neuroblastoma AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND hearing loss` — 1 terms, 2 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `free3:(TPMT OR TPMT variant) AND cisplatin`
- `PMID:42524757` — **MT-RNR1 genotype testing for preventing aminoglycoside-mediated ototoxicity: A guideline developed by the UK Centre of Excellence in Regulatory Science and Innovation in Pharmacogenomics (CERSI-PGx).** — *British journal of clinical pharmacology · 2026*
  - via `free2:hearing loss AND pharmacogenomics`
- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `free2:TPMT variant AND cisplatin`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `free2:"hearing loss"[tiab] AND Neuroblastoma`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity+pmc_xml`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(TPMT OR GSTM1) AND cisplatin AND hearing loss`

</details>

### Phase 11 — evidence ledger

**Genes:** GSTT1, NFE2L2, TPMT  ·  **Evidence:** 15 refs, 7 papers, 1 full text

Your daughter's TPMT variant increases her risk for cisplatin-induced ototoxicity due to altered drug metabolism, potentially leading to higher levels of the toxic compound in her system. The genetic variants GSTT1 and NRF2 also contribute to increased susceptibility to hearing loss from cisplatin treatment, as they affect antioxidant defense mechanisms crucial for mitigating oxidative stress caused by the drug. Given these factors, it is advisable to closely monitor your daughter's auditory function during cisplatin therapy and consider alternative treatments or adjunctive therapies that might reduce ototoxicity risks while maintaining effective cancer management.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `TPMT/TPMT variant AND cisplatin AND neuroblastoma` — 2 terms, 1 back-off(s), 2 hit(s)
- `hearing loss AND pharmacogenomics` — 2 terms, 1 back-off(s), 2 hit(s)
- `GSTM1/GSTT1 AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `hearing loss AND Neuroblastoma` — 2 terms, 0 back-off(s), 2 hit(s)
- `TPMT AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND genetic risk factors` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `TPMT/GSTM1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `Neuroblastoma AND cisplatin AND ototoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `TPMT variant AND hearing loss` — 1 terms, 2 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity`
- `PMID:41637682` — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `free3:(TPMT OR TPMT variant) AND cisplatin`
- `PMID:42524757` — **MT-RNR1 genotype testing for preventing aminoglycoside-mediated ototoxicity: A guideline developed by the UK Centre of Excellence in Regulatory Science and Innovation in Pharmacogenomics (CERSI-PGx).** — *British journal of clinical pharmacology · 2026*
  - via `free2:hearing loss AND pharmacogenomics`
- `PMID:37726872` — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `free2:TPMT variant AND cisplatin`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `free2:"hearing loss"[tiab] AND Neuroblastoma`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity+pmc_xml`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(TPMT OR GSTM1) AND cisplatin AND hearing loss`

</details>

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

### Baseline A — no external sources

**Genes:** GSTT1  ·  **Evidence:** 0 refs, 0 papers

The permanent inner ear damage experienced by the child after Platinol (cisplatin) treatment may be influenced by their GSTT1 status, a genetic factor involved in drug metabolism. The GSTT1 gene encodes glutathione S-transferase theta 1, which plays a role in detoxifying and eliminating xenobiotics like cisplatin from the body. Individuals with null GSTT1 genotype have reduced capacity to metabolize and excrete cisplatin efficiently, potentially increasing their risk for ototoxicity. For drug discovery and patient safety, pre-treatment genetic screening for GSTT1 status could help identify patients at higher risk of developing severe side effects like inner ear damage. This information can guide dose adjustments or the selection of alternative agents to minimize toxicity.

### Baseline B — paper setup

**Genes:** GSTT1  ·  **Evidence:** 0 refs, 0 papers

The permanent inner ear damage experienced by the child after receiving Platinol (cisplatin) may be influenced by their GSTT1 status, a genetic factor that affects drug metabolism. The evidence suggests a plausible biological mechanism where individuals with certain GSTT1 statuses might have altered cisplatin metabolism or detoxification processes, potentially increasing susceptibility to ototoxicity. For future drug discovery and patient safety, pre-treatment biomarker screening for GSTT1 status could help identify patients at higher risk of developing this adverse reaction, allowing for dose adjustments or the use of alternative agents such as carboplatin.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTT1  ·  **Evidence:** 0 refs, 0 papers

The GSTT1 status is a genetic factor potentially linked to the occurrence of inner ear damage in patients treated with Platinol (cisplatin). The biological mechanism likely involves variations in glutathione S-transferase theta 1 (GSTT1) affecting the detoxification and clearance of cisplatin, thereby increasing susceptibility to ototoxicity. For drug discovery and patient safety, pre-treatment genetic screening for GSTT1 status could help identify patients at higher risk of developing inner ear damage, allowing for dose adjustments or consideration of alternative agents such as carboplatin.

### Phase 3 — ClinPGx only

**Genes:** GSTT1  ·  **Evidence:** 8 refs, 0 papers

The GSTT1 status is a genetic factor potentially linked to the occurrence of inner ear damage in patients treated with Platinol (cisplatin). The biological mechanism likely involves variations in glutathione S-transferase theta 1 (GSTT1) affecting the detoxification and clearance of cisplatin, thereby increasing susceptibility to ototoxicity. For drug discovery and patient safety, pre-treatment genetic screening for GSTT1 status could help identify patients at higher risk of developing inner ear damage, allowing for dose adjustments or consideration of alternative agents such as carboplatin.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** GSTT1  ·  **Evidence:** 23 refs, 13 papers

The permanent inner ear damage observed after Platinol treatment may be influenced by the GSTT1 status, a genetic polymorphism affecting glutathione S-transferase theta 1 (GSTT1), which is involved in detoxifying and metabolizing drugs like cisplatin. Individuals with a null genotype for GSTT1 have reduced capacity to metabolize these drugs, potentially leading to higher toxicity and ototoxicity. This finding underscores the importance of pre-treatment genetic screening for GSTT1 status to predict drug metabolism efficiency and adjust dosing accordingly or consider alternative agents with lower ototoxic risk.

<details><summary>Papers retrieved</summary>

- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:19620936` — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - via `clinpgx_citation`
- `PMID:21435719` — **Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide.** — *Leukemia research · 2011*
  - via `clinpgx_citation`
- `PMID:25188725` — **Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia.** — *Clinical pharmacology and therapeutics · 2014*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:19786980` — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - via `clinpgx_citation`
- `PMID:22188361` — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - via `clinpgx_citation`
- `PMID:18473752` — **A carboxylesterase 2 gene polymorphism as predictor of capecitabine on response and time to progression.** — *Current drug metabolism · 2008*
  - via `clinpgx_citation`
- `PMID:19458626` — **SNP analyses in cytarabine metabolizing enzymes in AML patients and their impact on treatment response and patient survival: identification of CDA SNP C-451T as an independent prognostic parameter for survival.** — *Leukemia · 2009*
  - via `clinpgx_citation`
- `PMID:42165380` — **Association of XPD Gene Polymorphisms with Cutaneous Melanoma Risk: A Meta-Analysis and Trial Sequence Evaluation.** — *Cancer investigation · 2026*
  - via `-`
- `PMID:42109639` — **A meta-analysis and expression profiling of DNA repair gene polymorphisms in leukemia.** — *Frontiers in oncology · 2026*
  - via `-`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTT1  ·  **Evidence:** 24 refs, 14 papers, 1 full text

The permanent inner ear damage observed after Platinol treatment may be influenced by the child's GSTT1 status, a genetic polymorphism that affects drug metabolism and detoxification. The GSTT1 gene encodes glutathione S-transferase theta 1, which is involved in the conjugation of xenobiotics like cisplatin with glutathione for excretion or detoxification. Individuals lacking functional GSTT1 may have reduced capacity to metabolize Platinol efficiently, potentially increasing susceptibility to ototoxicity. For drug discovery and patient safety, pre-treatment screening for GSTT1 status could help identify patients at higher risk of adverse reactions, allowing for dose adjustments or the use of alternative agents such as carboplatin.

<details><summary>Papers retrieved</summary>

- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:19620936` — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - via `clinpgx_citation`
- `PMID:21435719` — **Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide.** — *Leukemia research · 2011*
  - via `clinpgx_citation`
- `PMID:25188725` — **Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia.** — *Clinical pharmacology and therapeutics · 2014*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:19786980` — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - via `clinpgx_citation`
- `PMID:22188361` — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - via `clinpgx_citation`
- `PMID:18473752` — **A carboxylesterase 2 gene polymorphism as predictor of capecitabine on response and time to progression.** — *Current drug metabolism · 2008*
  - via `clinpgx_citation`
- `PMID:19458626` — **SNP analyses in cytarabine metabolizing enzymes in AML patients and their impact on treatment response and patient survival: identification of CDA SNP C-451T as an independent prognostic parameter for survival.** — *Leukemia · 2009*
  - via `clinpgx_citation`
- `PMID:42165380` — **Association of XPD Gene Polymorphisms with Cutaneous Melanoma Risk: A Meta-Analysis and Trial Sequence Evaluation.** — *Cancer investigation · 2026*
  - via `-`
- `PMID:42109639` — **A meta-analysis and expression profiling of DNA repair gene polymorphisms in leukemia.** — *Frontiers in oncology · 2026*
  - via `-`
- `PMID:15213713/PMC2409815` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation+pmc_xml`

</details>

### Phase 6 — open LLM search

**Genes:** GSTT1  ·  **Evidence:** 28 refs, 19 papers

The adverse reaction of inner ear damage following Platinol treatment is likely influenced by the GSTT1 status, as indicated by a study published in Hearing Research (2024). The GSTT1 null genotype has been associated with increased susceptibility to cisplatin-induced ototoxicity. This suggests that genetic polymorphisms affecting glutathione S-transferase activity may impair the detoxification of reactive metabolites generated during cisplatin treatment, leading to greater cellular damage in the inner ear. For drug discovery and patient safety, pre-treatment screening for GSTT1 status could help identify patients at higher risk for ototoxicity, allowing for dose adjustments or consideration of alternative agents such as carboplatin.

<details><summary>Papers retrieved</summary>

- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity GSTT1`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTT1 status hearing loss`
- `PMID:40342074` — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `llm_topic:cisplatin pharmacogenomics GSTT1`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:Platinol`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:Platinol`
- `PMID:42627828` — **Tox regulates hair cell stereocilia development and Cdh23 expression in mice and zebrafish.** — *Proceedings of the National Academy of Sciences of the United States of America · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42621021` — **NADPH oxidase 3 inhibition preserves hearing in mice after stereotactic radiosurgery.** — *Molecular therapy. Nucleic acids · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42597480` — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42511983` — **A Multilevel Redox-Based Prognostic Model for Asthma Severity: From Genotype to Serum Biomarkers.** — *Biomedicines · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634570` — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2 genes`
- `PMID:42633538` — **Platycodon grandiflorus decoction against lipopolysaccharide (LPS)-induced acute lung injury via Keap1/Nrf2/ARE signaling pathway.** — *Pakistan journal of pharmaceutical sciences · 2026*
  - via `llm_topic:NRF2 genes`

</details>

### Phase 7 — open search + full text

**Genes:** GSTT1  ·  **Evidence:** 29 refs, 20 papers, 1 full text

The GSTT1 null genotype is implicated in the increased risk for permanent inner ear damage caused by Platinol (cisplatin). The likely biological mechanism involves reduced glutathione S-transferase activity, which normally detoxifies reactive metabolites of cisplatin that can cause ototoxicity. This genetic predisposition highlights the importance of pre-treatment biomarker screening to identify patients at higher risk for adverse effects, potentially allowing for dose adjustment or selection of alternative agents such as carboplatin, which has a lower incidence of ototoxicity.

<details><summary>Papers retrieved</summary>

- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity GSTT1`
- `PMID:42382212` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTT1 status hearing loss`
- `PMID:40342074` — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `llm_topic:cisplatin pharmacogenomics GSTT1`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:Platinol`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:Platinol`
- `PMID:42627828` — **Tox regulates hair cell stereocilia development and Cdh23 expression in mice and zebrafish.** — *Proceedings of the National Academy of Sciences of the United States of America · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42621021` — **NADPH oxidase 3 inhibition preserves hearing in mice after stereotactic radiosurgery.** — *Molecular therapy. Nucleic acids · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42597480` — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42511983` — **A Multilevel Redox-Based Prognostic Model for Asthma Severity: From Genotype to Serum Biomarkers.** — *Biomedicines · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42555790` — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634570` — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2 genes`
- `PMID:42633538` — **Platycodon grandiflorus decoction against lipopolysaccharide (LPS)-induced acute lung injury via Keap1/Nrf2/ARE signaling pathway.** — *Pakistan journal of pharmaceutical sciences · 2026*
  - via `llm_topic:NRF2 genes`
- `PMID:42382212/PMC13316012` — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:gstt1 status hearing loss+pmc_xml`

</details>

### Phase 8 — combined-topic search

**Genes:** GSTT1  ·  **Evidence:** 26 refs, 18 papers

The permanent inner ear damage observed after Platinol treatment may be influenced by the child's GSTT1 status. The glutathione S-transferase theta 1 (GSTT1) gene is involved in detoxifying reactive metabolites of drugs, including cisplatin. Variants or deletions in this gene can impair the body's ability to mitigate ototoxicity caused by Platinol, potentially increasing susceptibility to inner ear damage. For drug discovery and patient safety, pre-treatment genetic screening for GSTT1 status could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or consideration of alternative agents such as carboplatin.

<details><summary>Queries issued (combined terms)</summary>

- `Platinol AND GSTT1` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `Platinol AND ototoxicity AND children` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTT1` — 2 terms, 0 back-off(s), 2 hit(s)
- `Platinol AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 status AND cisplatin` — 2 terms, 0 back-off(s), 1 hit(s)
- `inner ear damage AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin-related Ovarian Neoplasms AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 rs11615 AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM3 rs1799735 AND cisplatin` — 2 terms, 0 back-off(s), 1 hit(s)
- `CDDP AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTT1` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND inner ear damage` — 2 terms, 1 back-off(s), 1 hit(s)
- `cisplatin AND ototoxicity AND pharmacogenomics` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM3 AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:40342074` — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `combo2:Platinol + GSTT1`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `combo2:GSTT1 + ototoxicity`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `combo3:Platinol + ototoxicity + children`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `combo2:Platinol + cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `combo2:Platinol + cisplatin`
- `PMID:11477586` — **Glutathione-associated enzymes in head and neck squamous cell carcinoma and response to cisplatin-based neoadjuvant chemotherapy.** — *International journal of cancer · 2001*
  - via `combo2:GSTT1 status + cisplatin`
- `PMID:42559411` — **An engineered ferritin nanocage co-delivery system for targeted hair cells protection and hearing loss attenuation.** — *Theranostics · 2026*
  - via `combo2:inner ear damage + cisplatin`
- `PMID:42435481` — **Functionalized Biomimetic Scaffolds for Human-Derived Auditory Neural Circuit Construction.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `combo2:inner ear damage + cisplatin`
- `PMID:21664657` — **Phase II trial of intraperitoneal cisplatin combined with intravenous paclitaxel in patients with ovarian, primary peritoneal and fallopian tube cancer.** — *Gynecologic oncology · 2011*
  - via `combo2:cisplatin-related Ovarian Neoplasms + cisplatin`
- `PMID:16020136` — **Severe neurotoxicity, ototoxicity and nephrotoxicity following high-dose cisplatin and amifostine.** — *Pediatric hematology and oncology · 2005*
  - via `combo2:cisplatin-related Ovarian Neoplasms + cisplatin`
- `PMID:40526606` — **EPHX1 and ERCC2 polymorphisms are associated with cisplatin-induced nephrotoxicity and prognosis in Thai cancer patients.** — *PloS one · 2025*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39431656` — **Association of ERCC1 Gene Polymorphisms (rs3212986 and rs11615) With the Risk of Lung Cancer in a Population From Southeast Iran.** — *Journal of research in health sciences · 2024*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39516666` — **Predictive and prognostic value of excision repair cross-complementing group 1 in patients with advanced gastric cancer.** — *BJC reports · 2024*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:36397425` — **Platinum-induced ototoxicity in pediatric cancer survivors: GSTP1 c.313A>G variant association.** — *Medicine · 2022*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `combo2:GSTM3 rs1799735 + cisplatin`
- `PMID:42632512` — **LINC00941 Drives Chemoresistance via Modulating PKM2 Activity and Aerobic Glycolysis in Oral Squamous Cell Carcinoma.** — *Cancer letters · 2026*
  - via `combo2:CDDP + cisplatin`
- `PMID:42616060` — **Curcumin blocks Fusobacterium nucleatum-driven tumor progression and carcinogenesis in ESCC via inhibiting the TLR4/MYD88/TRIF/STAT3 axis.** — *Journal of gastroenterology · 2026*
  - via `combo2:CDDP + cisplatin`
- `PMID:16788422` — **Glutathione s-transferase gene polymorphisms in Italian patients with sudden sensorineural hearing loss.** — *Otology & neurotology : official publication of the American Otological Society, American Neurotology Society [and] European Academy of Otology and Neurotology · 2006*
  - via `combo2:GSTT1 + inner ear damage`

</details>

### Phase 9 — combined + full text

**Genes:** GSTT1  ·  **Evidence:** 27 refs, 19 papers, 1 full text

The permanent inner ear damage observed after Platinol treatment may be influenced by the child's GSTT1 status. The glutathione S-transferase theta 1 (GSTT1) enzyme plays a role in detoxifying cisplatin through conjugation with glutathione, and genetic variability affecting its expression or function could increase susceptibility to ototoxicity. For drug discovery and patient safety, pre-treatment screening for GSTT1 status should be considered to identify patients at higher risk of adverse effects. This information can guide dose adjustments or the selection of alternative agents to mitigate ototoxic risks.

<details><summary>Queries issued (combined terms)</summary>

- `Platinol AND GSTT1` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND ototoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `Platinol AND ototoxicity AND children` — 3 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTT1` — 2 terms, 0 back-off(s), 2 hit(s)
- `Platinol AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 status AND cisplatin` — 2 terms, 0 back-off(s), 1 hit(s)
- `inner ear damage AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin-related Ovarian Neoplasms AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 rs11615 AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM3 rs1799735 AND cisplatin` — 2 terms, 0 back-off(s), 1 hit(s)
- `CDDP AND cisplatin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTT1` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND inner ear damage` — 2 terms, 1 back-off(s), 1 hit(s)
- `cisplatin AND ototoxicity AND pharmacogenomics` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM3 AND hearing loss` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:40342074` — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `combo2:Platinol + GSTT1`
- `PMID:40222694` — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `combo2:GSTT1 + ototoxicity`
- `PMID:42504125` — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `combo3:Platinol + ototoxicity + children`
- `PMID:42636270` — **Randomized trial of adjuvant 5-FU-platinum vs paclitaxel-platinum for high-risk penile cancer.** — *Journal of the National Cancer Institute · 2026*
  - via `combo2:Platinol + cisplatin`
- `PMID:42636269` — **Concurrent chemotherapy and external radiation therapy (ConCERT): phase 3 noninferiority randomized clinical trial of cisplatin weekly vs every 3 weeks in locally advanced squamous cell carcinoma of the head and neck.** — *Journal of the National Cancer Institute · 2026*
  - via `combo2:Platinol + cisplatin`
- `PMID:11477586` — **Glutathione-associated enzymes in head and neck squamous cell carcinoma and response to cisplatin-based neoadjuvant chemotherapy.** — *International journal of cancer · 2001*
  - via `combo2:GSTT1 status + cisplatin`
- `PMID:42559411` — **An engineered ferritin nanocage co-delivery system for targeted hair cells protection and hearing loss attenuation.** — *Theranostics · 2026*
  - via `combo2:inner ear damage + cisplatin`
- `PMID:42435481` — **Functionalized Biomimetic Scaffolds for Human-Derived Auditory Neural Circuit Construction.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `combo2:inner ear damage + cisplatin`
- `PMID:21664657` — **Phase II trial of intraperitoneal cisplatin combined with intravenous paclitaxel in patients with ovarian, primary peritoneal and fallopian tube cancer.** — *Gynecologic oncology · 2011*
  - via `combo2:cisplatin-related Ovarian Neoplasms + cisplatin`
- `PMID:16020136` — **Severe neurotoxicity, ototoxicity and nephrotoxicity following high-dose cisplatin and amifostine.** — *Pediatric hematology and oncology · 2005*
  - via `combo2:cisplatin-related Ovarian Neoplasms + cisplatin`
- `PMID:40526606` — **EPHX1 and ERCC2 polymorphisms are associated with cisplatin-induced nephrotoxicity and prognosis in Thai cancer patients.** — *PloS one · 2025*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39431656` — **Association of ERCC1 Gene Polymorphisms (rs3212986 and rs11615) With the Risk of Lung Cancer in a Population From Southeast Iran.** — *Journal of research in health sciences · 2024*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39516666` — **Predictive and prognostic value of excision repair cross-complementing group 1 in patients with advanced gastric cancer.** — *BJC reports · 2024*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:36397425` — **Platinum-induced ototoxicity in pediatric cancer survivors: GSTP1 c.313A>G variant association.** — *Medicine · 2022*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `combo2:GSTM3 rs1799735 + cisplatin`
- `PMID:42632512` — **LINC00941 Drives Chemoresistance via Modulating PKM2 Activity and Aerobic Glycolysis in Oral Squamous Cell Carcinoma.** — *Cancer letters · 2026*
  - via `combo2:CDDP + cisplatin`
- `PMID:42616060` — **Curcumin blocks Fusobacterium nucleatum-driven tumor progression and carcinogenesis in ESCC via inhibiting the TLR4/MYD88/TRIF/STAT3 axis.** — *Journal of gastroenterology · 2026*
  - via `combo2:CDDP + cisplatin`
- `PMID:40342074/PMC12434574` — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `combo2:cisplatin + GSTT1+pmc_xml`
- `PMID:16788422` — **Glutathione s-transferase gene polymorphisms in Italian patients with sudden sensorineural hearing loss.** — *Otology & neurotology : official publication of the American Otological Society, American Neurotology Society [and] European Academy of Otology and Neurotology · 2006*
  - via `combo2:GSTT1 + inner ear damage`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** GSTT1  ·  **Evidence:** 12 refs, 4 papers, 1 full text

The permanent inner ear damage experienced by your child after Platinol (cisplatin) treatment may be influenced by her GSTT1 null genotype, which is associated with increased susceptibility to cisplatin-induced ototoxicity. The likely biological mechanism involves the reduced capacity of individuals lacking functional GSTT1 to metabolize or detoxify cisplatin effectively, leading to heightened cellular sensitivity and toxicity in auditory cells. For drug discovery and patient safety, pre-treatment genetic screening for GSTT1 status could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents such as carboplatin, which has a lower propensity for causing hearing loss.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND GSTP1 AND GSTT1` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin-related ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1/GSTM1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM3 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `ABCC3/GSTP1 AND cisplatin AND auditory dysfunction` — 2 terms, 1 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(GSTT1) AND cisplatin AND hearing loss`
- `PMID:42634868` — **Prunetin Attenuates Dexamethasone-Induced Pancreatic β-Cell Apoptosis: Modulation of Oxidative Stress and MAPK Signaling but Not Phosphorylated C-Abl Levels.** — *Cell biochemistry and function · 2026*
  - via `free3:GSTM1 OR GSTP1 OR GSTT1`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity+pmc_xml`

</details>

### Phase 11 — evidence ledger

**Genes:** GSTT1  ·  **Evidence:** 12 refs, 4 papers, 1 full text

The permanent inner ear damage experienced by your child after Platinol (cisplatin) treatment may be influenced by her GSTT1 status, particularly if she has a null genotype for GSTT1. The study PMID:38518393 indicates that patients with the GSTT1 null genotype are more susceptible to cisplatin-induced ototoxicity. This genetic factor could explain why your child experienced permanent inner ear damage despite receiving standard chemotherapy protocols. For drug discovery and patient safety, it is crucial to screen for GSTT1 status in patients undergoing cisplatin treatment to identify those at higher risk of ototoxicity. Biomarker screening can help tailor dosing regimens or explore alternative agents with lower ototoxic potential.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND GSTP1 AND GSTT1` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin-related ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `drug-induced hearing loss AND platinum-based chemotherapy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `GSTT1/GSTM1 AND cisplatin AND hearing loss` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM3 AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `ABCC3/GSTP1 AND cisplatin AND auditory dysfunction` — 2 terms, 1 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42633148` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity`
- `PMID:38518393` — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `free3:(GSTT1) AND cisplatin AND hearing loss`
- `PMID:42634868` — **Prunetin Attenuates Dexamethasone-Induced Pancreatic β-Cell Apoptosis: Modulation of Oxidative Stress and MAPK Signaling but Not Phosphorylated C-Abl Levels.** — *Cell biochemistry and function · 2026*
  - via `free3:GSTM1 OR GSTP1 OR GSTT1`
- `PMID:42633148/PMC13499120` — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `free2:cisplatin ototoxicity+pmc_xml`

</details>

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

### Baseline A — no external sources

**Genes:** OXR1, SLC7A11, XRCC1  ·  **Evidence:** 0 refs, 0 papers

Cisplatin is a known risk factor for peripheral neuropathy with high confidence (0.80), but the evidence does not strongly support that cisplatin directly induces genetic changes leading to predisposition for peripheral neuropathy, as the direct causal relationship has lower confidence (0.49). The implicated genes/variants in this adverse reaction include those involved in DNA repair and neurotoxicity pathways such as XRCC1, OXR1, and SLC7A11. The likely biological mechanism involves cisplatin-induced oxidative stress and DNA damage leading to neuronal cell death. For drug discovery and patient safety, pre-treatment biomarker screening for genetic variants associated with increased susceptibility to cisplatin neurotoxicity could be beneficial, along with dose adjustment based on individual pharmacogenomic profiles or consideration of alternative agents like carboplatin in high-risk patients.

### Baseline B — paper setup

**Genes:** —  ·  **Evidence:** 0 refs, 0 papers

Based on the provided knowledge graph information, cisplatin is known to be a risk factor for both genetic predisposition and peripheral neuropathy. The confidence levels indicate that there is a moderate association between cisplatin use and these conditions. Specifically, the reasoning path 'cisplatin [risk_factor_for] -> genetic predisposition' has a confidence of 0.70, suggesting that cisplatin may contribute to an increased likelihood (genetic predisposition) for certain medical conditions. However, there is no direct evidence in the knowledge graph indicating that cisplatin directly causes genetic changes leading to peripheral neuropathy. The reasoning path 'cisplatin [risk_factor_for] -> genetic predisposition [risk_factor_for] -> peripheral neuropathy' has a confidence of 0.49, which suggests an indirect relationship but does not confirm causation. Therefore, while there is evidence that cisplatin can be a risk factor for both genetic predisposition and peripheral neuropathy, the available information does not support the conclusion that cisplatin directly causes a genetic predisposition to peripheral neuropathy.

### Phase 3 (old run) — ClinPGx

**Genes:** ERCC1, GSTP1  ·  **Evidence:** 0 refs, 0 papers

Cisplatin-induced peripheral neuropathy is influenced by genetic factors such as ERCC1 and GSTP1, but there is no direct evidence that cisplatin causes a genetic predisposition to peripheral neuropathy. The biological mechanism likely involves polymorphisms in these genes affecting drug metabolism or DNA repair processes, thereby modulating the toxicity of cisplatin. For patient safety, pre-treatment screening for genetic variants like ERCC1 and GSTP1 could help identify individuals at higher risk of developing severe peripheral neuropathy, allowing for dose adjustments or alternative therapeutic strategies to be considered.

### Phase 3 — ClinPGx only

**Genes:** ERCC1, GSTP1  ·  **Evidence:** 7 refs, 0 papers

Cisplatin-induced peripheral neuropathy is influenced by genetic factors such as ERCC1 and GSTP1, but there is no direct evidence that cisplatin causes a genetic predisposition to peripheral neuropathy. The biological mechanism likely involves polymorphisms in these genes affecting drug metabolism or DNA repair processes, thereby modulating the toxicity of cisplatin. For patient safety, pre-treatment screening for genetic variants like ERCC1 and GSTP1 could help identify individuals at higher risk of developing severe peripheral neuropathy, allowing for dose adjustments or alternative therapeutic strategies to be considered.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** ERCC1, GSTM3, GSTP1  ·  **Evidence:** 22 refs, 15 papers

Cisplatin-induced peripheral neuropathy is influenced by genetic polymorphisms such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735). These variants likely affect the drug's metabolism, DNA repair mechanisms, or cellular sensitivity to cisplatin, thereby modulating the risk of developing peripheral neuropathy. For drug discovery and patient safety, pre-treatment genetic screening for these polymorphisms can help predict susceptibility to adverse effects, allowing for dose adjustments or alternative therapeutic strategies to mitigate risks.

<details><summary>Papers retrieved</summary>

- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:19620936` — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - via `clinpgx_citation`
- `PMID:42598682` — **Ultrasound-Guided Perineural Corticosteroid Injection and Dextrose Hydrodissection for Carpal Tunnel Syndrome: Current Evidence and Clinical Considerations.** — *Cureus · 2026*
  - via `-`
- `PMID:42598352` — **Effectiveness of Buerger Allen Exercise as an Adjunct to Standard Pharmacotherapy in Reducing Peripheral Neuropathy Symptoms Among Patients with Type 2 Diabetes Mellitus: A Randomized Controlled Pilot Study.** — *Journal of pharmacy & bioallied sciences · 2026*
  - via `-`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:19786980` — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - via `clinpgx_citation`
- `PMID:22188361` — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - via `clinpgx_citation`
- `PMID:22441531` — **Association of CASP7 polymorphisms and survival of patients with non-small cell lung cancer with platinum-based chemotherapy treatment.** — *Chest · 2012*
  - via `clinpgx_citation`
- `PMID:42598812` — **MLN4924 suppresses pancreatic cancer progression and enhances chemosensitivity to gemcitabine by targeting the PTGS2/EGFR-PI3K/Akt/mTOR signaling axis.** — *Anti-cancer drugs · 2026*
  - via `-`
- `PMID:42599160` — **The pan-tumor landscape, allelic status, and genomic complexity of SMARCA4 alterations.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2026*
  - via `-`
- `PMID:42598915` — **TLS as Predictors and Targets in Neoadjuvant Chemoimmunotherapy for NSCLC.** — *Thoracic cancer · 2026*
  - via `-`
- `PMID:42516273` — **Experimental study and thermodynamic modelling of the Nb-Sb system.** — *RSC advances · 2026*
  - via `-`
- `PMID:42455354` — **Structural and biochemical characterization of a novel DinG containing an endonuclease domain.** — *Cellular and molecular life sciences : CMLS · 2026*
  - via `-`

</details>

### Phase 5 — + PMC full text

**Genes:** ERCC1, GSTM3, GSTP1  ·  **Evidence:** 22 refs, 15 papers

Cisplatin-induced peripheral neuropathy is influenced by genetic polymorphisms such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735). These variants likely affect the drug's metabolism, DNA repair mechanisms, or cellular sensitivity to cisplatin, thereby modulating the risk of developing peripheral neuropathy. For drug discovery and patient safety, pre-treatment genetic screening for these polymorphisms can help predict susceptibility to adverse effects, allowing for dose adjustments or alternative therapeutic strategies to mitigate risks.

<details><summary>Papers retrieved</summary>

- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:19620936` — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - via `clinpgx_citation`
- `PMID:42598682` — **Ultrasound-Guided Perineural Corticosteroid Injection and Dextrose Hydrodissection for Carpal Tunnel Syndrome: Current Evidence and Clinical Considerations.** — *Cureus · 2026*
  - via `-`
- `PMID:42598352` — **Effectiveness of Buerger Allen Exercise as an Adjunct to Standard Pharmacotherapy in Reducing Peripheral Neuropathy Symptoms Among Patients with Type 2 Diabetes Mellitus: A Randomized Controlled Pilot Study.** — *Journal of pharmacy & bioallied sciences · 2026*
  - via `-`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:19786980` — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - via `clinpgx_citation`
- `PMID:22188361` — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - via `clinpgx_citation`
- `PMID:22441531` — **Association of CASP7 polymorphisms and survival of patients with non-small cell lung cancer with platinum-based chemotherapy treatment.** — *Chest · 2012*
  - via `clinpgx_citation`
- `PMID:42598812` — **MLN4924 suppresses pancreatic cancer progression and enhances chemosensitivity to gemcitabine by targeting the PTGS2/EGFR-PI3K/Akt/mTOR signaling axis.** — *Anti-cancer drugs · 2026*
  - via `-`
- `PMID:42599160` — **The pan-tumor landscape, allelic status, and genomic complexity of SMARCA4 alterations.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2026*
  - via `-`
- `PMID:42598915` — **TLS as Predictors and Targets in Neoadjuvant Chemoimmunotherapy for NSCLC.** — *Thoracic cancer · 2026*
  - via `-`
- `PMID:42516273` — **Experimental study and thermodynamic modelling of the Nb-Sb system.** — *RSC advances · 2026*
  - via `-`
- `PMID:42455354` — **Structural and biochemical characterization of a novel DinG containing an endonuclease domain.** — *Cellular and molecular life sciences : CMLS · 2026*
  - via `-`

</details>

### Phase 6 — open LLM search

**Genes:** ERCC1, GSTM3, GSTP1  ·  **Evidence:** 25 refs, 20 papers

Cisplatin-induced peripheral neuropathy is influenced by genetic factors such as ERCC1 (rs11615), GSTP1, and GSTM3. These genes likely modulate the metabolism or cellular response to cisplatin, affecting neuronal toxicity and susceptibility to CIPN. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help predict risk and tailor treatment plans, including dose adjustments or alternative agents with similar efficacy but lower neurotoxicity.

<details><summary>Papers retrieved</summary>

- `PMID:42363989` — **Ex vivo modulation of monocyte/macrophage phenotypes by all-trans retinoic acid in chemotherapy-induced peripheral neuropathy.** — *Molecular biology reports · 2026*
  - via `llm_topic:cisplatin neuropathy genetics`
- `PMID:41984466` — **Biowaste-Archetyped Hierarchical Calcium Carbonate Nanoreactors Induce Tumor Bioenergetic Crisis and Reverse Cisplatin Resistance via Mitochondrial Metabolic Reprogramming.** — *ACS applied materials & interfaces · 2026*
  - via `llm_topic:ERCC1 cisplatin toxicity`
- `PMID:42494534` — **Why pharmacogenomic biomarkers for chemotherapy-induced peripheral neuropathy fail: a systematic review of genetic associations, replication, and clinical translation.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:GSTP1 peripheral neuropathy`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635220` — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42635172` — **Mediation of Smoking and Cardiometabolic Factors on Diabetic Peripheral Neuropathy.** — *Nursing research · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42634428` — **Clinical Pharmacology of Eplontersen, the First Approved GalNAc-Conjugated Antisense Oligonucleotide.** — *Journal of clinical pharmacology · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634682` — **Severe Pulmonary Differentiation Syndrome Despite Corticosteroid Prophylaxis in Acute Promyelocytic Leukemia: Clinical Improvement With Pulse Methylprednisolone Therapy and High-Flow Nasal Cannula.** — *Cureus · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42629042` — **Retinoic acid priming enhances myogenesis of bovine muscle stem cells for cultivated meat production by modulating mitochondrial function.** — *Food research international (Ottawa, Ont.) · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42621781` — **METTL3-mediated m6A modification of circMtmr7 contributes to paclitaxel-induced peripheral neuropathy in the dorsal horn.** — *The Journal of physiology · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`
- `PMID:42609802` — **The Ethanol-Insoluble Low-Molecular-Weight Fraction LEP-4 Derived From Lentinula edodes Mycelia Extract Attenuates Oxaliplatin-Evoked Allodynia in Mice.** — *Advances in pharmacological and pharmaceutical sciences · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`
- `PMID:39560009` — **Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limitations.** — *Personalized medicine · 2024*
  - via `llm_topic:GSTM3 cisplatin toxicity`

</details>

### Phase 7 — open search + full text

**Genes:** ERCC1, GSTM3, GSTP1  ·  **Evidence:** 25 refs, 20 papers

Cisplatin-induced peripheral neuropathy is influenced by genetic factors such as ERCC1 (rs11615), GSTP1, and GSTM3. These genes likely modulate the metabolism or cellular response to cisplatin, affecting neuronal toxicity and susceptibility to CIPN. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help predict risk and tailor treatment plans, including dose adjustments or alternative agents with similar efficacy but lower neurotoxicity.

<details><summary>Papers retrieved</summary>

- `PMID:42363989` — **Ex vivo modulation of monocyte/macrophage phenotypes by all-trans retinoic acid in chemotherapy-induced peripheral neuropathy.** — *Molecular biology reports · 2026*
  - via `llm_topic:cisplatin neuropathy genetics`
- `PMID:41984466` — **Biowaste-Archetyped Hierarchical Calcium Carbonate Nanoreactors Induce Tumor Bioenergetic Crisis and Reverse Cisplatin Resistance via Mitochondrial Metabolic Reprogramming.** — *ACS applied materials & interfaces · 2026*
  - via `llm_topic:ERCC1 cisplatin toxicity`
- `PMID:42494534` — **Why pharmacogenomic biomarkers for chemotherapy-induced peripheral neuropathy fail: a systematic review of genetic associations, replication, and clinical translation.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:GSTP1 peripheral neuropathy`
- `PMID:42634497` — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635220` — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42635172` — **Mediation of Smoking and Cardiometabolic Factors on Diabetic Peripheral Neuropathy.** — *Nursing research · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42634428` — **Clinical Pharmacology of Eplontersen, the First Approved GalNAc-Conjugated Antisense Oligonucleotide.** — *Journal of clinical pharmacology · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634682` — **Severe Pulmonary Differentiation Syndrome Despite Corticosteroid Prophylaxis in Acute Promyelocytic Leukemia: Clinical Improvement With Pulse Methylprednisolone Therapy and High-Flow Nasal Cannula.** — *Cureus · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42629042` — **Retinoic acid priming enhances myogenesis of bovine muscle stem cells for cultivated meat production by modulating mitochondrial function.** — *Food research international (Ottawa, Ont.) · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42621781` — **METTL3-mediated m6A modification of circMtmr7 contributes to paclitaxel-induced peripheral neuropathy in the dorsal horn.** — *The Journal of physiology · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`
- `PMID:42609802` — **The Ethanol-Insoluble Low-Molecular-Weight Fraction LEP-4 Derived From Lentinula edodes Mycelia Extract Attenuates Oxaliplatin-Evoked Allodynia in Mice.** — *Advances in pharmacological and pharmaceutical sciences · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`
- `PMID:39560009` — **Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limitations.** — *Personalized medicine · 2024*
  - via `llm_topic:GSTM3 cisplatin toxicity`

</details>

### Phase 8 — combined-topic search

**Genes:** ERCC1, GSTM3, GSTP1  ·  **Evidence:** 24 refs, 15 papers

Cisplatin-induced peripheral neuropathy is associated with genetic variants such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3. These genes are involved in DNA repair mechanisms and detoxification pathways, which can influence cellular sensitivity to cisplatin's cytotoxic effects. While the relationship between these genetic markers and increased susceptibility to peripheral neuropathy is not definitively established, pre-treatment biomarker screening could help identify patients at higher risk for this adverse reaction, potentially guiding dose adjustments or alternative therapeutic strategies.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTM3` — 2 terms, 0 back-off(s), 2 hit(s)
- `peripheral neuropathy AND pharmacogenomics` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND neuropathy` — 2 terms, 0 back-off(s), 2 hit(s)
- `peripheral neuropathy AND cisplatin AND neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 rs11615 AND cisplatin` — 2 terms, 1 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND cisplatin` — 2 terms, 1 back-off(s), 2 hit(s)
- `GSTM3 rs1799735 AND cisplatin` — 2 terms, 1 back-off(s), 1 hit(s)
- `Ovarian Neoplasms AND cisplatin AND neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `Hepatocellular Carcinoma HCC AND cisplatin AND neuropathy` — 3 terms, 0 back-off(s), 1 hit(s)
- `Mitochondrial Permeability Transition Pores mPTP AND cisplatin` — 2 terms, 1 back-off(s), 1 hit(s)
- `cisplatin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND rs11615` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:41984466` — **Biowaste-Archetyped Hierarchical Calcium Carbonate Nanoreactors Induce Tumor Bioenergetic Crisis and Reverse Cisplatin Resistance via Mitochondrial Metabolic Reprogramming.** — *ACS applied materials & interfaces · 2026*
  - via `combo2:cisplatin + ERCC1`
- `PMID:42008434` — **Pharmacogenetic strategies to mitigate cisplatin-induced ototoxicity in head and neck cancer: A cost-minimization analysis with the use of GSTP1 c.313A>G genotyping.** — *PloS one · 2026*
  - via `combo2:cisplatin + GSTP1`
- `PMID:39560009` — **Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limitations.** — *Personalized medicine · 2024*
  - via `combo2:cisplatin + GSTM3`
- `PMID:42589658` — **Multi-Targeted Neuroprotection by Areca catechu Against Cisplatin-Induced Neurotoxicity: Cellular, Caenorhabditis elegans, and Metabolomic Evidence.** — *International journal of molecular sciences · 2026*
  - via `combo2:cisplatin + neuropathy`
- `PMID:42573969` — **An NLRP3 inflammasome inhibitor evoked dose-dependent anti-allodynia in the hindpaws of a rat model of chemotherapy-induced peripheral neuropathy.** — *Inflammopharmacology · 2026*
  - via `combo2:cisplatin + neuropathy`
- `PMID:42388964` — **Carboplatin May Be an Effective and Tolerable Treatment Option for Platinum-Sensitive Pancreatic Cancer Patients With Pre-existing Neuropathy.** — *Cureus · 2026*
  - via `combo3:peripheral neuropathy + cisplatin + neuropathy`
- `PMID:40526606` — **EPHX1 and ERCC2 polymorphisms are associated with cisplatin-induced nephrotoxicity and prognosis in Thai cancer patients.** — *PloS one · 2025*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39431656` — **Association of ERCC1 Gene Polymorphisms (rs3212986 and rs11615) With the Risk of Lung Cancer in a Population From Southeast Iran.** — *Journal of research in health sciences · 2024*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39516666` — **Predictive and prognostic value of excision repair cross-complementing group 1 in patients with advanced gastric cancer.** — *BJC reports · 2024*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:36397425` — **Platinum-induced ototoxicity in pediatric cancer survivors: GSTP1 c.313A>G variant association.** — *Medicine · 2022*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `combo2:GSTM3 rs1799735 + cisplatin`
- `PMID:42241284` — **Cisplatin resistance in an ovarian cancer model is mediated by microtubule dynamics regulator TPPP3 in synergy with tubulin code rewiring.** — *Cell reports · 2026*
  - via `combo3:Ovarian Neoplasms + cisplatin + neuropathy`
- `PMID:41727545` — **Exploratory analysis of the association between body composition albumin-bound paclitaxel induced peripheral neuropathy.** — *Frontiers in pharmacology · 2026*
  - via `combo3:Ovarian Neoplasms + cisplatin + neuropathy`
- `PMID:22754208` — **Gemcitabine and cisplatin-based combination chemotherapy in advanced hepatocellular carcinoma: An Indian experience.** — *Indian journal of medical and paediatric oncology : official journal of Indian Society of Medical & Paediatric Oncology · 2012*
  - via `combo3:Hepatocellular Carcinoma HCC + cisplatin + neuropathy`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `combo2:ERCC1 + rs11615`

</details>

### Phase 9 — combined + full text

**Genes:** ERCC1, GSTP1  ·  **Evidence:** 24 refs, 15 papers, 1 full text

Cisplatin-induced peripheral neuropathy is associated with genetic variants such as ERCC1 (rs11615) and GSTP1 (rs1695). These genes are involved in DNA repair mechanisms and glutathione metabolism, respectively. Individuals carrying these variants may have an increased susceptibility to developing peripheral neuropathy due to impaired cellular defense against cisplatin's toxic effects on nerve cells. For drug discovery and patient safety, pre-treatment genetic screening for these risk factors could help identify patients at higher risk of adverse reactions, allowing for dose adjustments or the use of alternative agents.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND GSTM3` — 2 terms, 0 back-off(s), 2 hit(s)
- `peripheral neuropathy AND pharmacogenomics` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND neuropathy` — 2 terms, 0 back-off(s), 2 hit(s)
- `peripheral neuropathy AND cisplatin AND neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 rs11615 AND cisplatin` — 2 terms, 1 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND cisplatin` — 2 terms, 1 back-off(s), 2 hit(s)
- `GSTM3 rs1799735 AND cisplatin` — 2 terms, 1 back-off(s), 1 hit(s)
- `Ovarian Neoplasms AND cisplatin AND neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `Hepatocellular Carcinoma HCC AND cisplatin AND neuropathy` — 3 terms, 0 back-off(s), 1 hit(s)
- `Mitochondrial Permeability Transition Pores mPTP AND cisplatin` — 2 terms, 1 back-off(s), 1 hit(s)
- `cisplatin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND rs11615` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:41984466` — **Biowaste-Archetyped Hierarchical Calcium Carbonate Nanoreactors Induce Tumor Bioenergetic Crisis and Reverse Cisplatin Resistance via Mitochondrial Metabolic Reprogramming.** — *ACS applied materials & interfaces · 2026*
  - via `combo2:cisplatin + ERCC1`
- `PMID:42008434` — **Pharmacogenetic strategies to mitigate cisplatin-induced ototoxicity in head and neck cancer: A cost-minimization analysis with the use of GSTP1 c.313A>G genotyping.** — *PloS one · 2026*
  - via `combo2:cisplatin + GSTP1`
- `PMID:39560009` — **Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limitations.** — *Personalized medicine · 2024*
  - via `combo2:cisplatin + GSTM3`
- `PMID:42589658` — **Multi-Targeted Neuroprotection by Areca catechu Against Cisplatin-Induced Neurotoxicity: Cellular, Caenorhabditis elegans, and Metabolomic Evidence.** — *International journal of molecular sciences · 2026*
  - via `combo2:cisplatin + neuropathy`
- `PMID:42573969` — **An NLRP3 inflammasome inhibitor evoked dose-dependent anti-allodynia in the hindpaws of a rat model of chemotherapy-induced peripheral neuropathy.** — *Inflammopharmacology · 2026*
  - via `combo2:cisplatin + neuropathy`
- `PMID:42388964` — **Carboplatin May Be an Effective and Tolerable Treatment Option for Platinum-Sensitive Pancreatic Cancer Patients With Pre-existing Neuropathy.** — *Cureus · 2026*
  - via `combo3:peripheral neuropathy + cisplatin + neuropathy`
- `PMID:40526606` — **EPHX1 and ERCC2 polymorphisms are associated with cisplatin-induced nephrotoxicity and prognosis in Thai cancer patients.** — *PloS one · 2025*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39431656` — **Association of ERCC1 Gene Polymorphisms (rs3212986 and rs11615) With the Risk of Lung Cancer in a Population From Southeast Iran.** — *Journal of research in health sciences · 2024*
  - via `combo2:ERCC1 rs11615 + cisplatin`
- `PMID:39516666` — **Predictive and prognostic value of excision repair cross-complementing group 1 in patients with advanced gastric cancer.** — *BJC reports · 2024*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:36397425` — **Platinum-induced ototoxicity in pediatric cancer survivors: GSTP1 c.313A>G variant association.** — *Medicine · 2022*
  - via `combo2:GSTP1 rs1695 + cisplatin`
- `PMID:30112115` — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `combo2:GSTM3 rs1799735 + cisplatin`
- `PMID:42241284` — **Cisplatin resistance in an ovarian cancer model is mediated by microtubule dynamics regulator TPPP3 in synergy with tubulin code rewiring.** — *Cell reports · 2026*
  - via `combo3:Ovarian Neoplasms + cisplatin + neuropathy`
- `PMID:41727545` — **Exploratory analysis of the association between body composition albumin-bound paclitaxel induced peripheral neuropathy.** — *Frontiers in pharmacology · 2026*
  - via `combo3:Ovarian Neoplasms + cisplatin + neuropathy`
- `PMID:22754208` — **Gemcitabine and cisplatin-based combination chemotherapy in advanced hepatocellular carcinoma: An Indian experience.** — *Indian journal of medical and paediatric oncology : official journal of Indian Society of Medical & Paediatric Oncology · 2012*
  - via `combo3:Hepatocellular Carcinoma HCC + cisplatin + neuropathy`
- `PMID:42123691/PMC13164360` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `combo2:ERCC1 + rs11615+pmc_xml`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** ERCC1, GSTM3, GSTP1  ·  **Evidence:** 8 refs, 3 papers

Cisplatin-induced peripheral neuropathy may be influenced by genetic factors such as ERCC1, GSTP1, and GSTM3. However, the evidence linking these genes specifically to cisplatin-induced peripheral neuropathy is currently limited and inconclusive. The biological mechanism likely involves polymorphisms in these genes affecting drug metabolism or DNA repair pathways, thereby modulating susceptibility to neurotoxicity. For patient safety, further research is needed to establish definitive biomarkers for risk stratification before considering pre-treatment genetic screening or dose adjustments based on genotype.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1/GSTM3 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1/GSTM3 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42573969` — **An NLRP3 inflammasome inhibitor evoked dose-dependent anti-allodynia in the hindpaws of a rat model of chemotherapy-induced peripheral neuropathy.** — *Inflammopharmacology · 2026*
  - via `free2:cisplatin peripheral neuropathy`
- `PMID:30854066` — **GSTP1 as a potential predictive factor for adverse events associated with platinum-based antitumor agent-induced peripheral neuropathy.** — *Oncology letters · 2019*
  - via `free3:(ERCC1 OR GSTP1 OR GSTM3) AND cisplatin AND peripheral neuropathy`
- `PMID:42524928` — **Whole-genome sequencing in Brazilian patients with neurofibromatosis type 1, including novel variants, incidental findings, and dual diagnoses.** — *Einstein (Sao Paulo, Brazil) · 2026*
  - via `free2:genetic predisposition peripheral neuropathy[mh]`

</details>

### Phase 11 — evidence ledger

**Genes:** ABCC3, AKT1, ERCC1, GSTM3, GSTP1, SLC19A1  ·  **Evidence:** 8 refs, 3 papers

Cisplatin is known to cause peripheral neuropathy as a side effect, with genetic factors potentially influencing susceptibility. The evidence suggests that while ERCC1 (rs11615), GSTP1 (rs1695), and other genes like SLC19A1 may modulate the response to cisplatin, no definitive causal relationship has been established between these genetic variants and a predisposition specifically induced by cisplatin. The conflicting evidence for GSTP1 indicates that its association with peripheral neuropathy is more specific to oxaliplatin rather than cisplatin. This implies that while genetic screening might help identify patients at higher risk of developing peripheral neuropathy when treated with cisplatin, the relationship between these genes and the drug's side effects remains uncertain. Therefore, further research is needed to clarify the role of these genetic factors in predicting cisplatin-induced peripheral neuropathy.

<details><summary>Queries issued (combined terms)</summary>

- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1/GSTM3 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND peripheral neuropathy` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/GSTP1/GSTM3 AND cisplatin AND peripheral neuropathy` — 3 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND peripheral neuropathy` — 2 terms, 0 back-off(s), 2 hit(s)
- `cisplatin AND ototoxicity` — 1 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42573969` — **An NLRP3 inflammasome inhibitor evoked dose-dependent anti-allodynia in the hindpaws of a rat model of chemotherapy-induced peripheral neuropathy.** — *Inflammopharmacology · 2026*
  - via `free2:cisplatin peripheral neuropathy`
- `PMID:30854066` — **GSTP1 as a potential predictive factor for adverse events associated with platinum-based antitumor agent-induced peripheral neuropathy.** — *Oncology letters · 2019*
  - via `free3:(ERCC1 OR GSTP1 OR GSTM3) AND cisplatin AND peripheral neuropathy`
- `PMID:42524928` — **Whole-genome sequencing in Brazilian patients with neurofibromatosis type 1, including novel variants, incidental findings, and dual diagnoses.** — *Einstein (Sao Paulo, Brazil) · 2026*
  - via `free2:genetic predisposition peripheral neuropathy[mh]`

</details>

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

### Baseline A — no external sources

**Genes:** ABCB1, GSTP1  ·  **Evidence:** 0 refs, 0 papers

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment are likely due to the drug's cardiotoxic effects rather than a genetic predisposition, based on high confidence connections from medical knowledge graphs. However, genetic factors such as polymorphisms in genes like ABCB1 (encoding P-glycoprotein) or GSTP1 can influence individual patient responses and susceptibility to doxorubicin-induced cardiotoxicity. The biological mechanism involves the generation of reactive oxygen species by doxorubicin leading to DNA damage and apoptosis in cardiac myocytes, exacerbated in genetically susceptible individuals. For drug discovery and patient safety, pre-treatment genetic screening for these variants could help identify patients at higher risk, allowing for dose adjustments or alternative agents such as liposomal formulations of doxorubicin which may reduce cardiotoxicity.

### Baseline B — paper setup

**Genes:** ABCB1, CYP3A4, CYP3A5  ·  **Evidence:** 0 refs, 0 papers

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment may be influenced by genetic factors such as polymorphisms in the ABCB1 (MDR1) gene, which encodes for P-glycoprotein involved in drug efflux, or variants in CYP3A4/5 genes responsible for doxorubicin metabolism. These genetic variations can lead to altered drug clearance and increased cardiotoxicity risk. For drug discovery and patient safety, pre-treatment biomarker screening should be considered to identify patients at higher risk of adverse reactions, allowing for dose adjustments or the use of alternative agents like liposomal formulations of doxorubicin that reduce systemic toxicity.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 0 refs, 0 papers

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic variations, particularly in the SLC28A3 gene (rs7853758), with a moderate association at PharmGKB evidence level 2B. This suggests that individuals carrying this variant might have an increased risk of developing heart muscle damage and shortness of breath due to doxorubicin-induced cardiotoxicity. For drug discovery and patient safety, pre-treatment genetic screening for SLC28A3 variants could help identify patients at higher risk, allowing for dose adjustments or the use of alternative agents with lower cardiotoxic potential.

### Phase 3 — ClinPGx only

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 9 refs, 0 papers

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic variations, particularly in the SLC28A3 gene (rs7853758), with a moderate association at PharmGKB evidence level 2B. This suggests that individuals carrying this variant might have an increased risk of developing heart muscle damage and shortness of breath due to doxorubicin-induced cardiotoxicity. For drug discovery and patient safety, pre-treatment genetic screening for SLC28A3 variants could help identify patients at higher risk, allowing for dose adjustments or the use of alternative agents with lower cardiotoxic potential.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 22 refs, 13 papers

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors, particularly variants within the SLC28A3 (rs7853758) gene. This variant is associated with a reduced risk of anthracycline-induced cardiotoxicity, suggesting that its absence could contribute to increased susceptibility to doxorubicin's adverse effects. Additionally, polymorphisms in GSTP1 (rs1695) have been linked to heightened sensitivity to doxorubicin-related cardiotoxicity. These findings underscore the importance of genetic screening for these variants before initiating treatment with doxorubicin to identify patients at higher risk and potentially adjust dosing or consider alternative therapeutic options.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:11418485` — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - via `clinpgx_citation`
- `PMID:11710708` — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - via `clinpgx_citation`
- `PMID:42599106` — **An acceptance-based healthy lifestyle programme for community-dwelling patients with pneumoconiosis: A waitlist pilot randomised controlled trial.** — *Pulmonology · 2026*
  - via `-`
- `PMID:42598580` — **Pneumomediastinum After Third Molar Surgery: A Case Report.** — *Cureus · 2026*
  - via `-`
- `PMID:10233212` — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - via `clinpgx_citation`
- `PMID:10774634` — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:32587261` — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 22 refs, 13 papers

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors, particularly variants within the SLC28A3 (rs7853758) gene. This variant is associated with a reduced risk of anthracycline-induced cardiotoxicity, suggesting that its absence could contribute to increased susceptibility to doxorubicin's adverse effects. Additionally, polymorphisms in GSTP1 (rs1695) have been linked to heightened sensitivity to doxorubicin-related cardiotoxicity. These findings underscore the importance of genetic screening for these variants before initiating treatment with doxorubicin to identify patients at higher risk and potentially adjust dosing or consider alternative therapeutic options.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:11418485` — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - via `clinpgx_citation`
- `PMID:11710708` — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - via `clinpgx_citation`
- `PMID:42599106` — **An acceptance-based healthy lifestyle programme for community-dwelling patients with pneumoconiosis: A waitlist pilot randomised controlled trial.** — *Pulmonology · 2026*
  - via `-`
- `PMID:42598580` — **Pneumomediastinum After Third Molar Surgery: A Case Report.** — *Cureus · 2026*
  - via `-`
- `PMID:10233212` — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - via `clinpgx_citation`
- `PMID:10774634` — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:28763429` — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - via `clinpgx_citation`

</details>

### Phase 6 — open LLM search

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 27 refs, 18 papers

The severe cardiotoxicity observed after doxorubicin treatment in a pediatric lymphoma patient may be influenced by genetic variants such as SLC28A3 (rs7853758) and GSTP1 (rs1695). These genes are associated with the transport and metabolism of doxorubicin, respectively. Variants in these genes could alter drug handling and increase susceptibility to cardiotoxicity. However, due to limited evidence and ambiguous clinical significance, further research is needed to establish definitive associations. For patient safety, genetic screening for SLC28A3 and GSTP1 variants might be considered alongside monitoring cardiac function during treatment. Alternative agents or dose adjustments could also be explored based on individual genetic profiles.

<details><summary>Papers retrieved</summary>

- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:41864056` — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `llm_topic:GSTP1 doxorubicin toxicity`
- `PMID:42176227` — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635325` — **Genetic Markers of Early Skeletal Muscle Loss in Adolescent and Young Adult Cancer Patients Treated with Anthracyclines.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42633171` — **Disseminated intravascular coagulation in chimeric antigen receptor T-cell therapy: a 6-year nationwide analysis of clinical outcomes and health care resource utilization in patients with hematologic malignancies.** — *Research and practice in thrombosis and haemostasis · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42635460` — **Clinical Assessment of Smokers with Persistent Dyspnoea but Unremarkable Spirometry: The Added Value of Diffusing Capacity for Carbon Monoxide.** — *COPD · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42635141` — **Undetected Heart Failure in Cardiology: Prevalence, Characteristics, and Outcome.** — *European journal of preventive cardiology · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42633868` — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:33274195` — **Anthracycline-Induced Cardiotoxicity in Breast Cancer Patients from Southern Sri Lanka: An Echocardiographic Analysis.** — *BioMed research international · 2020*
  - via `llm_topic:early-onset chronic progressive cardiotoxicity`

</details>

### Phase 7 — open search + full text

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 27 refs, 18 papers

The severe cardiotoxicity observed after doxorubicin treatment in a pediatric lymphoma patient may be influenced by genetic variants such as SLC28A3 (rs7853758) and GSTP1 (rs1695). These genes are associated with the transport and metabolism of doxorubicin, respectively. Variants in these genes could alter drug handling and increase susceptibility to cardiotoxicity. However, due to limited evidence and ambiguous clinical significance, further research is needed to establish definitive associations. For patient safety, genetic screening for SLC28A3 and GSTP1 variants might be considered alongside monitoring cardiac function during treatment. Alternative agents or dose adjustments could also be explored based on individual genetic profiles.

<details><summary>Papers retrieved</summary>

- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:41864056` — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `llm_topic:GSTP1 doxorubicin toxicity`
- `PMID:42176227` — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635325` — **Genetic Markers of Early Skeletal Muscle Loss in Adolescent and Young Adult Cancer Patients Treated with Anthracyclines.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42633171` — **Disseminated intravascular coagulation in chimeric antigen receptor T-cell therapy: a 6-year nationwide analysis of clinical outcomes and health care resource utilization in patients with hematologic malignancies.** — *Research and practice in thrombosis and haemostasis · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42635460` — **Clinical Assessment of Smokers with Persistent Dyspnoea but Unremarkable Spirometry: The Added Value of Diffusing Capacity for Carbon Monoxide.** — *COPD · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42635141` — **Undetected Heart Failure in Cardiology: Prevalence, Characteristics, and Outcome.** — *European journal of preventive cardiology · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42633868` — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:33274195` — **Anthracycline-Induced Cardiotoxicity in Breast Cancer Patients from Southern Sri Lanka: An Echocardiographic Analysis.** — *BioMed research international · 2020*
  - via `llm_topic:early-onset chronic progressive cardiotoxicity`

</details>

### Phase 8 — combined-topic search

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 26 refs, 17 papers

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors such as the SLC28A3 and GSTP1 genes, with evidence suggesting a potential association but not definitive proof. The biological mechanism likely involves altered drug transport or metabolism due to these gene variants, leading to increased cardiotoxicity risk. For patient safety, pre-treatment biomarker screening for these genetic markers could be considered, although the current evidence is limited and further research is needed to establish robust predictive value. Alternative agents or dose adjustments based on genetic profiles might also be explored in future drug development.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND RARG` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND genetic_variant` — 2 terms, 0 back-off(s), 1 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `shortness of breath AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `heart muscle damage AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `RARG rs2229774 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `early-onset chronic progressive cardiotoxicity AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND RARG` — 2 terms, 0 back-off(s), 2 hit(s)
- `Cardiotoxicity AND GSTA1` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `combo2:doxorubicin + SLC28A3`
- `PMID:41864056` — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `combo2:doxorubicin + GSTP1`
- `PMID:40505291` — **Acute cardiac dysfunction in patients with ovarian cancer treated with Niraparib due to TFAM mutation: A case series and functional analysis.** — *Cancer genetics · 2025*
  - via `combo2:cardiotoxicity + genetic_variant`
- `PMID:42627580` — **Integrated Multi-omics Reveals CDKN1A Suppression and Metabolic Regulation as Key Mechanisms of Huangqi Guizhi Wuwu Decoction Against Doxorubicin-Induced Cardiotoxicity.** — *Cardiovascular toxicology · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42624274` — **Ginkgolide B Mitigates Doxorubicin-Induced Cardiotoxicity by Regulating AMPK-Mediated Mitochondrial Fission via P-Drp1/OPA1 and Apoptosis.** — *Archives of biochemistry and biophysics · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42420767` — **Anthracycline chemotherapy does not increase arterial stiffness or carotid intima-media thickness in young adult survivors of hematological malignancies.** — *Journal of applied physiology (Bethesda, Md. : 1985) · 2026*
  - via `combo3:pediatric lymphoma + doxorubicin + cardiotoxicity`
- `PMID:42322372` — **Early anthracycline cardiotoxicity in adolescents and young adults with sarcoma: a prospective echocardiographic study.** — *ESC heart failure · 2026*
  - via `combo3:pediatric lymphoma + doxorubicin + cardiotoxicity`
- `PMID:41278205` — **The mitigatory capabilities of exercise on breast cancer chemotherapy-induced cardiotoxicity.** — *Frontiers in cell and developmental biology · 2025*
  - via `combo3:shortness of breath + doxorubicin + cardiotoxicity`
- `PMID:41168904` — **Right ventricular vulnerability: a case study on anthracycline-induced cardiotoxicity post-pulmonary embolism recovery.** — *Cardio-oncology (London, England) · 2025*
  - via `combo3:shortness of breath + doxorubicin + cardiotoxicity`
- `PMID:42559407` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `combo3:heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:42531631` — **Metal-dependent cell death in doxorubicin-induced cardiotoxicity and mitigation by luteolin: Network pharmacology and experimental verification.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo3:heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:37828659` — **The Role of RARG rs2229774, SLC28A3 rs7853758, and UGT1A6*4 rs17863783 Single-nucleotide Polymorphisms in the Doxorubicin-induced Cardiotoxicity in Solid Childhood Tumors.** — *Journal of pediatric hematology/oncology · 2024*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:26354850` — **GSTP1 and GSTO1 single nucleotide polymorphisms and the response of bladder cancer patients to intravesical chemotherapy.** — *Scientific reports · 2015*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + doxorubicin + cardiotoxicity`
- `PMID:24259388` — **Anthracycline-induced cardiotoxicity: prospective cohort study from Pakistan.** — *BMJ open · 2013*
  - via `combo3:early-onset chronic progressive cardiotoxicity + doxorubicin + cardiotoxicity`

</details>

### Phase 9 — combined + full text

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 27 refs, 18 papers, 1 full text

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors such as SLC28A3 and GSTP1, though the evidence is not definitive. The biological mechanism likely involves altered drug transport or metabolism due to these variants, potentially leading to higher intracellular concentrations of doxorubicin and increased cardiotoxicity. For patient safety, pre-treatment biomarker screening for these genetic variants could help identify at-risk individuals who might benefit from dose adjustments or alternative agents with a lower risk of cardiotoxicity.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND RARG` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND genetic_variant` — 2 terms, 0 back-off(s), 1 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `shortness of breath AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `heart muscle damage AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `RARG rs2229774 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `early-onset chronic progressive cardiotoxicity AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND RARG` — 2 terms, 0 back-off(s), 2 hit(s)
- `Cardiotoxicity AND GSTA1` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `combo2:doxorubicin + SLC28A3`
- `PMID:41864056` — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `combo2:doxorubicin + GSTP1`
- `PMID:40505291` — **Acute cardiac dysfunction in patients with ovarian cancer treated with Niraparib due to TFAM mutation: A case series and functional analysis.** — *Cancer genetics · 2025*
  - via `combo2:cardiotoxicity + genetic_variant`
- `PMID:42627580` — **Integrated Multi-omics Reveals CDKN1A Suppression and Metabolic Regulation as Key Mechanisms of Huangqi Guizhi Wuwu Decoction Against Doxorubicin-Induced Cardiotoxicity.** — *Cardiovascular toxicology · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42624274` — **Ginkgolide B Mitigates Doxorubicin-Induced Cardiotoxicity by Regulating AMPK-Mediated Mitochondrial Fission via P-Drp1/OPA1 and Apoptosis.** — *Archives of biochemistry and biophysics · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42420767` — **Anthracycline chemotherapy does not increase arterial stiffness or carotid intima-media thickness in young adult survivors of hematological malignancies.** — *Journal of applied physiology (Bethesda, Md. : 1985) · 2026*
  - via `combo3:pediatric lymphoma + doxorubicin + cardiotoxicity`
- `PMID:42322372` — **Early anthracycline cardiotoxicity in adolescents and young adults with sarcoma: a prospective echocardiographic study.** — *ESC heart failure · 2026*
  - via `combo3:pediatric lymphoma + doxorubicin + cardiotoxicity`
- `PMID:41278205` — **The mitigatory capabilities of exercise on breast cancer chemotherapy-induced cardiotoxicity.** — *Frontiers in cell and developmental biology · 2025*
  - via `combo3:shortness of breath + doxorubicin + cardiotoxicity`
- `PMID:41168904` — **Right ventricular vulnerability: a case study on anthracycline-induced cardiotoxicity post-pulmonary embolism recovery.** — *Cardio-oncology (London, England) · 2025*
  - via `combo3:shortness of breath + doxorubicin + cardiotoxicity`
- `PMID:42559407` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `combo3:heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:42531631` — **Metal-dependent cell death in doxorubicin-induced cardiotoxicity and mitigation by luteolin: Network pharmacology and experimental verification.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo3:heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:37828659` — **The Role of RARG rs2229774, SLC28A3 rs7853758, and UGT1A6*4 rs17863783 Single-nucleotide Polymorphisms in the Doxorubicin-induced Cardiotoxicity in Solid Childhood Tumors.** — *Journal of pediatric hematology/oncology · 2024*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:26354850` — **GSTP1 and GSTO1 single nucleotide polymorphisms and the response of bladder cancer patients to intravesical chemotherapy.** — *Scientific reports · 2015*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + doxorubicin + cardiotoxicity`
- `PMID:24259388` — **Anthracycline-induced cardiotoxicity: prospective cohort study from Pakistan.** — *BMJ open · 2013*
  - via `combo3:early-onset chronic progressive cardiotoxicity + doxorubicin + cardiotoxicity`
- `PMID:41864056/PMC13185652` — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `combo2:doxorubicin + GSTP1+pmc_xml`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 12 refs, 3 papers

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic variants such as SLC28A3 (rs7853758) and GSTP1 (rs1695), which have been associated with increased risk of cardiotoxicity at evidence levels 2B and 3, respectively. The biological mechanism likely involves altered drug transport or metabolism due to these genetic polymorphisms, leading to higher doxorubicin concentrations in cardiac tissue and subsequent toxicity. For patient safety, pre-treatment genetic screening for these variants could help identify high-risk individuals who might benefit from dose adjustments or alternative chemotherapeutic agents with lower cardiotoxic potential.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND GSTP1 AND RARG AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND cardiotoxicity AND doxorubicin` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/rs1695 AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `lymphoma AND doxorubicin AND genetic variant` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42636514` — **Targeting ID2 to augment doxorubicin antitumor efficacy and enhance antibacterial defense without neutropenia.** — *International immunopharmacology · 2026*
  - via `free2:doxorubicin AND cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `free5:(SLC28A3 OR GSTP1 OR RARG) AND doxorubicin AND cardiotoxicity`
- `PMID:42628504` — **Multifocal Primary Cutaneous Diffuse Large B-Cell Lymphoma, Leg Type, Presenting on Face and Chest: Complete Remission With R-CHOP.** — *The American Journal of dermatopathology · 2026*
  - via `free2:pediatric lymphoma AND doxorubicin`

</details>

### Phase 11 — evidence ledger

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 12 refs, 3 papers

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may have a genetic component. The genes SLC28A3 (rs7853758) and GSTP1 (rs1695) are associated with doxorubicin-induced cardiotoxicity, though the evidence is ambiguous (PharmGKB levels 2B and 3 respectively). These associations suggest that genetic variations in these genes could modulate an individual's susceptibility to doxorubicin's cardiotoxic effects. For drug discovery and patient safety, it would be prudent to screen for these genetic variants before initiating doxorubicin therapy or consider dose adjustments based on the identified genotype. Additionally, exploring alternative agents with lower cardiotoxicity profiles may also benefit patients with specific genetic predispositions.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND GSTP1 AND RARG AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND cardiotoxicity AND doxorubicin` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1/rs1045642 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `pediatric lymphoma AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/rs7853758 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1/rs1695 AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `lymphoma AND doxorubicin AND genetic variant` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42643688` — **Borneol-based nanoparticles encapsulating Doxorubicin/Sodium tanshinone IIA sulfonate enhance the effect of anti-glioma and alleviate cardiotoxicity.** — *Cytotechnology · 2026*
  - via `free2:doxorubicin AND cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `free5:(SLC28A3 OR GSTP1 OR RARG) AND doxorubicin AND cardiotoxicity`
- `PMID:42628504` — **Multifocal Primary Cutaneous Diffuse Large B-Cell Lymphoma, Leg Type, Presenting on Face and Chest: Complete Remission With R-CHOP.** — *The American Journal of dermatopathology · 2026*
  - via `free2:pediatric lymphoma AND doxorubicin`

</details>

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

### Baseline A — no external sources

**Genes:** ABCB1, APOE, GSTP1  ·  **Evidence:** 0 refs, 0 papers

Pharmacogenomic biomarkers such as genetic variants in the ABCB1 (MDR1), APOE, and GSTP1 genes are implicated in anthracycline-induced cardiotoxicity among childhood cancer survivors. These genetic variations likely influence drug metabolism, transport, and oxidative stress pathways, contributing to differential susceptibility to cardiac damage from anthracyclines. For drug discovery and patient safety, pre-treatment screening for these biomarkers can help identify high-risk patients who may benefit from dose adjustments or alternative agents with lower cardiotoxic potential.

### Baseline B — paper setup

**Genes:** ABCB1, APOE, SLCO1B1  ·  **Evidence:** 0 refs, 0 papers

The pharmacogenomic biomarkers associated with anthracycline-induced cardiotoxicity primarily involve genetic variants within the SLCO1B1, ABCB1 (MDR1), and APOE genes. These genetic markers predict an individual's susceptibility to heart damage caused by anthracyclines in childhood cancer survivors due to their roles in drug transport and metabolism. For instance, polymorphisms in SLCO1B1 affect the hepatic uptake of anthracyclines, while ABCB1 variants influence drug efflux from cardiomyocytes. APOE gene variations are also linked with lipid metabolism and oxidative stress pathways that contribute to cardiac toxicity. These biomarkers have significant implications for personalized medicine approaches, including pre-treatment screening to identify high-risk patients, dose adjustment based on genetic profiles, and the potential use of alternative agents or cardioprotective strategies.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 0 refs, 0 papers

SLC28A3 (rs7853758) and GSTP1 (rs1695) are the primary pharmacogenomic biomarkers predicting anthracycline-induced cardiotoxicity in childhood cancer survivors. SLC28A3 is involved in nucleoside transport, potentially affecting drug metabolism and distribution, while GSTP1 encodes a glutathione transferase that detoxifies xenobiotics, including anthracyclines. These genetic variants likely influence the body's ability to handle anthracycline exposure, leading to increased cardiotoxicity risk. For drug discovery and patient safety, pre-treatment screening for these biomarkers can help identify high-risk patients who may benefit from dose adjustments or alternative agents with lower cardiotoxic potential.

### Phase 3 — ClinPGx only

**Genes:** RARG, SLC28A3  ·  **Evidence:** 9 refs, 0 papers

The genes/variants SLC28A3 (rs7853758) and RARG (rs2229774) are implicated in anthracycline-induced cardiotoxicity among childhood cancer survivors. The biological mechanism underlying this adverse reaction is likely related to the transport or metabolism of anthracyclines, with SLC28A3 potentially influencing drug uptake into cardiac cells and RARG affecting cellular response to these drugs. For drug discovery and patient safety, pre-treatment screening for these biomarkers can help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate this risk.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** GSTP1, RARG, SLC28A3  ·  **Evidence:** 22 refs, 13 papers

The genes/variants implicated in anthracycline-induced cardiotoxicity include SLC28A3 (rs7853758), RARG (rs2229774), and GSTP1 (rs1695). SLC28A3 (rs7853758) is a protective variant, reducing the risk of cardiotoxicity in childhood cancer survivors. The biological mechanism likely involves altered nucleoside transport or metabolism affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help identify high-risk patients who may benefit from dose adjustments or alternative agents with lower cardiotoxic potential.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:35147047` — **Pharmacogenomic study of anthracycline-induced cardiotoxicity in Mexican pediatric patients.** — *Pharmacogenomics · 2022*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:32587261` — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:11418485` — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - via `clinpgx_citation`
- `PMID:11710708` — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - via `clinpgx_citation`
- `PMID:12209976` — **Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation.** — *International journal of cancer · 2002*
  - via `clinpgx_citation`
- `PMID:17000685` — **Pharmacogenetics of capecitabine in advanced breast cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:42598301` — **Risk of fracture among lung cancer survivors by cancer treatment modality: A population-based retrospective cohort study.** — *Journal of bone oncology · 2026*
  - via `-`
- `PMID:42597694` — **Improving Survival Prediction of Head and Neck Cancer Patients by Modeling Long-term Symptom Burden.** — *Proceedings. IEEE International Conference on Healthcare Informatics · 2026*
  - via `-`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTP1, RARG, SLC28A3  ·  **Evidence:** 27 refs, 15 papers

The genetic variants SLC28A3 (rs7853758), GSTP1 (rs1695), and RARG (rs2229774) are implicated in anthracycline-induced cardiotoxicity, with SLC28A3 (rs7853758) showing the strongest protective effect. The biological mechanism likely involves altered nucleoside transport or metabolism affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment screening for these variants can help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or alternative agent selection to mitigate adverse effects.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:28763429` — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - via `clinpgx_citation`
- `PMID:11418485` — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - via `clinpgx_citation`
- `PMID:11710708` — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - via `clinpgx_citation`
- `PMID:12209976` — **Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation.** — *International journal of cancer · 2002*
  - via `clinpgx_citation`
- `PMID:17000685` — **Pharmacogenetics of capecitabine in advanced breast cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:24036429` — **Three most common nonsynonymous UGT1A6*2 polymorphisms (Thr181Ala, Arg184Ser and Ser7Ala) and therapeutic response to deferiprone in β-thalassemia major patients.** — *Gene · 2013*
  - via `clinpgx_citation`
- `PMID:18349289` — **Gilbert's Syndrome and irinotecan toxicity: combination with UDP-glucuronosyltransferase 1A7 variants increases risk.** — *Cancer epidemiology, biomarkers & prevention : a publication of the American Association for Cancer Research, cosponsored by the American Society of Preventive Oncology · 2008*
  - via `clinpgx_citation`
- `PMID:15805193` — **Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin.** — *Proceedings of the National Academy of Sciences of the United States of America · 2005*
  - via `clinpgx_citation`
- `PMID:16220110` — **CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population.** — *Pharmacogenetics and genomics · 2005*
  - via `clinpgx_citation`

</details>

### Phase 6 — open LLM search

**Genes:** RARG, SLC28A3  ·  **Evidence:** 23 refs, 13 papers

The genes/variants SLC28A3 (rs7853758) and RARG (rs2229774) are implicated in anthracycline-induced cardiotoxicity, with moderate evidence suggesting their predictive value. The biological mechanism likely involves altered nucleoside transport or receptor activity affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants could help identify high-risk patients who may benefit from dose adjustments or alternative agents to mitigate cardiotoxicity risk.

<details><summary>Papers retrieved</summary>

- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:anthracycline cardiotoxicity SLC28A3`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `llm_topic:RARG cardiotoxicity neoplasms`
- `PMID:33425072` — **Genetic Variability of Antioxidative Mechanisms and Cardiotoxicity after Adjuvant Radiotherapy in HER2-Positive Breast Cancer Patients.** — *Disease markers · 2020*
  - via `llm_topic:GSTP1 rs1695 cardiotoxicity`
- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `llm_topic:Anthracycline-induced cardiotoxicity`
- `PMID:42615446` — **A Simple Clinical Risk Score to Improve Prediction of Anthracycline-Induced Cardiotoxicity.** — *JACC. CardioOncology · 2026*
  - via `llm_topic:Anthracycline-induced cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42353582` — **Oxidative DNA Damage as an Integrative Marker of Redox Dysfunction Associated with Doxorubicin-Induced Cardiotoxicity in Pediatric Leukemia.** — *Current issues in molecular biology · 2026*
  - via `llm_topic:CBR3 rs1056892`
- `PMID:42527396` — **Effects of CYP3A4, CYP3A5, and ABCB1 genetic variants on tacrolimus metabolism during the early period after kidney transplantation.** — *The pharmacogenomics journal · 2026*
  - via `llm_topic:ABCB1 rs1045642`
- `PMID:41083112` — **Associations between host efflux pump gene polymorphisms (ABCB1, ABCC1, ABCG2) and drug-resistant tuberculosis in a Chinese cohort.** — *Gene · 2025*
  - via `llm_topic:ABCC2 rs8187710`

</details>

### Phase 7 — open search + full text

**Genes:** GSTP1, RARG, SLC28A3  ·  **Evidence:** 25 refs, 15 papers, 1 full text

The genes/variants SLC28A3 (rs7853758), RARG (rs2229774), and GSTP1 (rs1695) are implicated in anthracycline-induced cardiotoxicity. The biological mechanism likely involves altered transport, receptor activity, or detoxification pathways that affect cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help identify patients at higher risk of cardiotoxicity, enabling dose adjustments or the use of alternative agents to mitigate this adverse effect.

<details><summary>Papers retrieved</summary>

- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:anthracycline cardiotoxicity SLC28A3`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG anthracycline cardiotoxicity`
- `PMID:36536332` — **Pharmacogenetics of chemotherapy treatment response and -toxicities in patients with osteosarcoma: a systematic review.** — *BMC cancer · 2022*
  - via `llm_topic:GSTP1 osteosarcoma cardiotoxicity`
- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `llm_topic:anthracycline-induced cardiotoxicity`
- `PMID:42615446` — **A Simple Clinical Risk Score to Improve Prediction of Anthracycline-Induced Cardiotoxicity.** — *JACC. CardioOncology · 2026*
  - via `llm_topic:anthracycline-induced cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:40413218` — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42353582` — **Oxidative DNA Damage as an Integrative Marker of Redox Dysfunction Associated with Doxorubicin-Induced Cardiotoxicity in Pediatric Leukemia.** — *Current issues in molecular biology · 2026*
  - via `llm_topic:CBR3 rs1056892`
- `PMID:42527396` — **Effects of CYP3A4, CYP3A5, and ABCB1 genetic variants on tacrolimus metabolism during the early period after kidney transplantation.** — *The pharmacogenomics journal · 2026*
  - via `llm_topic:ABCB1 rs1045642`
- `PMID:41083112` — **Associations between host efflux pump gene polymorphisms (ABCB1, ABCC1, ABCG2) and drug-resistant tuberculosis in a Chinese cohort.** — *Gene · 2025*
  - via `llm_topic:ABCC2 rs8187710`
- `PMID:42594534` — **Feedback activation of MAPK-ERK1/2 signaling causes resistance to trastuzumab-deruxtecan in endometrial cancers.** — *Gynecologic oncology · 2026*
  - via `llm_topic:HER2-targeted antibodies`
- `PMID:42591779` — **Sequential HER2-targeted antibody-drug conjugate therapy for acquired resistance in a 55-year-old male kidney transplant recipient with metastatic urothelial carcinoma: a case report.** — *Translational cancer research · 2026*
  - via `llm_topic:HER2-targeted antibodies`
- `PMID:42279262/PMC13255899` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774 cancer+pmc_xml`

</details>

### Phase 8 — combined-topic search

**Genes:** SLC28A3  ·  **Evidence:** 24 refs, 15 papers

SLC28A3 (rs7853758) is a significant genetic marker linked to anthracycline-induced cardiotoxicity, with evidence suggesting it may influence susceptibility to cardiac damage. However, clinical factors such as cumulative dose and age are currently more predictive of cardiotoxicity in childhood cancer survivors than genetic polymorphisms like SLC28A3 (rs7853758). Further research is needed to clarify the role of pharmacogenomic biomarkers in predicting anthracycline-induced cardiotoxicity across different patient populations. Pre-treatment screening for these markers could still be valuable, but clinical factors should remain a primary focus for risk assessment and management.

<details><summary>Queries issued (combined terms)</summary>

- `SLC28A3 AND anthracycline-related Cardiotoxicity` — 2 terms, 0 back-off(s), 1 hit(s)
- `GSTP1 AND anthracycline-related Cardiotoxicity` — 2 terms, 0 back-off(s), 1 hit(s)
- `RARG AND anthracycline-related Cardiotoxicity` — 2 terms, 0 back-off(s), 0 hit(s)
- `SLC28A3 AND rs7853858` — 2 terms, 1 back-off(s), 0 hit(s)
- `pharmacogenomic biomarkers AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracycline-induced cardiotoxicity AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 rs7853758 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `RARG rs2229774 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Osteosarcoma AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Neoplasms AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695` — 2 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `combo2:SLC28A3 + anthracycline-related Cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `combo3:pharmacogenomic biomarkers + anthracycline + cardiotoxicity`
- `PMID:42176227` — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `combo3:pharmacogenomic biomarkers + anthracycline + cardiotoxicity`
- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `combo3:anthracycline-induced cardiotoxicity + anthracycline + cardiotoxicity`
- `PMID:42615446` — **A Simple Clinical Risk Score to Improve Prediction of Anthracycline-Induced Cardiotoxicity.** — *JACC. CardioOncology · 2026*
  - via `combo3:anthracycline-induced cardiotoxicity + anthracycline + cardiotoxicity`
- `PMID:42525877` — **Cardiometabolic Risk and Awareness of Anthracycline-Related Cardiotoxicity in Survivors of Childhood Cancer: A Population-Based Study.** — *Journal of pediatric hematology/oncology · 2026*
  - via `combo3:childhood cancer survivors + anthracycline + cardiotoxicity`
- `PMID:42499264` — **The Relationship Between Physical Activity and Left Ventricular Remodeling in Childhood Cancer Survivors Treated With Anthracyclines: A Cross-Sectional Study.** — *Pediatric blood & cancer · 2026*
  - via `combo3:childhood cancer survivors + anthracycline + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + anthracycline + cardiotoxicity`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `combo3:RARG rs2229774 + anthracycline + cardiotoxicity`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + anthracycline + cardiotoxicity`
- `PMID:41760893` — **Targeting the metabolic fingerprint of amino acids to identify novel metabolic characteristics in osteosarcoma patients undergoing anthracycline treatment.** — *Scientific reports · 2026*
  - via `combo3:Osteosarcoma + anthracycline + cardiotoxicity`
- `PMID:41346814` — **Novel Oncologic Strategies in Osteosarcoma Management: Maximizing Impact, Minimizing Harm.** — *Discoveries (Craiova, Romania) · 2025*
  - via `combo3:Osteosarcoma + anthracycline + cardiotoxicity`
- `PMID:42600597` — **TEMPORAL DYNAMICS OF GLOBAL LONGITUDINAL STRAIN AND NT-PROBNP IN THE EARLY DETECTION OF ANTHRACYCLINE-INDUCED CARDIOTOXICITY: A 24-MONTH PROSPECTIVE STUDY IN POSTMENOPAUSAL WOMEN WITH BREAST CANCER.** — *Georgian medical news · 2026*
  - via `combo3:Neoplasms + anthracycline + cardiotoxicity`
- `PMID:42592971` — **Early left ventricular ejection fraction trajectories according to CTox risk score in breast cancer patients treated with anthracycline and/or trastuzumab.** — *Medicinski glasnik : official publication of the Medical Association of Zenica-Doboj Canton, Bosnia and Herzegovina · 2026*
  - via `combo3:Neoplasms + anthracycline + cardiotoxicity`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `combo2:GSTP1 + rs1695`

</details>

### Phase 9 — combined + full text

**Genes:** RARG, SLC28A3  ·  **Evidence:** 21 refs, 13 papers, 1 full text

SLC28A3 (rs7853758) is a significant genetic marker linked to anthracycline-induced cardiotoxicity, with evidence suggesting it may influence the likelihood of developing cardiotoxicity in childhood cancer survivors. However, clinical studies indicate that non-genetic factors such as cumulative dose and use of HER2-targeted antibodies are more predictive in certain populations like Chinese early-stage breast cancer patients. The biological mechanism underlying SLC28A3's role is not fully elucidated but may involve its function in nucleoside transport, affecting cardiomyocyte metabolism or drug accumulation. For drug discovery and patient safety, pre-treatment biomarker screening for SLC28A3 could be considered alongside clinical risk factors to tailor anthracycline dosing or explore alternative agents with lower cardiotoxicity profiles.

<details><summary>Queries issued (combined terms)</summary>

- `SLC28A3 AND anthracycline-related Cardiotoxicity` — 2 terms, 0 back-off(s), 1 hit(s)
- `RARG AND anthracycline-related Cardiotoxicity` — 2 terms, 0 back-off(s), 0 hit(s)
- `GSTP1 AND rs1695 AND anthracycline-related Cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `pharmacogenomic biomarkers AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracycline-induced cardiotoxicity AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 rs7853758 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG rs2229774 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `CBR3 rs1056892 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 rs1045642 AND anthracycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND rs7853758` — 2 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695` — 2 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND Cardiotoxicity AND SLC28A3` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `combo2:SLC28A3 + anthracycline-related Cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `combo3:pharmacogenomic biomarkers + anthracycline + cardiotoxicity`
- `PMID:42176227` — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `combo3:pharmacogenomic biomarkers + anthracycline + cardiotoxicity`
- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `combo3:anthracycline-induced cardiotoxicity + anthracycline + cardiotoxicity`
- `PMID:42615446` — **A Simple Clinical Risk Score to Improve Prediction of Anthracycline-Induced Cardiotoxicity.** — *JACC. CardioOncology · 2026*
  - via `combo3:anthracycline-induced cardiotoxicity + anthracycline + cardiotoxicity`
- `PMID:42525877` — **Cardiometabolic Risk and Awareness of Anthracycline-Related Cardiotoxicity in Survivors of Childhood Cancer: A Population-Based Study.** — *Journal of pediatric hematology/oncology · 2026*
  - via `combo3:childhood cancer survivors + anthracycline + cardiotoxicity`
- `PMID:42499264` — **The Relationship Between Physical Activity and Left Ventricular Remodeling in Childhood Cancer Survivors Treated With Anthracyclines: A Cross-Sectional Study.** — *Pediatric blood & cancer · 2026*
  - via `combo3:childhood cancer survivors + anthracycline + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + anthracycline + cardiotoxicity`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `combo3:RARG rs2229774 + anthracycline + cardiotoxicity`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + anthracycline + cardiotoxicity`
- `PMID:40362292` — **Drugs Metabolism-Related Genes Variants Impact on Anthracycline-Based Chemotherapy Induced Subclinical Cardiotoxicity in Breast Cancer Patients.** — *International journal of molecular sciences · 2025*
  - via `combo3:CBR3 rs1056892 + anthracycline + cardiotoxicity`
- `PMID:37367397` — **The Impact of Polymorphisms in ATP-Binding Cassette Transporter Genes on Anthracycline-Induced Early Cardiotoxicity in Patients with Breast Cancer.** — *Journal of cardiovascular development and disease · 2023*
  - via `combo3:ABCB1 rs1045642 + anthracycline + cardiotoxicity`
- `PMID:42279262/PMC13255899` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `combo2:RARG + rs2229774+pmc_xml`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** RARG, SLC28A3  ·  **Evidence:** 13 refs, 4 papers

The genes/variants implicated in anthracycline-induced cardiotoxicity include SLC28A3 (rs7853758) and RARG (rs2229774). These genetic markers are associated with an increased risk of cardiotoxicity, potentially due to their roles in drug transport and receptor signaling pathways that affect cardiac function. However, clinical studies have shown limited predictive value for these biomarkers compared to traditional clinical factors such as cumulative anthracycline dose and age. For patient safety, pre-treatment screening for these genetic variants could still be considered alongside clinical risk assessment to identify high-risk individuals, particularly in childhood cancer survivors. Additionally, dose adjustment or the use of cardioprotective agents may be warranted based on individual genetic profiles.

<details><summary>Queries issued (combined terms)</summary>

- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenetics AND biomarker AND antrhacycline AND cardiotoxicity` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline-induced cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND rs7853758 AND anthracycline` — 2 terms, 0 back-off(s), 2 hit(s)
- `RARG AND rs2229774 AND anthracycline-induced cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND cardiotoxicity AND rs1695 AND anthracycline` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42525877` — **Cardiometabolic Risk and Awareness of Anthracycline-Related Cardiotoxicity in Survivors of Childhood Cancer: A Population-Based Study.** — *Journal of pediatric hematology/oncology · 2026*
  - via `free3:anthracycline cardiotoxicity childhood cancer survivors`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `free3:"SLC28A3" AND anthracycline AND cardiotoxicity`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `free4:(RARG OR rs2229774) AND anthracycline AND cardiotoxicity`
- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `free1:anthracycline-induced cardiotoxicity`

</details>

### Phase 11 — evidence ledger

**Genes:** GSTP1, SLC28A3  ·  **Evidence:** 13 refs, 6 papers

The pharmacogenomic biomarkers that predict anthracycline-induced cardiotoxicity in childhood cancer survivors are not definitively established, but there is evidence suggesting a potential role for certain genetic variations such as SLC28A3 (rs7853758) and GSTP1 (rs1695). However, the current evidence level is low to moderate due to conflicting data from clinical studies. The likely biological mechanism involves altered drug transport or metabolism affecting anthracycline cardiotoxicity risk. For drug development, further validation of these biomarkers in larger cohorts is necessary before implementing them for patient safety measures such as dose adjustment or alternative agent selection.

<details><summary>Queries issued (combined terms)</summary>

- `anthracycline AND cardiotoxicity AND childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695 AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `RARG AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `childhood cancer survivors` — 1 terms, 0 back-off(s), 2 hit(s)
- `pharmacogenomics/pharmacogenomic AND antrhacycline AND cardiotoxicity AND childhood cancer survivors` — 4 terms, 0 back-off(s), 2 hit(s)
- `anthracycline-induced cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND rs7853758 AND anthracycline` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695 AND childhood cancer survivors` — 2 terms, 0 back-off(s), 2 hit(s)
- `RARG AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42525877` — **Cardiometabolic Risk and Awareness of Anthracycline-Related Cardiotoxicity in Survivors of Childhood Cancer: A Population-Based Study.** — *Journal of pediatric hematology/oncology · 2026*
  - via `free3:anthracycline cardiotoxicity childhood cancer survivors`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `free3:"SLC28A3" AND anthracycline AND cardiotoxicity`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `free3:"RARG" AND anthracycline AND cardiotoxicity`
- `PMID:42633983` — **Preliminary study on efficacy and safety of pixantrone in relapsed/refractory aggressive B-cell lymphomas: multicenter, retrospective cohort study by Polish Lymphoma Research Group (PLRG).** — *Chinese clinical oncology · 2026*
  - via `free2:anthracycline cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `free3:(pharmacogenomics OR pharmacogenomic) AND anthracycline AND cardiotoxicity`
- `PMID:42600597` — **TEMPORAL DYNAMICS OF GLOBAL LONGITUDINAL STRAIN AND NT-PROBNP IN THE EARLY DETECTION OF ANTHRACYCLINE-INDUCED CARDIOTOXICITY: A 24-MONTH PROSPECTIVE STUDY IN POSTMENOPAUSAL WOMEN WITH BREAST CANCER.** — *Georgian medical news · 2026*
  - via `free1:anthracycline-induced cardiotoxicity[mh]`

</details>

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

### Baseline A — no external sources

**Genes:** CYP2D6  ·  **Evidence:** 0 refs, 0 papers

The adverse cardiac effects observed in your son are likely due to the interaction between his CYP2D6*4 genetic variant and doxorubicin treatment. The CYP2D6*4 variant impairs the metabolism of doxorubicin, potentially leading to higher systemic exposure and increased cardiotoxicity risk. This highlights the importance of pre-treatment biomarker screening for CYP2D6 variants in patients receiving doxorubicin or similar drugs. Additionally, dose adjustment or consideration of alternative agents with less dependence on CYP2D6 metabolism should be considered to mitigate cardiac risks.

### Baseline B — paper setup

**Genes:** CYP2D6  ·  **Evidence:** 0 refs, 0 papers

The early heart failure observed in your son is likely due to the combined effect of his CYP2D6*4 genetic variant and treatment with doxorubicin. The CYP2D6*4 variant impairs drug metabolism, potentially leading to higher levels of doxorubicin, which is known for its cardiotoxic effects. This interaction increases the risk of heart failure in patients treated with doxorubicin. For future drug discovery and patient safety, it is crucial to screen for CYP2D6 variants before initiating doxorubicin treatment, consider dose adjustments based on genetic profiles, or explore alternative agents that are less cardiotoxic.

### Phase 3 (old run) — ClinPGx

**Genes:** CYP2D6, SLC28A3  ·  **Evidence:** 0 refs, 0 papers

The early heart failure observed in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may reduce the metabolic capacity for certain drugs and increase susceptibility to cardiotoxicity. Additionally, SLC28A3 (rs7853758) has been linked to doxorubicin-related cardiotoxicity at a PharmGKB evidence level of 2B, suggesting that this genetic variation might also contribute to the adverse cardiac effects. For drug discovery and patient safety, pre-treatment biomarker screening for CYP2D6*4 and SLC28A3 variants is recommended to identify patients at higher risk of cardiotoxicity. Dose adjustment or alternative agents with lower cardiotoxic potential should be considered in these high-risk individuals.

### Phase 3 — ClinPGx only

**Genes:** CYP2D6, SLC28A3  ·  **Evidence:** 7 refs, 0 papers

The early heart failure observed in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may reduce the metabolic capacity for certain drugs and increase susceptibility to cardiotoxicity. Additionally, SLC28A3 (rs7853758) has been linked to doxorubicin-related cardiotoxicity at a PharmGKB evidence level of 2B, suggesting that this genetic variation might also contribute to the adverse cardiac effects. For drug discovery and patient safety, pre-treatment biomarker screening for CYP2D6*4 and SLC28A3 variants is recommended to identify patients at higher risk of cardiotoxicity. Dose adjustment or alternative agents with lower cardiotoxic potential should be considered in these high-risk individuals.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** CYP2D6, SLC28A3  ·  **Evidence:** 20 refs, 13 papers

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may alter drug metabolism and increase cardiotoxicity risk. Although there's no direct pharmacogenomic link between CYP2D6 and doxorubicin, the prolonged exposure to higher levels of doxorubicin due to reduced clearance could exacerbate cardiac side effects. Additionally, screening for SLC28A3 variants like rs7853758 might provide further insights into cardiotoxicity risk. For drug discovery and patient safety, pre-treatment genetic testing should be considered to identify high-risk patients who may benefit from dose adjustments or alternative treatments.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:12920424` — **Adverse drug reactions to oxycodone and hydrocodone in CYP2D6 ultrarapid metabolizers.** — *Journal of clinical psychopharmacology · 2003*
  - via `clinpgx_citation`
- `PMID:14998425` — **CYP2D6 and CYP3A4 involvement in the primary oxidative metabolism of hydrocodone by human liver microsomes.** — *British journal of clinical pharmacology · 2004*
  - via `clinpgx_citation`
- `PMID:42599271` — **High-Grade Myoepithelial Carcinoma with EWSR1::CREB1 Fusion in the Submandibular Gland of a Young Man: Salivary or Soft Tissue Type?** — *International journal of surgical pathology · 2026*
  - via `-`
- `PMID:42599237` — **[Effect of ESR1 Somatic Mutations on SERM/SERD Binding: Insights from Molecular Docking and Molecular Dynamics Simulations].** — *Molekuliarnaia biologiia · 2026*
  - via `-`
- `PMID:10233212` — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - via `clinpgx_citation`
- `PMID:10774634` — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:32587261` — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** CYP2D6, SLC28A3  ·  **Evidence:** 20 refs, 13 papers

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may alter drug metabolism and increase cardiotoxicity risk. Although there's no direct pharmacogenomic link between CYP2D6 and doxorubicin, the prolonged exposure to higher levels of doxorubicin due to reduced clearance could exacerbate cardiac side effects. Additionally, screening for SLC28A3 variants like rs7853758 might provide further insights into cardiotoxicity risk. For drug discovery and patient safety, pre-treatment genetic testing should be considered to identify high-risk patients who may benefit from dose adjustments or alternative treatments.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:12920424` — **Adverse drug reactions to oxycodone and hydrocodone in CYP2D6 ultrarapid metabolizers.** — *Journal of clinical psychopharmacology · 2003*
  - via `clinpgx_citation`
- `PMID:14998425` — **CYP2D6 and CYP3A4 involvement in the primary oxidative metabolism of hydrocodone by human liver microsomes.** — *British journal of clinical pharmacology · 2004*
  - via `clinpgx_citation`
- `PMID:42599271` — **High-Grade Myoepithelial Carcinoma with EWSR1::CREB1 Fusion in the Submandibular Gland of a Young Man: Salivary or Soft Tissue Type?** — *International journal of surgical pathology · 2026*
  - via `-`
- `PMID:42599237` — **[Effect of ESR1 Somatic Mutations on SERM/SERD Binding: Insights from Molecular Docking and Molecular Dynamics Simulations].** — *Molekuliarnaia biologiia · 2026*
  - via `-`
- `PMID:10233212` — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - via `clinpgx_citation`
- `PMID:10774634` — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:28763429` — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - via `clinpgx_citation`

</details>

### Phase 6 — open LLM search

**Genes:** CYP2D6  ·  **Evidence:** 29 refs, 20 papers

The adverse reaction observed in your son is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of doxorubicin, exacerbating cardiotoxicity. The biological mechanism involves altered drug metabolism leading to increased toxicity. For patient safety, pre-treatment genetic screening for CYP2D6 variants is recommended to identify high-risk patients who might benefit from dose adjustments or alternative treatments with lower cardiotoxic potential.

<details><summary>Papers retrieved</summary>

- `PMID:38196322` — **Clinical significance of coadministration of moderate to strong CYP enzyme inhibitors with doxorubicin in breast cancer patients receiving AC chemotherapy.** — *Journal of oncology pharmacy practice : official publication of the International Society of Oncology Pharmacy Practitioners · 2025*
  - via `llm_topic:doxorubicin cardiotoxicity CYP2D6`
- `PMID:33900042` — **Pharmacogenetic testing to guide therapeutic decision-making and improve outcomes for children undergoing anthracycline-based chemotherapy.** — *Basic & clinical pharmacology & toxicology · 2022*
  - via `llm_topic:SLC28A3 heart failure`
- `PMID:42530245` — **Transcriptomic and Single-Cell Analyses Reveal a Prognostic Mitochondria- and Immunity-Related Risk Signature in Osteosarcoma.** — *Frontiers in bioscience (Landmark edition) · 2026*
  - via `llm_topic:GSTP1 neoplasm risk`
- `PMID:42217759` — **Antiplatelet activity of novel aminoestrogens: R-β-mefenetame as a candidate for safer estrogen-based therapies.** — *The Journal of steroid biochemistry and molecular biology · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:41532000` — **Personalizing Treatment for Acute Alcoholic Hallucinosis: Clinical Utility of Integrated Pharmacogenetic Testing, Metabolic Phenotyping, and microRNA Biomarkers.** — *Psychopharmacology bulletin · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635550` — **Clinical validation of the nursing diagnosis of inadequate nutritional intake in children with cancer.** — *International journal of nursing knowledge · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635508` — **Eating Experiences During Cancer Treatment in Adolescents and Young Adults: A Systematic Literature Review and Meta-Synthesis.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635410` — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:heart failure`
- `PMID:42635407` — **MxA expression in systemic lupus erythematosus -associated myocarditis indicates type I interferon pathway activation.** — *Immunological medicine · 2026*
  - via `llm_topic:heart failure`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42634505` — **Innovative Insights into Osteosarcoma: Unraveling the Role of LncRNAs, miRNAs, and CircRNAs in Tumorigenesis and Therapeutic Resistance.** — *Current gene therapy · 2026*
  - via `llm_topic:osteosarcoma`
- `PMID:42634348` — **Development of a Prognostic Model Based on SCISSOR+ Osteoblastic Osteosarcoma Cell-Associated Genes.** — *Current medicinal chemistry · 2026*
  - via `llm_topic:osteosarcoma`
- `PMID:27197003` — **Recommendations for genetic testing to reduce the incidence of anthracycline-induced cardiotoxicity.** — *British journal of clinical pharmacology · 2016*
  - via `llm_topic:SLC28A3 doxorubicin heart failure`

</details>

### Phase 7 — open search + full text

**Genes:** CYP2D6  ·  **Evidence:** 29 refs, 20 papers

The adverse reaction observed in your son is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of doxorubicin, exacerbating cardiotoxicity. The biological mechanism involves altered drug metabolism leading to increased toxicity. For patient safety, pre-treatment genetic screening for CYP2D6 variants is recommended to identify high-risk patients who might benefit from dose adjustments or alternative treatments with lower cardiotoxic potential.

<details><summary>Papers retrieved</summary>

- `PMID:38196322` — **Clinical significance of coadministration of moderate to strong CYP enzyme inhibitors with doxorubicin in breast cancer patients receiving AC chemotherapy.** — *Journal of oncology pharmacy practice : official publication of the International Society of Oncology Pharmacy Practitioners · 2025*
  - via `llm_topic:doxorubicin cardiotoxicity CYP2D6`
- `PMID:33900042` — **Pharmacogenetic testing to guide therapeutic decision-making and improve outcomes for children undergoing anthracycline-based chemotherapy.** — *Basic & clinical pharmacology & toxicology · 2022*
  - via `llm_topic:SLC28A3 heart failure`
- `PMID:42530245` — **Transcriptomic and Single-Cell Analyses Reveal a Prognostic Mitochondria- and Immunity-Related Risk Signature in Osteosarcoma.** — *Frontiers in bioscience (Landmark edition) · 2026*
  - via `llm_topic:GSTP1 neoplasm risk`
- `PMID:42217759` — **Antiplatelet activity of novel aminoestrogens: R-β-mefenetame as a candidate for safer estrogen-based therapies.** — *The Journal of steroid biochemistry and molecular biology · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:41532000` — **Personalizing Treatment for Acute Alcoholic Hallucinosis: Clinical Utility of Integrated Pharmacogenetic Testing, Metabolic Phenotyping, and microRNA Biomarkers.** — *Psychopharmacology bulletin · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635550` — **Clinical validation of the nursing diagnosis of inadequate nutritional intake in children with cancer.** — *International journal of nursing knowledge · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635508` — **Eating Experiences During Cancer Treatment in Adolescents and Young Adults: A Systematic Literature Review and Meta-Synthesis.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635410` — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:heart failure`
- `PMID:42635407` — **MxA expression in systemic lupus erythematosus -associated myocarditis indicates type I interferon pathway activation.** — *Immunological medicine · 2026*
  - via `llm_topic:heart failure`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42634505` — **Innovative Insights into Osteosarcoma: Unraveling the Role of LncRNAs, miRNAs, and CircRNAs in Tumorigenesis and Therapeutic Resistance.** — *Current gene therapy · 2026*
  - via `llm_topic:osteosarcoma`
- `PMID:42634348` — **Development of a Prognostic Model Based on SCISSOR+ Osteoblastic Osteosarcoma Cell-Associated Genes.** — *Current medicinal chemistry · 2026*
  - via `llm_topic:osteosarcoma`
- `PMID:27197003` — **Recommendations for genetic testing to reduce the incidence of anthracycline-induced cardiotoxicity.** — *British journal of clinical pharmacology · 2016*
  - via `llm_topic:SLC28A3 doxorubicin heart failure`

</details>

### Phase 8 — combined-topic search

**Genes:** CYP2D6  ·  **Evidence:** 20 refs, 13 papers

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of unmetabolized doxorubicin. This increased exposure can exacerbate cardiotoxicity due to prolonged cardiac tissue damage. For drug discovery and patient safety, pre-treatment screening for CYP2D6 variants is crucial to identify patients at risk and consider dose adjustments or alternative agents with lower cardiotoxic potential.

<details><summary>Queries issued (combined terms)</summary>

- `CYP2D6*4 AND doxorubicin` — 2 terms, 0 back-off(s), 0 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND heart failure` — 2 terms, 0 back-off(s), 0 hit(s)
- `RARG AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin` — 2 terms, 1 back-off(s), 0 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `Neoplasm AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `heart failure AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `RARG rs2229774 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `CDKN1A Suppression AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `doxorubicin AND CYP2D6*4` — 2 terms, 0 back-off(s), 0 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND rs7853758` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42627580` — **Integrated Multi-omics Reveals CDKN1A Suppression and Metabolic Regulation as Key Mechanisms of Huangqi Guizhi Wuwu Decoction Against Doxorubicin-Induced Cardiotoxicity.** — *Cardiovascular toxicology · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `combo2:RARG + doxorubicin`
- `PMID:42624274` — **Ginkgolide B Mitigates Doxorubicin-Induced Cardiotoxicity by Regulating AMPK-Mediated Mitochondrial Fission via P-Drp1/OPA1 and Apoptosis.** — *Archives of biochemistry and biophysics · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42593900` — **Discovery of ZJC-11 as a Novel Selective CDK7 Inhibitor for Treating Triple-Negative Breast Cancer by Inducing Cell Senescence.** — *Journal of medicinal chemistry · 2026*
  - via `combo3:Neoplasm + doxorubicin + cardiotoxicity`
- `PMID:42420767` — **Anthracycline chemotherapy does not increase arterial stiffness or carotid intima-media thickness in young adult survivors of hematological malignancies.** — *Journal of applied physiology (Bethesda, Md. : 1985) · 2026*
  - via `combo3:Neoplasm + doxorubicin + cardiotoxicity`
- `PMID:42608157` — **Ferroptosis in Anthracycline Cardiotoxicity: Mechanisms, the Cardioprotection Paradox and the Limits of Single-Pathway Thinking.** — *Journal of applied toxicology : JAT · 2026*
  - via `combo3:heart failure + doxorubicin + cardiotoxicity`
- `PMID:42596797` — **A recent update on luteolin: mechanisms and therapeutic implications in cardiac disease.** — *Journal of basic and clinical physiology and pharmacology · 2026*
  - via `combo3:heart failure + doxorubicin + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:37828659` — **The Role of RARG rs2229774, SLC28A3 rs7853758, and UGT1A6*4 rs17863783 Single-nucleotide Polymorphisms in the Doxorubicin-induced Cardiotoxicity in Solid Childhood Tumors.** — *Journal of pediatric hematology/oncology · 2024*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:26354850` — **GSTP1 and GSTO1 single nucleotide polymorphisms and the response of bladder cancer patients to intravesical chemotherapy.** — *Scientific reports · 2015*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + doxorubicin + cardiotoxicity`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `combo2:SLC28A3 + rs7853758`

</details>

### Phase 9 — combined + full text

**Genes:** CYP2D6  ·  **Evidence:** 20 refs, 13 papers

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of unmetabolized doxorubicin. This increased exposure can exacerbate cardiotoxicity due to prolonged cardiac tissue damage. For drug discovery and patient safety, pre-treatment screening for CYP2D6 variants is crucial to identify patients at risk and consider dose adjustments or alternative agents with lower cardiotoxic potential.

<details><summary>Queries issued (combined terms)</summary>

- `CYP2D6*4 AND doxorubicin` — 2 terms, 0 back-off(s), 0 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND heart failure` — 2 terms, 0 back-off(s), 0 hit(s)
- `RARG AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin` — 2 terms, 1 back-off(s), 0 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `Neoplasm AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `heart failure AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `RARG rs2229774 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `CDKN1A Suppression AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `doxorubicin AND CYP2D6*4` — 2 terms, 0 back-off(s), 0 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3 AND rs7853758` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 AND rs1695` — 2 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42627580` — **Integrated Multi-omics Reveals CDKN1A Suppression and Metabolic Regulation as Key Mechanisms of Huangqi Guizhi Wuwu Decoction Against Doxorubicin-Induced Cardiotoxicity.** — *Cardiovascular toxicology · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `combo2:RARG + doxorubicin`
- `PMID:42624274` — **Ginkgolide B Mitigates Doxorubicin-Induced Cardiotoxicity by Regulating AMPK-Mediated Mitochondrial Fission via P-Drp1/OPA1 and Apoptosis.** — *Archives of biochemistry and biophysics · 2026*
  - via `combo2:doxorubicin + cardiotoxicity`
- `PMID:42593900` — **Discovery of ZJC-11 as a Novel Selective CDK7 Inhibitor for Treating Triple-Negative Breast Cancer by Inducing Cell Senescence.** — *Journal of medicinal chemistry · 2026*
  - via `combo3:Neoplasm + doxorubicin + cardiotoxicity`
- `PMID:42420767` — **Anthracycline chemotherapy does not increase arterial stiffness or carotid intima-media thickness in young adult survivors of hematological malignancies.** — *Journal of applied physiology (Bethesda, Md. : 1985) · 2026*
  - via `combo3:Neoplasm + doxorubicin + cardiotoxicity`
- `PMID:42608157` — **Ferroptosis in Anthracycline Cardiotoxicity: Mechanisms, the Cardioprotection Paradox and the Limits of Single-Pathway Thinking.** — *Journal of applied toxicology : JAT · 2026*
  - via `combo3:heart failure + doxorubicin + cardiotoxicity`
- `PMID:42596797` — **A recent update on luteolin: mechanisms and therapeutic implications in cardiac disease.** — *Journal of basic and clinical physiology and pharmacology · 2026*
  - via `combo3:heart failure + doxorubicin + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:37828659` — **The Role of RARG rs2229774, SLC28A3 rs7853758, and UGT1A6*4 rs17863783 Single-nucleotide Polymorphisms in the Doxorubicin-induced Cardiotoxicity in Solid Childhood Tumors.** — *Journal of pediatric hematology/oncology · 2024*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:26354850` — **GSTP1 and GSTO1 single nucleotide polymorphisms and the response of bladder cancer patients to intravesical chemotherapy.** — *Scientific reports · 2015*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + doxorubicin + cardiotoxicity`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `combo2:SLC28A3 + rs7853758`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** CYP2D6  ·  **Evidence:** 14 refs, 5 papers

The adverse reaction observed in your son is likely influenced by the CYP2D6*4 genetic variant, which affects drug metabolism and can increase cardiotoxicity risks associated with doxorubicin treatment. The biological mechanism involves increased susceptibility to doxorubicin-induced damage to cardiomyocytes due to altered drug metabolism, leading to elevated reactive oxygen species (ROS) levels and apoptosis in cardiac cells. For patient safety, pre-treatment genetic screening for CYP2D6 variants is recommended to identify individuals at higher risk of cardiotoxicity. Additionally, dose adjustment or the use of cardioprotective agents may be considered during chemotherapy.

<details><summary>Queries issued (combined terms)</summary>

- `CYP2D6*4` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure AND cardiotoxicity` — 1 terms, 2 back-off(s), 2 hit(s)
- `CYP2D6*4 AND Neoplasm AND doxorubicin` — 1 terms, 2 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6/CYP2D6*4 AND doxorubicin AND heart failure` — 2 terms, 1 back-off(s), 2 hit(s)
- `Neoplasm AND CYP2D6*4 AND cardiotoxicity` — 1 terms, 3 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42217759` — **Antiplatelet activity of novel aminoestrogens: R-β-mefenetame as a candidate for safer estrogen-based therapies.** — *The Journal of steroid biochemistry and molecular biology · 2026*
  - via `free1:CYP2D6*4[gene]`
- `PMID:42594973` — **Vincristine enhances doxorubicin cardiotoxicity in human iPSC-derived cardiomyocytes: Partial attenuation by SGLT2 inhibition.** — *Toxicology and applied pharmacology · 2026*
  - via `free2:"doxorubicin cardiotoxicity"`
- `PMID:41532000` — **Personalizing Treatment for Acute Alcoholic Hallucinosis: Clinical Utility of Integrated Pharmacogenetic Testing, Metabolic Phenotyping, and microRNA Biomarkers.** — *Psychopharmacology bulletin · 2026*
  - via `free1:CYP2D6*4[gene]`
- `PMID:42612758` — **Doxorubicin-induced damage to AC16 cardiomyocytes and attenuation by human pericardial fluid Sca-1+/Nanog+ cells conditioned medium: a pilot study.** — *Biochimica et biophysica acta. General subjects · 2026*
  - via `free2:(doxorubicin AND heart failure)[tiab]`
- `PMID:42636514` — **Targeting ID2 to augment doxorubicin antitumor efficacy and enhance antibacterial defense without neutropenia.** — *International immunopharmacology · 2026*
  - via `free2:doxorubicin AND cardiotoxicity`

</details>

### Phase 11 — evidence ledger

**Genes:** CYP2D6, SLC28A3  ·  **Evidence:** 14 refs, 5 papers

The concern about early heart failure in your son who carries the CYP2D6*4 genetic variant and was treated with doxorubicin for his neoplasm is well-founded. The CYP2D6*4 variant, which affects drug metabolism, may increase susceptibility to doxorubicin-induced cardiotoxicity due to altered drug processing. Although there is no direct evidence linking CYP2D6*4 specifically to doxorubicin from PharmGKB, the medical knowledge graph indicates a moderate risk factor for heart failure (confidence: 0.80). The specific type of cancer does not significantly alter this general risk but may influence treatment duration and dosage. For drug discovery and patient safety, screening for CYP2D6*4 could help identify patients at higher risk for cardiotoxicity, potentially guiding dose adjustments or the use of alternative agents to mitigate adverse effects.

<details><summary>Queries issued (combined terms)</summary>

- `CYP2D6*4` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 1 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure AND cardiotoxicity` — 1 terms, 2 back-off(s), 2 hit(s)
- `CYP2D6*4 AND Neoplasm AND doxorubicin` — 1 terms, 2 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 1 back-off(s), 2 hit(s)
- `doxorubicin AND heart failure` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4 AND doxorubicin AND heart failure` — 1 terms, 2 back-off(s), 2 hit(s)
- `pharmacogenomics AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6*4` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYP2D6/CYP2D6*4 AND doxorubicin AND heart failure` — 2 terms, 1 back-off(s), 2 hit(s)
- `Neoplasm AND CYP2D6*4 AND cardiotoxicity` — 1 terms, 3 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42217759` — **Antiplatelet activity of novel aminoestrogens: R-β-mefenetame as a candidate for safer estrogen-based therapies.** — *The Journal of steroid biochemistry and molecular biology · 2026*
  - via `free1:CYP2D6*4[gene]`
- `PMID:42594973` — **Vincristine enhances doxorubicin cardiotoxicity in human iPSC-derived cardiomyocytes: Partial attenuation by SGLT2 inhibition.** — *Toxicology and applied pharmacology · 2026*
  - via `free2:"doxorubicin cardiotoxicity"`
- `PMID:41532000` — **Personalizing Treatment for Acute Alcoholic Hallucinosis: Clinical Utility of Integrated Pharmacogenetic Testing, Metabolic Phenotyping, and microRNA Biomarkers.** — *Psychopharmacology bulletin · 2026*
  - via `free1:CYP2D6*4[gene]`
- `PMID:42612758` — **Doxorubicin-induced damage to AC16 cardiomyocytes and attenuation by human pericardial fluid Sca-1+/Nanog+ cells conditioned medium: a pilot study.** — *Biochimica et biophysica acta. General subjects · 2026*
  - via `free2:(doxorubicin AND heart failure)[tiab]`
- `PMID:42643688` — **Borneol-based nanoparticles encapsulating Doxorubicin/Sodium tanshinone IIA sulfonate enhance the effect of anti-glioma and alleviate cardiotoxicity.** — *Cytotechnology · 2026*
  - via `free2:doxorubicin AND cardiotoxicity`

</details>

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

### Baseline A — no external sources

**Genes:** GSTM1  ·  **Evidence:** 0 refs, 0 papers

The adverse cardiac effects observed in your daughter after Adriamycin treatment are likely influenced by her GSTM1 status. The GSTM1 enzyme is involved in detoxifying harmful substances, including those that may contribute to heart damage from chemotherapy drugs like Adriamycin. Individuals with null variants of GSTM1 have reduced capacity for detoxification, potentially increasing their risk of cardiotoxicity. For drug discovery and patient safety, pre-treatment biomarker screening for GSTM1 status could help identify patients at higher risk of cardiac toxicity, allowing for dose adjustments or the use of alternative agents to mitigate these risks.

### Baseline B — paper setup

**Genes:** GSTM1  ·  **Evidence:** 0 refs, 0 papers

The GSTM1 gene is implicated in the cardiac strain and heart muscle damage observed following Adriamycin treatment. The likely biological mechanism involves GSTM1's role in detoxifying reactive metabolites that can cause oxidative stress, leading to cardiotoxicity when this process is impaired. For drug discovery and patient safety, pre-treatment screening for GSTM1 variants should be considered to identify patients at higher risk of cardiac side effects from Adriamycin. This could inform dose adjustments or the use of alternative agents with lower cardiotoxic potential.

### Phase 3 (old run) — ClinPGx

**Genes:** GSTM1, GSTP1, SLC28A3  ·  **Evidence:** 0 refs, 0 papers

Adriamycin-induced cardiotoxicity is associated with cardiac strain and heart muscle damage. While the GSTM1 gene shows an indirect connection as a risk factor, it is less well-established compared to SLC28A3 (rs7853758) and GSTP1 (rs1695), which have stronger evidence linking them to Adriamycin-related cardiotoxicity. The biological mechanism likely involves genetic variations affecting drug metabolism or transport, leading to altered Adriamycin levels or activity in the heart tissue. For patient safety, pre-treatment screening for SLC28A3 and GSTP1 variants could help identify individuals at higher risk of cardiotoxicity, allowing for dose adjustments or alternative chemotherapy agents to be considered.

### Phase 3 — ClinPGx only

**Genes:** GSTM1, GSTP1, SLC28A3  ·  **Evidence:** 8 refs, 0 papers

Adriamycin-induced cardiotoxicity is associated with cardiac strain and heart muscle damage. While the GSTM1 gene shows an indirect connection as a risk factor, it is less well-established compared to SLC28A3 (rs7853758) and GSTP1 (rs1695), which have stronger evidence linking them to Adriamycin-related cardiotoxicity. The biological mechanism likely involves genetic variations affecting drug metabolism or transport, leading to altered Adriamycin levels or activity in the heart tissue. For patient safety, pre-treatment screening for SLC28A3 and GSTP1 variants could help identify individuals at higher risk of cardiotoxicity, allowing for dose adjustments or alternative chemotherapy agents to be considered.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** GSTM1, SLC28A3  ·  **Evidence:** 21 refs, 13 papers

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by genetic factors such as the GSTM1 genotype and a synonymous coding variant rs7853758 within the SLC28A3 gene. These genetic variations may modulate an individual's susceptibility to doxorubicin-induced cardiotoxicity through mechanisms that affect drug metabolism, transport, or cellular response pathways. For future drug discovery efforts and patient safety, pre-treatment biomarker screening for these variants could help identify patients at higher risk of developing heart damage from Adriamycin, enabling dose adjustments or the use of alternative therapies to mitigate this risk.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:42598455` — **Endovascular technology for aortic arch repair: from innovation to integration.** — *Annals of cardiothoracic surgery · 2026*
  - via `-`
- `PMID:42597513` — **Risk factors for cardiac dysfunction caused by anthracycline drugs in the treatment of lymphoma and the early monitoring value of three-dimensional echocardiography.** — *American journal of cancer research · 2026*
  - via `-`
- `PMID:10233212` — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - via `clinpgx_citation`
- `PMID:10774634` — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - via `clinpgx_citation`
- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:32587261` — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** GSTM1, SLC28A3  ·  **Evidence:** 21 refs, 13 papers

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by genetic factors such as the GSTM1 genotype and a synonymous coding variant rs7853758 within the SLC28A3 gene. These genetic variations may modulate an individual's susceptibility to doxorubicin-induced cardiotoxicity through mechanisms that affect drug metabolism, transport, or cellular response pathways. For future drug discovery efforts and patient safety, pre-treatment biomarker screening for these variants could help identify patients at higher risk of developing heart damage from Adriamycin, enabling dose adjustments or the use of alternative therapies to mitigate this risk.

<details><summary>Papers retrieved</summary>

- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:25823784` — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - via `clinpgx_citation`
- `PMID:42598455` — **Endovascular technology for aortic arch repair: from innovation to integration.** — *Annals of cardiothoracic surgery · 2026*
  - via `-`
- `PMID:42597513` — **Risk factors for cardiac dysfunction caused by anthracycline drugs in the treatment of lymphoma and the early monitoring value of three-dimensional echocardiography.** — *American journal of cancer research · 2026*
  - via `-`
- `PMID:10233212` — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - via `clinpgx_citation`
- `PMID:10774634` — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - via `clinpgx_citation`
- `PMID:17228018` — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - via `clinpgx_citation`
- `PMID:20530282` — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - via `clinpgx_citation`
- `PMID:15213713` — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - via `clinpgx_citation`
- `PMID:16707601` — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - via `clinpgx_citation`
- `PMID:26237429` — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - via `clinpgx_citation`
- `PMID:28763429` — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - via `clinpgx_citation`

</details>

### Phase 6 — open LLM search

**Genes:** GSTM1  ·  **Evidence:** 27 refs, 19 papers

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by her GSTM1 genotype, as functional studies suggest that GSTM1 may play a role in anthracycline-induced cardiotoxicity. The biological mechanism involves the potential modulation of doxorubicin metabolism and detoxification pathways by GSTM1, which could exacerbate or mitigate cardiac strain and heart muscle damage. For drug discovery and patient safety, pre-treatment screening for GSTM1 status may help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or consideration of alternative agents to minimize cardiac injury.

<details><summary>Papers retrieved</summary>

- `PMID:38510289` — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `llm_topic:adriamycin cardiotoxicity gstm1`
- `PMID:42559407` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `llm_topic:doxorubicin heart damage genetics`
- `PMID:42176227` — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:anthracycline toxicity slc28a3`
- `PMID:42635315` — **Baseline podocyte-associated state and persistent cell-matrix transcriptional programs are associated with BALB/c substrain differences in adriamycin nephropathy.** — *Animal models and experimental medicine · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42635410` — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42634934` — **Multimodal Framework of Left Heart-Pulmonary Vascular Remodeling Underlying Right Ventricular Failure in PH-HFpEF.** — *Circulation. Heart failure · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42633868` — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42577562` — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42561509` — **Loki Zupa alleviates type 2-high acute asthma airway inflammation by regulating the glutathione metabolism-ferroptosis axis.** — *Phytomedicine : international journal of phytotherapy and phytopharmacology · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42522562` — **Meta-Analysis of Genome-Wide Association Studies of Doxorubicin-Induced Arrhythmia Identifies MMP16 and KCTD15 as Risk Loci.** — *Circulation. Genomic and precision medicine · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42522188` — **Inhibition of late sodium current prevents pathological hyperactivation of calcium/calmodulin-dependent protein kinase IIδ in a murine model of acute doxorubicin-related cardiotoxicity.** — *British journal of pharmacology · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42520516` — **Machine learning, WGCNA and molecular docking identify SLC transporter genes as biomarkers and drug targets in Helicobacter pylori-associated carcinogenesis.** — *Bioorganic chemistry · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42634868` — **Prunetin Attenuates Dexamethasone-Induced Pancreatic β-Cell Apoptosis: Modulation of Oxidative Stress and MAPK Signaling but Not Phosphorylated C-Abl Levels.** — *Cell biochemistry and function · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42631444` — **Low-Cost Nucleic-Acid-Based Radial Flow Assay for the Detection of GSTP1 Promoter DNA Methylation in Prostate Cancer.** — *ACS applied bio materials · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42555353` — **ID2 Unlocks retinoic acid signaling to promote eosinophil maturation by antagonizing TCF3.** — *Cell reports · 2026*
  - via `llm_topic:RARG`
- `PMID:42434795` — **Rh-Induced Oxygen Vacancies in a PdRh/SnO2 Heterointerface for Enhanced MEMS Hydrogen Detection.** — *ACS sensors · 2026*
  - via `llm_topic:RARG`

</details>

### Phase 7 — open search + full text

**Genes:** GSTM1, SLC28A3  ·  **Evidence:** 29 refs, 21 papers, 2 full text

The adverse cardiac effects observed in your daughter after Adriamycin treatment are likely influenced by genetic factors such as GSTM1, which is a risk factor for doxorubicin-induced cardiotoxicity. The biological mechanism involves the role of transporters like SLC28A3 and detoxification enzymes like those encoded by GSTM1, which can affect drug uptake, distribution, metabolism, and excretion, thereby modulating the extent of cardiac damage caused by Adriamycin. For drug discovery and patient safety, pre-treatment genetic screening for variants in genes such as GSTM1 and SLC28A3 could help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate adverse effects.

<details><summary>Papers retrieved</summary>

- `PMID:38510289` — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `llm_topic:adriamycin cardiotoxicity gstm1`
- `PMID:42559407` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `llm_topic:doxorubicin heart damage genetics`
- `PMID:42176227` — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:anthracycline toxicity slc28a3`
- `PMID:42635315` — **Baseline podocyte-associated state and persistent cell-matrix transcriptional programs are associated with BALB/c substrain differences in adriamycin nephropathy.** — *Animal models and experimental medicine · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42635410` — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42634934` — **Multimodal Framework of Left Heart-Pulmonary Vascular Remodeling Underlying Right Ventricular Failure in PH-HFpEF.** — *Circulation. Heart failure · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42633868` — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42577562` — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42561509` — **Loki Zupa alleviates type 2-high acute asthma airway inflammation by regulating the glutathione metabolism-ferroptosis axis.** — *Phytomedicine : international journal of phytotherapy and phytopharmacology · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42522562` — **Meta-Analysis of Genome-Wide Association Studies of Doxorubicin-Induced Arrhythmia Identifies MMP16 and KCTD15 as Risk Loci.** — *Circulation. Genomic and precision medicine · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42522188` — **Inhibition of late sodium current prevents pathological hyperactivation of calcium/calmodulin-dependent protein kinase IIδ in a murine model of acute doxorubicin-related cardiotoxicity.** — *British journal of pharmacology · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42549829` — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42520516` — **Machine learning, WGCNA and molecular docking identify SLC transporter genes as biomarkers and drug targets in Helicobacter pylori-associated carcinogenesis.** — *Bioorganic chemistry · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42634868` — **Prunetin Attenuates Dexamethasone-Induced Pancreatic β-Cell Apoptosis: Modulation of Oxidative Stress and MAPK Signaling but Not Phosphorylated C-Abl Levels.** — *Cell biochemistry and function · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42631444` — **Low-Cost Nucleic-Acid-Based Radial Flow Assay for the Detection of GSTP1 Promoter DNA Methylation in Prostate Cancer.** — *ACS applied bio materials · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42555353` — **ID2 Unlocks retinoic acid signaling to promote eosinophil maturation by antagonizing TCF3.** — *Cell reports · 2026*
  - via `llm_topic:RARG`
- `PMID:42434795` — **Rh-Induced Oxygen Vacancies in a PdRh/SnO2 Heterointerface for Enhanced MEMS Hydrogen Detection.** — *ACS sensors · 2026*
  - via `llm_topic:RARG`
- `PMID:38510289/PMC10950437` — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `llm_topic:adriamycin cardiotoxicity gstm1+pmc_xml`
- `PMID:42559407/PMC13440645` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `llm_topic:doxorubicin heart damage genetics+pmc_xml`

</details>

### Phase 8 — combined-topic search

**Genes:** GSTM1  ·  **Evidence:** 22 refs, 14 papers

The adverse cardiac strain and heart muscle damage experienced by the patient's daughter after taking Adriamycin may be influenced by her GSTM1 status, as indicated by a moderate confidence level (0.70) linking GSTM1 to increased risk of cardiotoxicity from this drug. The biological mechanism likely involves oxidative stress and vascular aging, given that upregulation of GSTM1 is associated with these conditions in endothelial cells. For drug discovery and patient safety, pre-treatment genetic screening for specific GSTM1 variants could help identify patients at higher risk of Adriamycin-induced cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate this risk.

<details><summary>Queries issued (combined terms)</summary>

- `Adriamycin AND cardiac strain` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND heart muscle damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `Adriamycin AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Cardiac strain AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Heart muscle damage AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `RARG rs2229774 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Doxorubicin AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Adriamycin AND cardiac strain` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND heart muscle damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTP1 AND rs1695` — 3 terms, 0 back-off(s), 2 hit(s)
- `Cardiotoxicity AND RARG AND rs2229774` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `combo2:Adriamycin + cardiac strain`
- `PMID:32896271` — **Direct reprogramming of human smooth muscle and vascular endothelial cells reveals defects associated with aging and Hutchinson-Gilford progeria syndrome.** — *eLife · 2020*
  - via `combo2:GSTM1 + heart muscle damage`
- `PMID:41823204` — **Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute Lymphoblastic Leukemia and Lymphoma Undergoing Chemotherapy.** — *Pediatric blood & cancer · 2026*
  - via `combo2:doxorubicin + GSTM1`
- `PMID:42627580` — **Integrated Multi-omics Reveals CDKN1A Suppression and Metabolic Regulation as Key Mechanisms of Huangqi Guizhi Wuwu Decoction Against Doxorubicin-Induced Cardiotoxicity.** — *Cardiovascular toxicology · 2026*
  - via `combo3:Adriamycin + doxorubicin + cardiotoxicity`
- `PMID:42624274` — **Ginkgolide B Mitigates Doxorubicin-Induced Cardiotoxicity by Regulating AMPK-Mediated Mitochondrial Fission via P-Drp1/OPA1 and Apoptosis.** — *Archives of biochemistry and biophysics · 2026*
  - via `combo3:Adriamycin + doxorubicin + cardiotoxicity`
- `PMID:42528395` — **Integrated Cantilever-MEA Platform for High-Sensitivity and Scalable Recording of Cardiomyocyte Electromechanics.** — *Small (Weinheim an der Bergstrasse, Germany) · 2026*
  - via `combo3:Cardiac strain + doxorubicin + cardiotoxicity`
- `PMID:42559407` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `combo3:Heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:42531631` — **Metal-dependent cell death in doxorubicin-induced cardiotoxicity and mitigation by luteolin: Network pharmacology and experimental verification.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo3:Heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:38510289` — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `combo3:GSTM1 + doxorubicin + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:37828659` — **The Role of RARG rs2229774, SLC28A3 rs7853758, and UGT1A6*4 rs17863783 Single-nucleotide Polymorphisms in the Doxorubicin-induced Cardiotoxicity in Solid Childhood Tumors.** — *Journal of pediatric hematology/oncology · 2024*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:26354850` — **GSTP1 and GSTO1 single nucleotide polymorphisms and the response of bladder cancer patients to intravesical chemotherapy.** — *Scientific reports · 2015*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + doxorubicin + cardiotoxicity`

</details>

### Phase 9 — combined + full text

**Genes:** GSTM1, SLC28A3  ·  **Evidence:** 23 refs, 15 papers, 1 full text

Adriamycin-induced cardiac strain and heart muscle damage may be influenced by genetic factors such as GSTM1, though the evidence linking these is not definitive. The biological mechanism likely involves oxidative stress and DNA damage caused by Adriamycin, which can vary in severity based on individual genetic predispositions. For drug discovery and patient safety, pre-treatment biomarker screening for genes like SLC28A3 could help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate adverse effects.

<details><summary>Queries issued (combined terms)</summary>

- `Adriamycin AND cardiac strain` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND heart muscle damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTM1` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND GSTP1` — 2 terms, 0 back-off(s), 2 hit(s)
- `Adriamycin AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Cardiac strain AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Heart muscle damage AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 1 hit(s)
- `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `GSTP1 rs1695 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `RARG rs2229774 AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Doxorubicin AND doxorubicin AND cardiotoxicity` — 3 terms, 0 back-off(s), 2 hit(s)
- `Adriamycin AND cardiac strain` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND heart muscle damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND GSTP1 AND rs1695` — 3 terms, 0 back-off(s), 2 hit(s)
- `Cardiotoxicity AND RARG AND rs2229774` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42618256` — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `combo2:Adriamycin + cardiac strain`
- `PMID:32896271` — **Direct reprogramming of human smooth muscle and vascular endothelial cells reveals defects associated with aging and Hutchinson-Gilford progeria syndrome.** — *eLife · 2020*
  - via `combo2:GSTM1 + heart muscle damage`
- `PMID:41823204` — **Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute Lymphoblastic Leukemia and Lymphoma Undergoing Chemotherapy.** — *Pediatric blood & cancer · 2026*
  - via `combo2:doxorubicin + GSTM1`
- `PMID:42627580` — **Integrated Multi-omics Reveals CDKN1A Suppression and Metabolic Regulation as Key Mechanisms of Huangqi Guizhi Wuwu Decoction Against Doxorubicin-Induced Cardiotoxicity.** — *Cardiovascular toxicology · 2026*
  - via `combo3:Adriamycin + doxorubicin + cardiotoxicity`
- `PMID:42624274` — **Ginkgolide B Mitigates Doxorubicin-Induced Cardiotoxicity by Regulating AMPK-Mediated Mitochondrial Fission via P-Drp1/OPA1 and Apoptosis.** — *Archives of biochemistry and biophysics · 2026*
  - via `combo3:Adriamycin + doxorubicin + cardiotoxicity`
- `PMID:42528395` — **Integrated Cantilever-MEA Platform for High-Sensitivity and Scalable Recording of Cardiomyocyte Electromechanics.** — *Small (Weinheim an der Bergstrasse, Germany) · 2026*
  - via `combo3:Cardiac strain + doxorubicin + cardiotoxicity`
- `PMID:42559407` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `combo3:Heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:42531631` — **Metal-dependent cell death in doxorubicin-induced cardiotoxicity and mitigation by luteolin: Network pharmacology and experimental verification.** — *Biomedicine & pharmacotherapy = Biomedecine & pharmacotherapie · 2026*
  - via `combo3:Heart muscle damage + doxorubicin + cardiotoxicity`
- `PMID:38510289` — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `combo3:GSTM1 + doxorubicin + cardiotoxicity`
- `PMID:41537578` — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:37828659` — **The Role of RARG rs2229774, SLC28A3 rs7853758, and UGT1A6*4 rs17863783 Single-nucleotide Polymorphisms in the Doxorubicin-induced Cardiotoxicity in Solid Childhood Tumors.** — *Journal of pediatric hematology/oncology · 2024*
  - via `combo3:SLC28A3 rs7853758 + doxorubicin + cardiotoxicity`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:26354850` — **GSTP1 and GSTO1 single nucleotide polymorphisms and the response of bladder cancer patients to intravesical chemotherapy.** — *Scientific reports · 2015*
  - via `combo2:GSTP1 rs1695 + doxorubicin`
- `PMID:38951505` — **Risk of anthracycline-induced cardiac dysfunction in adolescent and young adult (AYA) cancer survivors: role of genetic susceptibility loci.** — *The pharmacogenomics journal · 2024*
  - via `combo3:RARG rs2229774 + doxorubicin + cardiotoxicity`
- `PMID:32896271/PMC7478891` — **Direct reprogramming of human smooth muscle and vascular endothelial cells reveals defects associated with aging and Hutchinson-Gilford progeria syndrome.** — *eLife · 2020*
  - via `combo2:GSTM1 + heart muscle damage+pmc_xml`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** GSTM1  ·  **Evidence:** 14 refs, 6 papers, 2 full text

The adverse cardiac strain and heart muscle damage experienced by your daughter after taking Adriamycin (Doxorubicin) may be influenced by her GSTM1 genotype, although the evidence linking GSTM1 directly to these effects is not definitive. The likely biological mechanism involves increased susceptibility to Adriamycin-induced cardiotoxicity due to altered detoxification or cellular stress responses mediated by GST activity. For drug discovery and patient safety, pre-treatment biomarker screening for genetic variants like GSTM1 could help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or the use of alternative agents such as ID2-iNeu in combination therapy to mitigate these risks.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND pharmacogenomics` — 2 terms, 1 back-off(s), 1 hit(s)
- `GSTM1 AND heart damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND heart muscle damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GST AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND pharmacogenomics` — 2 terms, 1 back-off(s), 1 hit(s)
- `GSTM1/GSTP1 AND doxorubicin AND heart damage` — 2 terms, 1 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42636514` — **Targeting ID2 to augment doxorubicin antitumor efficacy and enhance antibacterial defense without neutropenia.** — *International immunopharmacology · 2026*
  - via `free2:doxorubicin AND cardiotoxicity`
- `PMID:41823204` — **Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute Lymphoblastic Leukemia and Lymphoma Undergoing Chemotherapy.** — *Pediatric blood & cancer · 2026*
  - via `free2:(GSTM1 OR GSTM1* OR GSTM1-null) AND doxorubicin`
- `PMID:42551595` — **Letter to the editor: Exploring the role of drug interactions in lithium-associated bradycardia: A network analysis of Vigibase.** — *Progress in neuro-psychopharmacology & biological psychiatry · 2026*
  - via `free2:cardiotoxicity AND pharmacogenomics`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `free2:doxorubicin AND SLC28A3`
- `PMID:42559407/PMC13440645` — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `free2:doxorubicin AND heart muscle damage+pmc_xml`
- `PMID:42515685/PMC13416366` — **Differential Effects of 17β-Estradiol, Its Metabolites, and Cadmium on Cytotoxicity and Redox-Related Pathways in Doxorubicin-Sensitive and -Resistant Breast Cancer Cell Lines.** — *Pharmaceuticals (Basel, Switzerland) · 2026*
  - via `free2:(GSTM1 OR GSTM1* OR GST) AND doxorubicin+pmc_xml`

</details>

### Phase 11 — evidence ledger

**Genes:** GSTM1  ·  **Evidence:** 14 refs, 6 papers, 1 full text

Adriamycin-induced cardiac strain and heart muscle damage are well-documented side effects with high confidence levels. The GSTM1 genetic variant is suggested as a potential risk factor, though the evidence is mixed (confidence 0.34). Studies indicate that cadmium exposure increases GST activity in breast cancer cells, which may be relevant to Adriamycin-induced oxidative stress and cardiotoxicity. However, direct evidence linking GSTM1 specifically to cardiac damage from Adriamycin is limited. Further genetic testing of your daughter could clarify her risk profile, potentially guiding personalized treatment strategies or dose adjustments.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND pharmacogenomics` — 2 terms, 1 back-off(s), 1 hit(s)
- `GSTM1 AND heart damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND SLC28A3` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND cardiotoxicity` — 2 terms, 0 back-off(s), 2 hit(s)
- `ABCB1 AND doxorubicin AND multiple myeloma` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND heart muscle damage` — 2 terms, 0 back-off(s), 2 hit(s)
- `GSTM1/GST AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `cardiotoxicity AND pharmacogenomics` — 2 terms, 1 back-off(s), 1 hit(s)
- `GSTM1/GSTP1 AND doxorubicin AND heart damage` — 2 terms, 1 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42643688` — **Borneol-based nanoparticles encapsulating Doxorubicin/Sodium tanshinone IIA sulfonate enhance the effect of anti-glioma and alleviate cardiotoxicity.** — *Cytotechnology · 2026*
  - via `free2:doxorubicin AND cardiotoxicity`
- `PMID:41823204` — **Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute Lymphoblastic Leukemia and Lymphoma Undergoing Chemotherapy.** — *Pediatric blood & cancer · 2026*
  - via `free2:(GSTM1 OR GSTM1* OR GSTM1-null) AND doxorubicin`
- `PMID:42551595` — **Letter to the editor: Exploring the role of drug interactions in lithium-associated bradycardia: A network analysis of Vigibase.** — *Progress in neuro-psychopharmacology & biological psychiatry · 2026*
  - via `free2:cardiotoxicity AND pharmacogenomics`
- `PMID:42246857` — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `free2:doxorubicin AND SLC28A3`
- `PMID:42639770` — **Therapeutic effect of Fuzheng Yixin decoction on cardiac insufficiencythe soluble guanylyl cyclase-cyclic guanosine monophosphate-protein kinase G pathway in a doxorubicin-induced dilated cardiomyopathy rat model.** — *Journal of traditional Chinese medicine = Chung i tsa chih ying wen pan · 2026*
  - via `free2:doxorubicin AND heart muscle damage`
- `PMID:42515685/PMC13416366` — **Differential Effects of 17β-Estradiol, Its Metabolites, and Cadmium on Cytotoxicity and Redox-Related Pathways in Doxorubicin-Sensitive and -Resistant Breast Cancer Cell Lines.** — *Pharmaceuticals (Basel, Switzerland) · 2026*
  - via `free2:(GSTM1 OR GSTM1* OR GST) AND doxorubicin+pmc_xml`

</details>

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

### Phase 3 — ClinPGx only

**Genes:** CYBA, ERCC1  ·  **Evidence:** 9 refs, 0 papers

Doxorubicin-induced mucositis is associated with genetic variants such as ERCC1 (rs11615) and CYBA (rs4673), which may modulate the drug's response, potentially increasing the risk of developing this adverse reaction. The biological mechanism likely involves impaired DNA repair or oxidative stress responses due to these genetic variations, leading to heightened mucositis susceptibility in treated individuals. For drug discovery and patient safety, pre-treatment screening for these variants could inform personalized dosing strategies or identify patients at higher risk who might benefit from prophylactic interventions or alternative therapies.

### Phase 4 — ClinPGx + cited PubMed

**Genes:** CYBA, ERCC1  ·  **Evidence:** 23 refs, 14 papers

Doxorubicin-induced mucositis is associated with genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing susceptibility to this adverse effect. The biological mechanism likely involves impaired DNA repair or oxidative stress responses due to these genetic variations, leading to heightened toxicity from doxorubicin. For drug discovery and patient safety, pre-treatment screening for these variants could inform personalized dosing strategies or identify patients at higher risk who might benefit from mucositis prophylaxis or alternative therapies.

<details><summary>Papers retrieved</summary>

- `PMID:21887680` — **Germline genetic polymorphisms may influence chemotherapy response and disease outcome in osteosarcoma: a pilot study.** — *Cancer · 2012*
  - via `clinpgx_citation`
- `PMID:29507678` — **Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients.** — *Oncotarget · 2018*
  - via `clinpgx_citation`
- `PMID:16330681` — **NAD(P)H oxidase and multidrug resistance protein genetic polymorphisms are associated with doxorubicin-induced cardiotoxicity.** — *Circulation · 2005*
  - via `clinpgx_citation`
- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:11418485` — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - via `clinpgx_citation`
- `PMID:11710708` — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:15936011` — **A beneficial effect of simvastatin on DNA damage in 242T allele of the NADPH oxidase p22phox in hypercholesterolemic patients.** — *Clinica chimica acta; international journal of clinical chemistry · 2005*
  - via `clinpgx_citation`
- `PMID:12411325` — **Polymorphism G80A in the reduced folate carrier gene and its relationship to methotrexate plasma levels and outcome of childhood acute lymphoblastic leukemia.** — *Blood · 2002*
  - via `clinpgx_citation`
- `PMID:12915598` — **Homocysteine, pharmacogenetics, and neurotoxicity in children with leukemia.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2003*
  - via `clinpgx_citation`
- `PMID:15805193` — **Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin.** — *Proceedings of the National Academy of Sciences of the United States of America · 2005*
  - via `clinpgx_citation`
- `PMID:16220110` — **CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population.** — *Pharmacogenetics and genomics · 2005*
  - via `clinpgx_citation`

</details>

### Phase 5 — + PMC full text

**Genes:** CYBA, ERCC1  ·  **Evidence:** 24 refs, 15 papers, 1 full text

Doxorubicin-induced mucositis is associated with genetic variants such as ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing susceptibility to this adverse effect. The biological mechanism likely involves these genes' roles in DNA repair and oxidative stress regulation, respectively, impacting cellular damage and recovery from doxorubicin exposure. For drug discovery and patient safety, pre-treatment genetic screening for these variants could help identify patients at higher risk of mucositis, allowing for dose adjustments or the use of alternative agents to mitigate this side effect.

<details><summary>Papers retrieved</summary>

- `PMID:21887680` — **Germline genetic polymorphisms may influence chemotherapy response and disease outcome in osteosarcoma: a pilot study.** — *Cancer · 2012*
  - via `clinpgx_citation`
- `PMID:29507678` — **Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients.** — *Oncotarget · 2018*
  - via `clinpgx_citation`
- `PMID:16330681` — **NAD(P)H oxidase and multidrug resistance protein genetic polymorphisms are associated with doxorubicin-induced cardiotoxicity.** — *Circulation · 2005*
  - via `clinpgx_citation`
- `PMID:21900104` — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - via `clinpgx_citation`
- `PMID:23441093` — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - via `clinpgx_citation`
- `PMID:11418485` — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - via `clinpgx_citation`
- `PMID:11710708` — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - via `clinpgx_citation`
- `PMID:18347182` — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - via `clinpgx_citation`
- `PMID:19361884` — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - via `clinpgx_citation`
- `PMID:15936011` — **A beneficial effect of simvastatin on DNA damage in 242T allele of the NADPH oxidase p22phox in hypercholesterolemic patients.** — *Clinica chimica acta; international journal of clinical chemistry · 2005*
  - via `clinpgx_citation`
- `PMID:12411325` — **Polymorphism G80A in the reduced folate carrier gene and its relationship to methotrexate plasma levels and outcome of childhood acute lymphoblastic leukemia.** — *Blood · 2002*
  - via `clinpgx_citation`
- `PMID:12915598` — **Homocysteine, pharmacogenetics, and neurotoxicity in children with leukemia.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2003*
  - via `clinpgx_citation`
- `PMID:15805193` — **Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin.** — *Proceedings of the National Academy of Sciences of the United States of America · 2005*
  - via `clinpgx_citation`
- `PMID:16220110` — **CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population.** — *Pharmacogenetics and genomics · 2005*
  - via `clinpgx_citation`
- `PMID:29507678/PMC5823653` — **Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients.** — *Oncotarget · 2018*
  - via `clinpgx_citation+pmc_xml`

</details>

### Phase 6 — open LLM search

**Genes:** CYBA, ERCC1  ·  **Evidence:** 20 refs, 14 papers

Doxorubicin-induced mucositis is influenced by genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing the risk of developing this adverse reaction. The biological mechanism likely involves these genes affecting DNA repair processes or oxidative stress responses, thereby altering cellular sensitivity to doxorubicin-induced damage. For drug discovery and patient safety, pre-treatment genetic screening for these variants could help identify patients at higher risk, allowing for dose adjustments or consideration of alternative agents with a lower mucositis risk profile.

<details><summary>Papers retrieved</summary>

- `PMID:41782384` — **Piezo1 Channel Mediates Mechanically Programmable Drug Delivery to Potentiate Intravesical Chemotherapy.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:40243204` — **Tritrichomonas muris sensitizes the intestinal epithelium to doxorubicin-induced apoptosis.** — *American journal of physiology. Gastrointestinal and liver physiology · 2025*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635616` — **When Surgical Intervention Becomes a Risk: Severe Drug-Induced Gingival Overgrowth and Clinical Decision-Making in Alpers-Huttenlocher Syndrome.** — *Special care in dentistry : official publication of the American Association of Hospital Dentists, the Academy of Dentistry for the Handicapped, and the American Society for Geriatric Dentistry · 2026*
  - via `llm_topic:mucositis`
- `PMID:42635600` — **BRD4 contributes to the cytokine-induced acquisition of an IL-13RA2-positive inflammatory fibroblast phenotype.** — *Journal of Crohn's & colitis · 2026*
  - via `llm_topic:mucositis`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42548792` — **Pharmacogenomic variation and chemotherapy-related toxicity profiles in pediatric patients with cancer in Tanzania: a cross-sectional study.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:CYBA rs4673`
- `PMID:39960941` — **Association between rs4673 and blood pressure response to acute saline infusion in Chinese population.** — *Medicine · 2025*
  - via `llm_topic:CYBA rs4673`
- `PMID:42635220` — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42614547` — **Shared genetic architecture between Crohn's disease and IgA nephropathy: implications for a gut-immune-kidney axis.** — *Frontiers in immunology · 2026*
  - via `llm_topic:genetic predisposition mucositis`
- `PMID:42579038` — **Influenza A(H1N1) triggered atypical hemolytic uremic syndrome in a child with homozygous CD46 variant successfully treated with ravulizumab: a case report.** — *CEN case reports · 2026*
  - via `llm_topic:genetic predisposition mucositis`

</details>

### Phase 7 — open search + full text

**Genes:** CYBA, ERCC1  ·  **Evidence:** 20 refs, 14 papers, 1 full text

Doxorubicin-induced mucositis is influenced by genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response. These variants likely affect DNA repair mechanisms or oxidative stress responses, thereby increasing susceptibility to mucosal damage from doxorubicin. For patient safety, pre-treatment screening for these genetic markers could help identify individuals at higher risk of developing mucositis, allowing for dose adjustments or alternative chemotherapy agents to be considered.

<details><summary>Papers retrieved</summary>

- `PMID:41782384` — **Piezo1 Channel Mediates Mechanically Programmable Drug Delivery to Potentiate Intravesical Chemotherapy.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:40243204` — **Tritrichomonas muris sensitizes the intestinal epithelium to doxorubicin-induced apoptosis.** — *American journal of physiology. Gastrointestinal and liver physiology · 2025*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:42634559` — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635616` — **When Surgical Intervention Becomes a Risk: Severe Drug-Induced Gingival Overgrowth and Clinical Decision-Making in Alpers-Huttenlocher Syndrome.** — *Special care in dentistry : official publication of the American Association of Hospital Dentists, the Academy of Dentistry for the Handicapped, and the American Society for Geriatric Dentistry · 2026*
  - via `llm_topic:mucositis`
- `PMID:42635600` — **BRD4 contributes to the cytokine-induced acquisition of an IL-13RA2-positive inflammatory fibroblast phenotype.** — *Journal of Crohn's & colitis · 2026*
  - via `llm_topic:mucositis`
- `PMID:42123691` — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42548792` — **Pharmacogenomic variation and chemotherapy-related toxicity profiles in pediatric patients with cancer in Tanzania: a cross-sectional study.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:CYBA rs4673`
- `PMID:39960941` — **Association between rs4673 and blood pressure response to acute saline infusion in Chinese population.** — *Medicine · 2025*
  - via `llm_topic:CYBA rs4673`
- `PMID:42635220` — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42614547/PMC13481795` — **Shared genetic architecture between Crohn's disease and IgA nephropathy: implications for a gut-immune-kidney axis.** — *Frontiers in immunology · 2026*
  - via `llm_topic:genetic predisposition mucositis+pmc_xml`
- `PMID:42579038` — **Influenza A(H1N1) triggered atypical hemolytic uremic syndrome in a child with homozygous CD46 variant successfully treated with ravulizumab: a case report.** — *CEN case reports · 2026*
  - via `llm_topic:genetic predisposition mucositis`

</details>

### Phase 8 — combined-topic search

**Genes:** CYBA, ERCC1  ·  **Evidence:** 21 refs, 11 papers

Doxorubicin-induced mucositis is associated with genetic polymorphisms in ERCC1 (rs11615) and CYBA (rs4673). These variants likely influence the biological mechanism by modulating DNA repair efficiency and oxidative stress response, respectively. For drug discovery and patient safety, pre-treatment screening for these risk factors could enable personalized dosing strategies or identification of patients at higher risk who might benefit from mucositis prophylaxis or alternative agents.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND CYBA` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND mucositis` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYBA AND mucositis` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 2 terms, 0 back-off(s), 2 hit(s)
- `mucositis AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 rs11615 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `CYBA rs4673 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `chemotherapy-induced neutropenia CIN AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `febrile neutropenia FN AND doxorubicin AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `anemia AND doxorubicin AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracyclines AND doxorubicin AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND rs11615` — 2 terms, 0 back-off(s), 2 hit(s)
- `mucositis AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYBA AND doxorubicin AND rs4673` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:40859847` — **Development of a predictive model for neutropenia risk in Japanese breast cancer patients treated with doxorubicin and cyclophosphamide.** — *British journal of clinical pharmacology · 2026*
  - via `combo2:doxorubicin + ERCC1`
- `PMID:40362292` — **Drugs Metabolism-Related Genes Variants Impact on Anthracycline-Based Chemotherapy Induced Subclinical Cardiotoxicity in Breast Cancer Patients.** — *International journal of molecular sciences · 2025*
  - via `combo2:doxorubicin + CYBA`
- `PMID:33160994` — **Reserpine inhibits DNA repair, cell proliferation, invasion and induces apoptosis in oral carcinogenesis via modulation of TGF-β signaling.** — *Life sciences · 2021*
  - via `combo2:ERCC1 + mucositis`
- `PMID:42623591` — **Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Invasive Bladder Cancer: Real-World Feasibility and Safety in a Resource-Constrained Setting.** — *JCO global oncology · 2026*
  - via `combo2:doxorubicin + mucositis`
- `PMID:42622897` — **Feasibility and safety of accelerated MVAC (aMVAC) in geriatric patients with muscle-invasive bladder cancer.** — *Medical oncology (Northwood, London, England) · 2026*
  - via `combo2:doxorubicin + mucositis`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:ERCC1 rs11615 + doxorubicin`
- `PMID:39774928` — **The association between NADPH oxidase (NOX) polymorphisms with immunohistochemistry and survival in diffuse large B cell lymphoma patients.** — *Annals of hematology · 2025*
  - via `combo2:CYBA rs4673 + doxorubicin`
- `PMID:25168315` — **Impact of genetic variability and treatment-related factors on outcome in early breast cancer patients receiving (neo-) adjuvant chemotherapy with 5-fluorouracil, epirubicin and cyclophosphamide, and docetaxel.** — *Breast cancer research and treatment · 2014*
  - via `combo2:CYBA rs4673 + doxorubicin`
- `PMID:42342254` — **Chemotherapy-Induced Neutropenia in Palestinian Patients with Solid Malignancies: Patient Characteristics, Severity Risk Factors, and Management Patterns.** — *Cancer research communications · 2026*
  - via `combo2:chemotherapy-induced neutropenia CIN + doxorubicin`
- `PMID:30235921` — **A Phase II Study to Evaluate the Safety and Efficacy of Pegteograstim in Korean Breast Cancer Patients Receiving Dose-Dense Doxorubicin/Cyclophosphamide.** — *Cancer research and treatment · 2019*
  - via `combo3:febrile neutropenia FN + doxorubicin + mucositis`
- `PMID:21824038` — **TAXTOX - a retrospective study regarding the side effects of docetaxel given as part of the adjuvant treatment to patients with primary breast cancer in Denmark from 2007 to 2009.** — *Acta oncologica (Stockholm, Sweden) · 2011*
  - via `combo3:febrile neutropenia FN + doxorubicin + mucositis`

</details>

### Phase 9 — combined + full text

**Genes:** CYBA, ERCC1  ·  **Evidence:** 22 refs, 11 papers

Doxorubicin-induced mucositis is associated with genetic polymorphisms in ERCC1 (rs11615) and CYBA (rs4673). These variants likely influence the biological mechanism by modulating DNA repair efficiency and oxidative stress response, respectively. For drug discovery and patient safety, pre-treatment screening for these risk factors could enable personalized dosing strategies or identification of patients at higher risk who might benefit from mucositis prophylaxis or alternative agents.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND CYBA` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 AND mucositis` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYBA AND mucositis` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 2 terms, 0 back-off(s), 2 hit(s)
- `mucositis AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `ERCC1 rs11615 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `CYBA rs4673 AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `chemotherapy-induced neutropenia CIN AND doxorubicin` — 2 terms, 1 back-off(s), 2 hit(s)
- `febrile neutropenia FN AND doxorubicin AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `anemia AND doxorubicin AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `anthracyclines AND doxorubicin AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND rs11615` — 2 terms, 0 back-off(s), 2 hit(s)
- `mucositis AND ERCC1` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYBA AND doxorubicin AND rs4673` — 3 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:40859847` — **Development of a predictive model for neutropenia risk in Japanese breast cancer patients treated with doxorubicin and cyclophosphamide.** — *British journal of clinical pharmacology · 2026*
  - via `combo2:doxorubicin + ERCC1`
- `PMID:40362292` — **Drugs Metabolism-Related Genes Variants Impact on Anthracycline-Based Chemotherapy Induced Subclinical Cardiotoxicity in Breast Cancer Patients.** — *International journal of molecular sciences · 2025*
  - via `combo2:doxorubicin + CYBA`
- `PMID:33160994` — **Reserpine inhibits DNA repair, cell proliferation, invasion and induces apoptosis in oral carcinogenesis via modulation of TGF-β signaling.** — *Life sciences · 2021*
  - via `combo2:ERCC1 + mucositis`
- `PMID:42623591` — **Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Invasive Bladder Cancer: Real-World Feasibility and Safety in a Resource-Constrained Setting.** — *JCO global oncology · 2026*
  - via `combo2:doxorubicin + mucositis`
- `PMID:42622897` — **Feasibility and safety of accelerated MVAC (aMVAC) in geriatric patients with muscle-invasive bladder cancer.** — *Medical oncology (Northwood, London, England) · 2026*
  - via `combo2:doxorubicin + mucositis`
- `PMID:34149004` — **Pharmacogenetic study in gastric cancer patients treated with adjuvant fluorouracil/leucovorin or epirubicin/cisplatin/fluorouracil before and after chemoradiation on CALGB 80101 (Alliance).** — *Pharmacogenetics and genomics · 2021*
  - via `combo2:ERCC1 rs11615 + doxorubicin`
- `PMID:39774928` — **The association between NADPH oxidase (NOX) polymorphisms with immunohistochemistry and survival in diffuse large B cell lymphoma patients.** — *Annals of hematology · 2025*
  - via `combo2:CYBA rs4673 + doxorubicin`
- `PMID:25168315` — **Impact of genetic variability and treatment-related factors on outcome in early breast cancer patients receiving (neo-) adjuvant chemotherapy with 5-fluorouracil, epirubicin and cyclophosphamide, and docetaxel.** — *Breast cancer research and treatment · 2014*
  - via `combo2:CYBA rs4673 + doxorubicin`
- `PMID:42342254` — **Chemotherapy-Induced Neutropenia in Palestinian Patients with Solid Malignancies: Patient Characteristics, Severity Risk Factors, and Management Patterns.** — *Cancer research communications · 2026*
  - via `combo2:chemotherapy-induced neutropenia CIN + doxorubicin`
- `PMID:30235921` — **A Phase II Study to Evaluate the Safety and Efficacy of Pegteograstim in Korean Breast Cancer Patients Receiving Dose-Dense Doxorubicin/Cyclophosphamide.** — *Cancer research and treatment · 2019*
  - via `combo3:febrile neutropenia FN + doxorubicin + mucositis`
- `PMID:21824038` — **TAXTOX - a retrospective study regarding the side effects of docetaxel given as part of the adjuvant treatment to patients with primary breast cancer in Denmark from 2007 to 2009.** — *Acta oncologica (Stockholm, Sweden) · 2011*
  - via `combo3:febrile neutropenia FN + doxorubicin + mucositis`

</details>

### Phase 10 — free arity + own phrasing

**Genes:** CYBA, ERCC1, RS11615, RS4673  ·  **Evidence:** 13 refs, 4 papers

Doxorubicin-induced mucositis is associated with genetic variants ERCC1 (rs11615) and CYBA (rs4673), which are linked to an increased risk of developing mucositis according to PharmGKB evidence level 3. The biological mechanism likely involves altered drug metabolism or response, as these polymorphisms may affect DNA repair processes (ERCC1) and oxidative stress responses (CYBA). For patient safety and personalized treatment strategies, pre-treatment genetic screening for these variants could help identify patients at higher risk of mucositis, allowing for dose adjustments or the use of alternative agents to mitigate adverse effects.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/rs11615 AND doxorubicin AND mucositis` — 2 terms, 1 back-off(s), 2 hit(s)
- `CYBA/rs4673 AND doxorubicin AND mucositis` — 2 terms, 1 back-off(s), 2 hit(s)
- `genetic predisposition to mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/rs11615 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYBA/rs4673 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition to mucositis` — 1 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42623591` — **Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Invasive Bladder Cancer: Real-World Feasibility and Safety in a Resource-Constrained Setting.** — *JCO global oncology · 2026*
  - via `free2:doxorubicin mucositis`
- `PMID:40859847` — **Development of a predictive model for neutropenia risk in Japanese breast cancer patients treated with doxorubicin and cyclophosphamide.** — *British journal of clinical pharmacology · 2026*
  - via `free3:(ERCC1 OR rs11615) AND doxorubicin`
- `PMID:40362292` — **Drugs Metabolism-Related Genes Variants Impact on Anthracycline-Based Chemotherapy Induced Subclinical Cardiotoxicity in Breast Cancer Patients.** — *International journal of molecular sciences · 2025*
  - via `free3:(CYBA OR rs4673) AND doxorubicin`
- `PMID:42624930` — **Pharmacological inhibition of CDK7 and CDK9 suppresses gastrointestinal (colon) cancer progression through modulation of stemness, epithelial-mesenchymal transition, and chemoresistance.** — *Naunyn-Schmiedeberg's archives of pharmacology · 2026*
  - via `free2:(SLC28A3 OR ABCB1) AND doxorubicin`

</details>

### Phase 11 — evidence ledger

**Genes:** CYBA, ERCC1  ·  **Evidence:** 13 refs, 4 papers

Doxorubicin is known to cause mucositis as a side effect. Genetic variants such as ERCC1 (rs11615) and CYBA (rs4673) are associated with an increased risk of doxorubicin-related adverse effects, including mucositis. The PharmGKB evidence level 3 for ERCC1 (rs11615) indicates that individuals carrying this genetic variant may have a predisposition to developing mucositis when treated with doxorubicin. This suggests that there is a genetic component influencing the risk of mucositis in patients receiving doxorubicin therapy. For drug discovery and patient safety, screening for these genetic variants could help identify high-risk patients who might benefit from dose adjustment or alternative agents.

<details><summary>Queries issued (combined terms)</summary>

- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/rs11615 AND doxorubicin AND mucositis` — 2 terms, 1 back-off(s), 2 hit(s)
- `CYBA/rs4673 AND doxorubicin AND mucositis` — 2 terms, 1 back-off(s), 2 hit(s)
- `genetic predisposition to mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `SLC28A3/ABCB1 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND genetic variation AND mucositis` — 3 terms, 0 back-off(s), 2 hit(s)
- `doxorubicin AND mucositis` — 1 terms, 0 back-off(s), 2 hit(s)
- `ERCC1/rs11615 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `CYBA/rs4673 AND doxorubicin` — 2 terms, 0 back-off(s), 2 hit(s)
- `genetic predisposition to mucositis` — 1 terms, 0 back-off(s), 2 hit(s)

</details>

<details><summary>Papers retrieved</summary>

- `PMID:42623591` — **Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Invasive Bladder Cancer: Real-World Feasibility and Safety in a Resource-Constrained Setting.** — *JCO global oncology · 2026*
  - via `free2:doxorubicin mucositis`
- `PMID:40859847` — **Development of a predictive model for neutropenia risk in Japanese breast cancer patients treated with doxorubicin and cyclophosphamide.** — *British journal of clinical pharmacology · 2026*
  - via `free3:(ERCC1 OR rs11615) AND doxorubicin`
- `PMID:40362292` — **Drugs Metabolism-Related Genes Variants Impact on Anthracycline-Based Chemotherapy Induced Subclinical Cardiotoxicity in Breast Cancer Patients.** — *International journal of molecular sciences · 2025*
  - via `free3:(CYBA OR rs4673) AND doxorubicin`
- `PMID:42624930` — **Pharmacological inhibition of CDK7 and CDK9 suppresses gastrointestinal (colon) cancer progression through modulation of stemness, epithelial-mesenchymal transition, and chemoresistance.** — *Naunyn-Schmiedeberg's archives of pharmacology · 2026*
  - via `free2:(SLC28A3 OR ABCB1) AND doxorubicin`

</details>

---

## Caveats

- **n = 10, no gold answers.** Descriptive measurements, not significance tests.
- **ClinPGx-valid % is partly circular** for phases 3–9: they retrieve from ClinPGx and are then scored against it. Fair for baselines A/B and fair *between* grounded phases.
- **Baselines A/B and phase 3-old predate provenance logging** (no grounding column) and cover 9 questions rather than 10.
- **On-topic % is a keyword proxy** — a relevant paper that never repeats the drug name in its abstract scores as off-topic, so treat it as a lower bound.
