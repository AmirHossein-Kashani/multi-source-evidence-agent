# Phases 8 & 9 — combined-topic search over graph relations

Phases 6/7 searched **one topic at a time**, so a bare entity (`tinnitus`, `cancer`) could drift far off topic. Phases 8/9 search **relationships**: entities that are related in the knowledge graph are combined into a single conjunctive PubMed query (`cisplatin AND ACYP2 AND hearing loss`), so the hit is a paper about the *link*.

The LLM sees the knowledge-graph edges and decides **how many terms** go in each query (the *arity*). A query returning nothing is **backed off** by dropping its last term and retried, down to 2 terms. Every issued query is recorded in `search_shape`.

| Phase | Configuration | Retrieval |
|---|---|---|
| **Phase 8** | `AMG_KB_SOURCE=pharmgkb+pubmed_combo` | combined-topic queries — abstracts |
| **Phase 9** | `+ AMG_PUBMED_FULLTEXT=1` | combined-topic queries — full paper via PMC |

## Search shape — Phase 8

**160 queries issued** across 10 questions (16.0 per question).

### How many terms were searched together

| Terms per query | Requested by LLM | Actually searched | Hit rate | Papers found |
|---|---|---|---|---|
| **2-term** | 85 (53%) `███████████` | 104 | 88% | 176 |
| **3-term** | 75 (47%) `█████████` | 56 | 100% | 107 |

- **Back-offs:** 19 of 160 queries were over-constrained and had to drop terms (19 terms dropped in total).
- **Empty after back-off:** 12 queries (8%).
- **Mean arity:** requested 2.47, searched 2.35.

| Stage | Queries | Mean terms | Hit rate |
|---|---|---|---|
| `entity` | 80 | 2.55 | 92% |
| `question_context` | 40 | 2.12 | 90% |
| `reasoning` | 40 | 2.17 | 95% |

## Search shape — Phase 9

**159 queries issued** across 10 questions (15.9 per question).

### How many terms were searched together

| Terms per query | Requested by LLM | Actually searched | Hit rate | Papers found |
|---|---|---|---|---|
| **2-term** | 80 (50%) `██████████` | 98 | 90% | 169 |
| **3-term** | 79 (50%) `██████████` | 61 | 100% | 117 |

- **Back-offs:** 18 of 159 queries were over-constrained and had to drop terms (18 terms dropped in total).
- **Empty after back-off:** 10 queries (6%).
- **Mean arity:** requested 2.50, searched 2.38.

| Stage | Queries | Mean terms | Hit rate |
|---|---|---|---|
| `entity` | 80 | 2.56 | 92% |
| `question_context` | 39 | 2.15 | 92% |
| `reasoning` | 40 | 2.25 | 98% |

## Did combining topics improve precision?

On-topic % = share of retrieved papers whose title+abstract mention **both** the question's drug **and** its adverse effect (same metric as `adr_phase_evaluation.md`).

| Phase | Search shape | Papers | On-topic % |
|---|---|---|---|
| Phase 6 | one topic per query | 177 | 20% |
| Phase 7 | one topic per query | 186 | 23% |
| Phase 8 | **combined** topics per query | 135 | 53% |
| Phase 9 | **combined** topics per query | 140 | 54% |

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** GSTM1, TPMT

The development of hearing loss and tinnitus in a child receiving cisplatin for cancer treatment implicates genetic variants such as GSTM1 non-null, which is associated with reduced detoxification capacity leading to increased ototoxicity risk. TPMT*1 has also been linked to this adverse effect but with less consistent evidence. The biological mechanism involves impaired metabolism and detoxification of cisplatin's reactive metabolites, causing oxidative stress and cellular damage in the auditory system. For drug discovery and patient safety, genetic screening for GSTM1 status could inform personalized dosing strategies or alternative agents with lower ototoxic potential to mitigate these risks.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `GSTM1 AND cisplatin` | 0 | 2 |
| 2 | `TPMT AND ototoxicity` | 0 | 2 |
| 2 | `COMT AND drug toxicity` | 0 | 2 |
| 2 | `cisplatin AND hearing loss` | 0 | 2 |
| 3 | `cancer AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `hearing loss AND cisplatin` | 0 | 2 |
| 3 | `tinnitus AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `GSTM1 non-null AND cisplatin` | 1 | 0 |
| 2 | `TPMT*1 AND cisplatin` | 1 | 0 |
| 3 | `rs4646316 AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `Gadd45a AND cisplatin AND hearing loss` | 0 | 1 |
| 2 | `cisplatin AND GSTM1` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 2 | `GSTM1 AND ototoxicity` | 0 | 2 |
| 2 | `TPMT AND ototoxicity` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** ACYP2, GSTM1, TPMT

Cisplatin-induced ototoxicity, leading to hearing loss and tinnitus, is associated with genetic variants in ACYP2 (rs1872328), GSTM1, and TPMT. These variants likely influence the metabolism or cellular uptake of cisplatin, affecting its toxicity profile within auditory tissues. For drug discovery and patient safety, pre-treatment screening for these risk variants could enable personalized dosing strategies to mitigate ototoxicity risks in pediatric patients receiving cisplatin.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND ACYP2` | 0 | 2 |
| 3 | `cisplatin AND GSTM1 AND ototoxicity` | 0 | 2 |
| 2 | `TPMT AND ototoxicity` | 0 | 2 |
| 3 | `hearing_loss AND tinnitus AND pharmacogenomics` | 0 | 2 |
| 2 | `cisplatin AND hearing loss` | 0 | 2 |
| 3 | `cancer AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `hearing loss AND cisplatin` | 0 | 2 |
| 3 | `tinnitus AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `ototoxicity AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `ACYP2 rs1872328 AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `GSTM1 GSTM1 non-null AND cisplatin` | 1 | 0 |
| 2 | `TPMT TPMT*1 AND cisplatin` | 1 | 0 |
| 2 | `cisplatin AND ACYP2` | 0 | 2 |
| 2 | `GSTM1 AND ototoxicity` | 0 | 2 |
| 2 | `TPMT AND cisplatin` | 0 | 2 |
| 3 | `COMT AND rs4646316 AND hearing loss` | 0 | 2 |

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

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** GSTM1

GSTM1 non-null is the primary genetic variant linked to cisplatin-induced ototoxicity in pediatric cancer patients, with moderate evidence (PharmGKB Level 3). The biological mechanism likely involves impaired glutathione metabolism, as GSTM1 encodes a protein involved in detoxifying reactive metabolites of cisplatin. This impairment may lead to increased cellular damage and subsequent hearing loss. For drug discovery and patient safety, pre-treatment screening for the GSTM1 non-null variant could help identify patients at higher risk of ototoxicity, potentially allowing dose adjustments or consideration of alternative agents such as carboplatin.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND GSTM1` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 3 | `cisplatin AND COMT AND rs4646316` | 0 | 2 |
| 2 | `ototoxicity AND children` | 0 | 2 |
| 2 | `cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `ototoxicity AND cisplatin` | 0 | 2 |
| 3 | `pediatric cancer patients AND cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `GSTM1 GSTM1 non-null AND cisplatin` | 1 | 0 |
| 2 | `TPMT TPMT*1 AND cisplatin` | 1 | 0 |
| 3 | `COMT rs4646316 AND cisplatin AND ototoxicity` | 0 | 2 |
| 3 | `GSTT1 AND cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `ROS-triggered ferroptosis AND cisplatin` | 1 | 2 |
| 2 | `cisplatin AND GSTM1` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 3 | `GSTM1 AND ototoxicity AND children` | 0 | 2 |
| 3 | `cisplatin AND COMT AND rs4646316` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** GSTM1, TPMT

GSTM1 non-null is the primary genetic variant associated with increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, although evidence linking TPMT variants to this adverse effect is also present but less reliable. The biological mechanism likely involves GSTM1's role in glutathione metabolism, which may influence the detoxification and cellular damage caused by cisplatin. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could help identify patients at higher risk of ototoxicity, potentially guiding dose adjustments or alternative therapeutic strategies to mitigate this side effect.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND GSTM1` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 3 | `cisplatin AND COMT AND rs4646316` | 0 | 2 |
| 2 | `ototoxicity AND children` | 0 | 2 |
| 2 | `cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `ototoxicity AND cisplatin` | 0 | 2 |
| 3 | `pediatric cancer patients AND cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `GSTM1 GSTM1 non-null AND cisplatin` | 1 | 0 |
| 2 | `TPMT TPMT*1 AND cisplatin` | 1 | 0 |
| 3 | `COMT rs4646316 AND cisplatin AND ototoxicity` | 0 | 2 |
| 3 | `GSTT1 AND cisplatin AND ototoxicity` | 0 | 2 |
| 2 | `ROS-triggered ferroptosis AND cisplatin` | 1 | 2 |
| 2 | `cisplatin AND GSTM1` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 3 | `GSTM1 AND ototoxicity AND children` | 0 | 2 |
| 3 | `cisplatin AND COMT AND rs4646316` | 0 | 2 |

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

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** TPMT

The TPMT variant is implicated in the increased risk of ototoxicity when a patient undergoes cisplatin treatment for Neuroblastoma. The reduced activity of the TPMT enzyme due to genetic variation leads to higher levels of toxic metabolites, which can damage auditory hair cells and cause hearing loss. For drug discovery and patient safety, pre-treatment biomarker screening for TPMT variants should be considered to identify patients at high risk of ototoxicity. Dose adjustment or alternative agents with lower ototoxic potential may also need to be explored.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 3 | `TPMT AND cisplatin AND ototoxicity` | 0 | 2 |
| 3 | `GSTM1 AND ototoxicity AND children` | 0 | 2 |
| 3 | `cisplatin AND neuroblastoma AND hearing loss` | 0 | 2 |
| 2 | `COMT AND drug toxicity` | 0 | 2 |
| 3 | `TPMT variant AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `cisplatin AND hearing loss` | 0 | 2 |
| 3 | `Neuroblastoma AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `hearing loss AND cisplatin` | 0 | 2 |
| 2 | `GSTM1 non-null AND cisplatin` | 1 | 0 |
| 3 | `COMT rs4646316 AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `ototoxicity AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `Deafness AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 2 | `GSTM1 AND ototoxicity` | 0 | 2 |
| 3 | `cisplatin AND hearing loss AND children` | 0 | 2 |
| 2 | `TPMT*1 AND neuroblastoma` | 0 | 0 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** TPMT, ACYP2, GSTM1

The TPMT variant is a key genetic factor implicated in the increased risk of cisplatin-induced hearing loss. The TPMT enzyme's reduced function due to the variant can lead to higher levels of toxic metabolites that may exacerbate ototoxicity. Additionally, other genetic factors such as ACYP2 and GSTM1 further modulate this response. For drug discovery and patient safety, pre-treatment biomarker screening for these variants is crucial to identify patients at high risk. Dose adjustment or alternative agents with lower ototoxic potential should be considered in TPMT variant carriers.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 2 | `ACYP2 AND hearing loss` | 0 | 2 |
| 2 | `GSTM1 AND ototoxicity` | 0 | 2 |
| 3 | `cisplatin AND neuroblastoma AND ototoxicity` | 0 | 2 |
| 3 | `TPMT variant AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `cisplatin AND hearing loss` | 0 | 2 |
| 3 | `Neuroblastoma AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `Hearing loss AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `Audiologist AND cisplatin AND hearing loss` | 0 | 2 |
| 3 | `ACYP2 rs1872328 AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `GSTM1 GSTM1 non-null AND cisplatin` | 1 | 0 |
| 3 | `Ototoxicity AND cisplatin AND hearing loss` | 0 | 2 |
| 2 | `cisplatin AND TPMT` | 0 | 2 |
| 2 | `TPMT AND ototoxicity` | 0 | 2 |
| 3 | `GSTM1 AND cisplatin AND ototoxicity` | 0 | 2 |
| 3 | `cisplatin AND neuroblastoma AND hearing loss` | 0 | 2 |

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

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** GSTT1

The permanent inner ear damage observed after Platinol treatment may be influenced by the child's GSTT1 status. The glutathione S-transferase theta 1 (GSTT1) gene is involved in detoxifying reactive metabolites of drugs, including cisplatin. Variants or deletions in this gene can impair the body's ability to mitigate ototoxicity caused by Platinol, potentially increasing susceptibility to inner ear damage. For drug discovery and patient safety, pre-treatment genetic screening for GSTT1 status could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or consideration of alternative agents such as carboplatin.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `Platinol AND GSTT1` | 0 | 2 |
| 2 | `GSTT1 AND ototoxicity` | 0 | 2 |
| 3 | `Platinol AND ototoxicity AND children` | 0 | 2 |
| 2 | `cisplatin AND GSTT1` | 0 | 2 |
| 2 | `Platinol AND cisplatin` | 0 | 2 |
| 2 | `GSTT1 status AND cisplatin` | 0 | 1 |
| 2 | `inner ear damage AND cisplatin` | 0 | 2 |
| 2 | `cisplatin-related Ovarian Neoplasms AND cisplatin` | 0 | 2 |
| 2 | `ERCC1 rs11615 AND cisplatin` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND cisplatin` | 0 | 2 |
| 2 | `GSTM3 rs1799735 AND cisplatin` | 0 | 1 |
| 2 | `CDDP AND cisplatin` | 0 | 2 |
| 2 | `cisplatin AND GSTT1` | 0 | 2 |
| 2 | `GSTT1 AND inner ear damage` | 1 | 1 |
| 3 | `cisplatin AND ototoxicity AND pharmacogenomics` | 0 | 2 |
| 2 | `GSTM3 AND hearing loss` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** GSTT1

The permanent inner ear damage observed after Platinol treatment may be influenced by the child's GSTT1 status. The glutathione S-transferase theta 1 (GSTT1) enzyme plays a role in detoxifying cisplatin through conjugation with glutathione, and genetic variability affecting its expression or function could increase susceptibility to ototoxicity. For drug discovery and patient safety, pre-treatment screening for GSTT1 status should be considered to identify patients at higher risk of adverse effects. This information can guide dose adjustments or the selection of alternative agents to mitigate ototoxic risks.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `Platinol AND GSTT1` | 0 | 2 |
| 2 | `GSTT1 AND ototoxicity` | 0 | 2 |
| 3 | `Platinol AND ototoxicity AND children` | 0 | 2 |
| 2 | `cisplatin AND GSTT1` | 0 | 2 |
| 2 | `Platinol AND cisplatin` | 0 | 2 |
| 2 | `GSTT1 status AND cisplatin` | 0 | 1 |
| 2 | `inner ear damage AND cisplatin` | 0 | 2 |
| 2 | `cisplatin-related Ovarian Neoplasms AND cisplatin` | 0 | 2 |
| 2 | `ERCC1 rs11615 AND cisplatin` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND cisplatin` | 0 | 2 |
| 2 | `GSTM3 rs1799735 AND cisplatin` | 0 | 1 |
| 2 | `CDDP AND cisplatin` | 0 | 2 |
| 2 | `cisplatin AND GSTT1` | 0 | 2 |
| 2 | `GSTT1 AND inner ear damage` | 1 | 1 |
| 3 | `cisplatin AND ototoxicity AND pharmacogenomics` | 0 | 2 |
| 2 | `GSTM3 AND hearing loss` | 0 | 2 |

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

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** ERCC1, GSTP1, GSTM3

Cisplatin-induced peripheral neuropathy is associated with genetic variants such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3. These genes are involved in DNA repair mechanisms and detoxification pathways, which can influence cellular sensitivity to cisplatin's cytotoxic effects. While the relationship between these genetic markers and increased susceptibility to peripheral neuropathy is not definitively established, pre-treatment biomarker screening could help identify patients at higher risk for this adverse reaction, potentially guiding dose adjustments or alternative therapeutic strategies.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND ERCC1` | 0 | 2 |
| 2 | `cisplatin AND GSTP1` | 0 | 2 |
| 2 | `cisplatin AND GSTM3` | 0 | 2 |
| 2 | `peripheral neuropathy AND pharmacogenomics` | 0 | 2 |
| 2 | `cisplatin AND neuropathy` | 0 | 2 |
| 3 | `peripheral neuropathy AND cisplatin AND neuropathy` | 0 | 2 |
| 2 | `ERCC1 rs11615 AND cisplatin` | 1 | 2 |
| 2 | `GSTP1 rs1695 AND cisplatin` | 1 | 2 |
| 2 | `GSTM3 rs1799735 AND cisplatin` | 1 | 1 |
| 3 | `Ovarian Neoplasms AND cisplatin AND neuropathy` | 0 | 2 |
| 3 | `Hepatocellular Carcinoma HCC AND cisplatin AND neuropathy` | 0 | 1 |
| 2 | `Mitochondrial Permeability Transition Pores mPTP AND cisplatin` | 1 | 1 |
| 2 | `cisplatin AND ERCC1` | 0 | 2 |
| 2 | `ERCC1 AND rs11615` | 0 | 2 |
| 2 | `cisplatin AND peripheral neuropathy` | 0 | 2 |
| 2 | `GSTP1 AND rs1695` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** ERCC1, GSTP1

Cisplatin-induced peripheral neuropathy is associated with genetic variants such as ERCC1 (rs11615) and GSTP1 (rs1695). These genes are involved in DNA repair mechanisms and glutathione metabolism, respectively. Individuals carrying these variants may have an increased susceptibility to developing peripheral neuropathy due to impaired cellular defense against cisplatin's toxic effects on nerve cells. For drug discovery and patient safety, pre-treatment genetic screening for these risk factors could help identify patients at higher risk of adverse reactions, allowing for dose adjustments or the use of alternative agents.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `cisplatin AND ERCC1` | 0 | 2 |
| 2 | `cisplatin AND GSTP1` | 0 | 2 |
| 2 | `cisplatin AND GSTM3` | 0 | 2 |
| 2 | `peripheral neuropathy AND pharmacogenomics` | 0 | 2 |
| 2 | `cisplatin AND neuropathy` | 0 | 2 |
| 3 | `peripheral neuropathy AND cisplatin AND neuropathy` | 0 | 2 |
| 2 | `ERCC1 rs11615 AND cisplatin` | 1 | 2 |
| 2 | `GSTP1 rs1695 AND cisplatin` | 1 | 2 |
| 2 | `GSTM3 rs1799735 AND cisplatin` | 1 | 1 |
| 3 | `Ovarian Neoplasms AND cisplatin AND neuropathy` | 0 | 2 |
| 3 | `Hepatocellular Carcinoma HCC AND cisplatin AND neuropathy` | 0 | 1 |
| 2 | `Mitochondrial Permeability Transition Pores mPTP AND cisplatin` | 1 | 1 |
| 2 | `cisplatin AND ERCC1` | 0 | 2 |
| 2 | `ERCC1 AND rs11615` | 0 | 2 |
| 2 | `cisplatin AND peripheral neuropathy` | 0 | 2 |
| 2 | `GSTP1 AND rs1695` | 0 | 2 |

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

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** SLC28A3, GSTP1

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors such as the SLC28A3 and GSTP1 genes, with evidence suggesting a potential association but not definitive proof. The biological mechanism likely involves altered drug transport or metabolism due to these gene variants, leading to increased cardiotoxicity risk. For patient safety, pre-treatment biomarker screening for these genetic markers could be considered, although the current evidence is limited and further research is needed to establish robust predictive value. Alternative agents or dose adjustments based on genetic profiles might also be explored in future drug development.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `doxorubicin AND SLC28A3` | 0 | 2 |
| 2 | `doxorubicin AND GSTP1` | 0 | 2 |
| 2 | `doxorubicin AND RARG` | 0 | 2 |
| 2 | `cardiotoxicity AND genetic_variant` | 0 | 1 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `pediatric lymphoma AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `shortness of breath AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `heart muscle damage AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND doxorubicin` | 1 | 2 |
| 3 | `RARG rs2229774 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `early-onset chronic progressive cardiotoxicity AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `doxorubicin AND SLC28A3` | 0 | 2 |
| 2 | `doxorubicin AND GSTP1` | 0 | 2 |
| 2 | `doxorubicin AND RARG` | 0 | 2 |
| 2 | `Cardiotoxicity AND GSTA1` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** SLC28A3, GSTP1

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors such as SLC28A3 and GSTP1, though the evidence is not definitive. The biological mechanism likely involves altered drug transport or metabolism due to these variants, potentially leading to higher intracellular concentrations of doxorubicin and increased cardiotoxicity. For patient safety, pre-treatment biomarker screening for these genetic variants could help identify at-risk individuals who might benefit from dose adjustments or alternative agents with a lower risk of cardiotoxicity.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `doxorubicin AND SLC28A3` | 0 | 2 |
| 2 | `doxorubicin AND GSTP1` | 0 | 2 |
| 2 | `doxorubicin AND RARG` | 0 | 2 |
| 2 | `cardiotoxicity AND genetic_variant` | 0 | 1 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `pediatric lymphoma AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `shortness of breath AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `heart muscle damage AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND doxorubicin` | 1 | 2 |
| 3 | `RARG rs2229774 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `early-onset chronic progressive cardiotoxicity AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `doxorubicin AND SLC28A3` | 0 | 2 |
| 2 | `doxorubicin AND GSTP1` | 0 | 2 |
| 2 | `doxorubicin AND RARG` | 0 | 2 |
| 2 | `Cardiotoxicity AND GSTA1` | 0 | 2 |

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

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** SLC28A3 (rs7853758)

SLC28A3 (rs7853758) is a significant genetic marker linked to anthracycline-induced cardiotoxicity, with evidence suggesting it may influence susceptibility to cardiac damage. However, clinical factors such as cumulative dose and age are currently more predictive of cardiotoxicity in childhood cancer survivors than genetic polymorphisms like SLC28A3 (rs7853758). Further research is needed to clarify the role of pharmacogenomic biomarkers in predicting anthracycline-induced cardiotoxicity across different patient populations. Pre-treatment screening for these markers could still be valuable, but clinical factors should remain a primary focus for risk assessment and management.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `SLC28A3 AND anthracycline-related Cardiotoxicity` | 0 | 1 |
| 2 | `GSTP1 AND anthracycline-related Cardiotoxicity` | 0 | 1 |
| 2 | `RARG AND anthracycline-related Cardiotoxicity` | 0 | 0 |
| 2 | `SLC28A3 AND rs7853858` | 1 | 0 |
| 3 | `pharmacogenomic biomarkers AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `anthracycline-induced cardiotoxicity AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `childhood cancer survivors AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `SLC28A3 rs7853758 AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `GSTP1 rs1695 AND anthracycline AND cardiotoxicity` | 0 | 1 |
| 3 | `RARG rs2229774 AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `Osteosarcoma AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `Neoplasms AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 2 | `anthracycline AND SLC28A3` | 0 | 2 |
| 2 | `GSTP1 AND rs1695` | 0 | 2 |
| 2 | `RARG AND rs2229774` | 0 | 2 |
| 2 | `SLC28A3 AND cardiotoxicity` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** SLC28A3 (rs7853758), RARG (rs2229774)

SLC28A3 (rs7853758) is a significant genetic marker linked to anthracycline-induced cardiotoxicity, with evidence suggesting it may influence the likelihood of developing cardiotoxicity in childhood cancer survivors. However, clinical studies indicate that non-genetic factors such as cumulative dose and use of HER2-targeted antibodies are more predictive in certain populations like Chinese early-stage breast cancer patients. The biological mechanism underlying SLC28A3's role is not fully elucidated but may involve its function in nucleoside transport, affecting cardiomyocyte metabolism or drug accumulation. For drug discovery and patient safety, pre-treatment biomarker screening for SLC28A3 could be considered alongside clinical risk factors to tailor anthracycline dosing or explore alternative agents with lower cardiotoxicity profiles.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `SLC28A3 AND anthracycline-related Cardiotoxicity` | 0 | 1 |
| 2 | `RARG AND anthracycline-related Cardiotoxicity` | 0 | 0 |
| 3 | `GSTP1 AND rs1695 AND anthracycline-related Cardiotoxicity` | 0 | 1 |
| 3 | `pharmacogenomic biomarkers AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `anthracycline-induced cardiotoxicity AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `childhood cancer survivors AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `SLC28A3 rs7853758 AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `RARG rs2229774 AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `GSTP1 rs1695 AND anthracycline AND cardiotoxicity` | 0 | 1 |
| 3 | `CBR3 rs1056892 AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 3 | `ABCB1 rs1045642 AND anthracycline AND cardiotoxicity` | 0 | 2 |
| 2 | `SLC28A3 AND rs7853758` | 0 | 2 |
| 2 | `RARG AND rs2229774` | 0 | 2 |
| 2 | `GSTP1 AND rs1695` | 0 | 2 |
| 3 | `anthracycline AND Cardiotoxicity AND SLC28A3` | 0 | 2 |

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

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** CYP2D6*4

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of unmetabolized doxorubicin. This increased exposure can exacerbate cardiotoxicity due to prolonged cardiac tissue damage. For drug discovery and patient safety, pre-treatment screening for CYP2D6 variants is crucial to identify patients at risk and consider dose adjustments or alternative agents with lower cardiotoxic potential.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `CYP2D6*4 AND doxorubicin` | 0 | 0 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `CYP2D6*4 AND heart failure` | 0 | 0 |
| 2 | `RARG AND doxorubicin` | 0 | 2 |
| 2 | `CYP2D6*4 AND doxorubicin` | 1 | 0 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Neoplasm AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `heart failure AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND doxorubicin` | 1 | 2 |
| 3 | `RARG rs2229774 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `CDKN1A Suppression AND doxorubicin AND cardiotoxicity` | 0 | 1 |
| 2 | `doxorubicin AND CYP2D6*4` | 0 | 0 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `SLC28A3 AND rs7853758` | 0 | 2 |
| 2 | `GSTP1 AND rs1695` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** CYP2D6*4

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of unmetabolized doxorubicin. This increased exposure can exacerbate cardiotoxicity due to prolonged cardiac tissue damage. For drug discovery and patient safety, pre-treatment screening for CYP2D6 variants is crucial to identify patients at risk and consider dose adjustments or alternative agents with lower cardiotoxic potential.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `CYP2D6*4 AND doxorubicin` | 0 | 0 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `CYP2D6*4 AND heart failure` | 0 | 0 |
| 2 | `RARG AND doxorubicin` | 0 | 2 |
| 2 | `CYP2D6*4 AND doxorubicin` | 1 | 0 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Neoplasm AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `heart failure AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND doxorubicin` | 1 | 2 |
| 3 | `RARG rs2229774 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `CDKN1A Suppression AND doxorubicin AND cardiotoxicity` | 0 | 1 |
| 2 | `doxorubicin AND CYP2D6*4` | 0 | 0 |
| 2 | `doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `SLC28A3 AND rs7853758` | 0 | 2 |
| 2 | `GSTP1 AND rs1695` | 0 | 2 |

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

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** GSTM1

The adverse cardiac strain and heart muscle damage experienced by the patient's daughter after taking Adriamycin may be influenced by her GSTM1 status, as indicated by a moderate confidence level (0.70) linking GSTM1 to increased risk of cardiotoxicity from this drug. The biological mechanism likely involves oxidative stress and vascular aging, given that upregulation of GSTM1 is associated with these conditions in endothelial cells. For drug discovery and patient safety, pre-treatment genetic screening for specific GSTM1 variants could help identify patients at higher risk of Adriamycin-induced cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate this risk.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `Adriamycin AND cardiac strain` | 0 | 2 |
| 2 | `GSTM1 AND heart muscle damage` | 0 | 2 |
| 2 | `doxorubicin AND GSTM1` | 0 | 2 |
| 2 | `cardiotoxicity AND GSTP1` | 0 | 2 |
| 3 | `Adriamycin AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Cardiac strain AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Heart muscle damage AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `GSTM1 AND doxorubicin AND cardiotoxicity` | 0 | 1 |
| 3 | `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND doxorubicin` | 1 | 2 |
| 3 | `RARG rs2229774 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Doxorubicin AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `Adriamycin AND cardiac strain` | 0 | 2 |
| 2 | `GSTM1 AND heart muscle damage` | 0 | 2 |
| 3 | `doxorubicin AND GSTP1 AND rs1695` | 0 | 2 |
| 3 | `Cardiotoxicity AND RARG AND rs2229774` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** GSTM1, SLC28A3

Adriamycin-induced cardiac strain and heart muscle damage may be influenced by genetic factors such as GSTM1, though the evidence linking these is not definitive. The biological mechanism likely involves oxidative stress and DNA damage caused by Adriamycin, which can vary in severity based on individual genetic predispositions. For drug discovery and patient safety, pre-treatment biomarker screening for genes like SLC28A3 could help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate adverse effects.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `Adriamycin AND cardiac strain` | 0 | 2 |
| 2 | `GSTM1 AND heart muscle damage` | 0 | 2 |
| 2 | `doxorubicin AND GSTM1` | 0 | 2 |
| 2 | `cardiotoxicity AND GSTP1` | 0 | 2 |
| 3 | `Adriamycin AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Cardiac strain AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Heart muscle damage AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `GSTM1 AND doxorubicin AND cardiotoxicity` | 0 | 1 |
| 3 | `SLC28A3 rs7853758 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `GSTP1 rs1695 AND doxorubicin` | 1 | 2 |
| 3 | `RARG rs2229774 AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 3 | `Doxorubicin AND doxorubicin AND cardiotoxicity` | 0 | 2 |
| 2 | `Adriamycin AND cardiac strain` | 0 | 2 |
| 2 | `GSTM1 AND heart muscle damage` | 0 | 2 |
| 3 | `doxorubicin AND GSTP1 AND rs1695` | 0 | 2 |
| 3 | `Cardiotoxicity AND RARG AND rs2229774` | 0 | 2 |

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

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

#### Phase 8 — combined topics, abstracts

**Genes surfaced:** ERCC1, CYBA

Doxorubicin-induced mucositis is associated with genetic polymorphisms in ERCC1 (rs11615) and CYBA (rs4673). These variants likely influence the biological mechanism by modulating DNA repair efficiency and oxidative stress response, respectively. For drug discovery and patient safety, pre-treatment screening for these risk factors could enable personalized dosing strategies or identification of patients at higher risk who might benefit from mucositis prophylaxis or alternative agents.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `doxorubicin AND ERCC1` | 0 | 2 |
| 2 | `doxorubicin AND CYBA` | 0 | 2 |
| 2 | `ERCC1 AND mucositis` | 0 | 2 |
| 2 | `CYBA AND mucositis` | 0 | 2 |
| 2 | `doxorubicin AND mucositis` | 0 | 2 |
| 2 | `mucositis AND doxorubicin` | 0 | 2 |
| 2 | `ERCC1 rs11615 AND doxorubicin` | 1 | 2 |
| 2 | `CYBA rs4673 AND doxorubicin` | 1 | 2 |
| 2 | `chemotherapy-induced neutropenia CIN AND doxorubicin` | 1 | 2 |
| 3 | `febrile neutropenia FN AND doxorubicin AND mucositis` | 0 | 2 |
| 3 | `anemia AND doxorubicin AND mucositis` | 0 | 2 |
| 3 | `anthracyclines AND doxorubicin AND mucositis` | 0 | 2 |
| 2 | `doxorubicin AND ERCC1` | 0 | 2 |
| 2 | `doxorubicin AND rs11615` | 0 | 2 |
| 2 | `mucositis AND ERCC1` | 0 | 2 |
| 3 | `CYBA AND doxorubicin AND rs4673` | 0 | 2 |

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

#### Phase 9 — combined topics + full text

**Genes surfaced:** ERCC1, CYBA

Doxorubicin-induced mucositis is associated with genetic polymorphisms in ERCC1 (rs11615) and CYBA (rs4673). These variants likely influence the biological mechanism by modulating DNA repair efficiency and oxidative stress response, respectively. For drug discovery and patient safety, pre-treatment screening for these risk factors could enable personalized dosing strategies or identification of patients at higher risk who might benefit from mucositis prophylaxis or alternative agents.

**Queries issued (terms searched together):**

| Terms | Query | Back-offs | Hits |
|---|---|---|---|
| 2 | `doxorubicin AND ERCC1` | 0 | 2 |
| 2 | `doxorubicin AND CYBA` | 0 | 2 |
| 2 | `ERCC1 AND mucositis` | 0 | 2 |
| 2 | `CYBA AND mucositis` | 0 | 2 |
| 2 | `doxorubicin AND mucositis` | 0 | 2 |
| 2 | `mucositis AND doxorubicin` | 0 | 2 |
| 2 | `ERCC1 rs11615 AND doxorubicin` | 1 | 2 |
| 2 | `CYBA rs4673 AND doxorubicin` | 1 | 2 |
| 2 | `chemotherapy-induced neutropenia CIN AND doxorubicin` | 1 | 2 |
| 3 | `febrile neutropenia FN AND doxorubicin AND mucositis` | 0 | 2 |
| 3 | `anemia AND doxorubicin AND mucositis` | 0 | 2 |
| 3 | `anthracyclines AND doxorubicin AND mucositis` | 0 | 2 |
| 2 | `doxorubicin AND ERCC1` | 0 | 2 |
| 2 | `doxorubicin AND rs11615` | 0 | 2 |
| 2 | `mucositis AND ERCC1` | 0 | 2 |
| 3 | `CYBA AND doxorubicin AND rs4673` | 0 | 2 |

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

---

