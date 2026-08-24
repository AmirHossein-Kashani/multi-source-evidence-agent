# ADR clinical QA — Phase 6 & 7 (open, LLM-directed literature search)

Phases 4/5 could only read the papers ClinPGx already cites for a gene–drug pair. **Phases 6/7 remove that restriction**: an LLM that has seen the question *and* the evidence and knowledge-graph content retrieved so far chooses the search topics, and each topic is searched separately on PubMed.

| Phase | Configuration | Literature access |
|---|---|---|
| **Phase 6** | `AMG_KB_SOURCE=pharmgkb+pubmed_open` | Free topic search — abstracts |
| **Phase 7** | `+ AMG_PUBMED_FULLTEXT=1` | Free topic search — full paper via PMC |

ClinPGx grounding stays on in both, so these are *phase 3 + unrestricted literature*. Papers marked **NEW** were never cited by ClinPGx for these pairs, i.e. they are reachable only because the search was opened up.

## Summary

| # | Topics chosen (phase 7) | Papers | NEW vs phases 4/5 | Full text |
|---|---|---|---|---|
| Q1 | cisplatin ototoxicity genetics; GSTM1 cisplatin deafness; TPMT variant ototoxicity; ACYP2 hearing loss | 20 | **20** | 1 |
| Q2 | cisplatin ototoxicity gstm1; tpmt cisplatin ototoxicity; comt variant ototoxicity | 19 | **17** | 0 |
| Q3 | TPMT variant ototoxicity; cisplatin neuroblastoma hearing; ACYP2 cisplatin ototoxicity | 19 | **19** | 0 |
| Q4 | cisplatin ototoxicity GSTT1; GSTT1 status hearing loss; cisplatin pharmacogenomics GSTT1; cisplatin ototoxicity gstt1; gstt1 status hearing loss | 20 | **20** | 1 |
| Q5 | cisplatin neuropathy genetics; ERCC1 cisplatin toxicity; GSTP1 peripheral neuropathy; cisplatin peripheral neuropathy genetics; GSTM3 cisplatin toxicity | 20 | **20** | 0 |
| Q6 | doxorubicin cardiotoxicity SLC28A3; GSTP1 doxorubicin toxicity | 18 | **18** | 0 |
| Q7 | anthracycline cardiotoxicity SLC28A3; RARG anthracycline cardiotoxicity; GSTP1 osteosarcoma cardiotoxicity; RARG rs2229774 cancer | 15 | **15** | 1 |
| Q8 | doxorubicin cardiotoxicity CYP2D6; SLC28A3 heart failure; GSTP1 neoplasm risk; SLC28A3 doxorubicin heart failure | 20 | **20** | 0 |
| Q9 | adriamycin cardiotoxicity gstm1; doxorubicin heart damage genetics; anthracycline toxicity slc28a3 | 21 | **21** | 2 |
| Q10 | anthracycline mucositis genetics; genetic predisposition mucositis | 14 | **14** | 1 |
| | **Total** | **186** | **184** | **6** |

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

#### Phase 6 — open search, abstracts

**Genes surfaced:** GSTM1 non-null

The genetic variants GSTM1 non-null are implicated in cisplatin-induced ototoxicity, including hearing loss and tinnitus. Individuals lacking the null variant of GSTM1 (GSTM1 non-null) have reduced detoxification capacity due to lower glutathione S-transferase activity, leading to increased oxidative stress and inflammation in the cochlea. This highlights the need for pre-treatment genetic screening for GSTM1 status to identify patients at higher risk of ototoxicity, potentially allowing for dose adjustments or the use of alternative agents such as carboplatin, which has a lower incidence of ototoxic side effects.

**Search topics the model chose:** `cisplatin ototoxicity genetics`; `GSTM1 hearing loss`; `TPMT ototoxicity variants`; `GSTM1 tinnitus risk`

<details><summary>Papers retrieved</summary>

- `PMID:42633148` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin ototoxicity genetics`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 tinnitus risk`
- `PMID:40222694` **[NEW]** — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:TPMT ototoxicity variants`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635394` **[NEW]** — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635355` **[NEW]** — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635501` **[NEW]** — **Normative Ranges for Auditory Brainstem Response Wave I Amplitude: A Potential Diagnostic Indicator of Cochlear Deafferentation.** — *American journal of audiology · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42634562` **[NEW]** — **Assessment of Transverse-sigmoid Sinus Dural Arteriovenous Fistula using Transcranial Doppler Ultrasonography: A Case Report.** — *Current medical imaging · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42091970` **[NEW]** — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 non-null`
- `PMID:36672743` **[NEW]** — **Molecular Characterization of Tropomyosin and Its Potential Involvement in Muscle Contraction in Pacific Abalone.** — *Genes · 2022*
  - via `llm_topic:TPMT*1`
- `PMID:18775689` **[NEW]** — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT*1`
- `PMID:41077199` **[NEW]** — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:rs4646316`
- `PMID:36802061` **[NEW]** — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:rs4646316`
- `PMID:42621050` **[NEW]** — **Integrating multi-omics and deep learning to explore the active ingredients and molecular mechanisms of Cinnamomum migao volatile oil in the treatment of coronary heart disease.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:Gadd45a`
- `PMID:42532387` **[NEW]** — **Comparative transcriptomic analysis reveals immune regulation in mandarin fish (Siniperca chuatsi) under high- and low-temperature.** — *Developmental and comparative immunology · 2026*
  - via `llm_topic:CXCL family protein expression`

</details>

<sub>KG: 28 entities / 86 relations · 23 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** ACYP2, GSTM1

The development of hearing loss and tinnitus due to cisplatin treatment is associated with genetic variants in ACYP2 (acylphosphatase 2) and GSTM1 (glutathione S-transferase mu 1). Specifically, the variant rs1872328 in ACYP2 has been linked to increased susceptibility to ototoxicity. The biological mechanisms underlying these associations are not fully understood but may involve altered cellular processes such as DNA repair or stress kinase signaling that affect cell survival during cisplatin exposure. For drug discovery and patient safety, pre-treatment genetic screening for variants like rs1872328 in ACYP2 could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents to mitigate these side effects.

**Search topics the model chose:** `cisplatin ototoxicity genetics`; `GSTM1 cisplatin deafness`; `TPMT variant ototoxicity`; `ACYP2 hearing loss`

<details><summary>Papers retrieved</summary>

- `PMID:42633148/PMC13499120` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin ototoxicity genetics+pmc_xml`
- `PMID:37726872` **[NEW]** — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `llm_topic:ACYP2 hearing loss`
- `PMID:42633148` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin ototoxicity genetics`
- `PMID:38518393` **[NEW]** — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:GSTM1 cisplatin deafness`
- `PMID:40222694` **[NEW]** — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:TPMT variant ototoxicity`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635634` **[NEW]** — **CORRIGENDUM: Curcumin nanoparticles combined with 3D printed bionic tumor models for breast cancer treatment (2023Biofabrication 15 014105).** — *Biofabrication · 2026*
  - via `llm_topic:cancer`
- `PMID:42635633` **[NEW]** — **Mesoporous-Shell Monolayer Plasmonic Architecture Enables Quantitative and Decision-Guided SERS.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `llm_topic:cancer`
- `PMID:42635394` **[NEW]** — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635355` **[NEW]** — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635501` **[NEW]** — **Normative Ranges for Auditory Brainstem Response Wave I Amplitude: A Potential Diagnostic Indicator of Cochlear Deafferentation.** — *American journal of audiology · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42634562` **[NEW]** — **Assessment of Transverse-sigmoid Sinus Dural Arteriovenous Fistula using Transcranial Doppler Ultrasonography: A Case Report.** — *Current medical imaging · 2026*
  - via `llm_topic:tinnitus`
- `PMID:42631829` **[NEW]** — **Inner Ear Organoids: Recent Progress and Challenges.** — *Stem cell reviews and reports · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:36802061` **[NEW]** — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:31666714` **[NEW]** — **Genetic variation of cisplatin-induced ototoxicity in non-cranial-irradiated pediatric patients using a candidate gene approach: The International PanCareLIFE Study.** — *The pharmacogenomics journal · 2020*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` **[NEW]** — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:18775689` **[NEW]** — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:16621695` **[NEW]** — **Cloning and characterization of a new multi-stress inducible metallothionein gene in Tetrahymena pyriformis.** — *Protist · 2006*
  - via `llm_topic:TPMT TPMT*1`

</details>

<sub>KG: 33 entities / 86 relations · 27 references</sub>

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

#### Phase 6 — open search, abstracts

**Genes surfaced:** GSTM1 (non-null), TPMT, COMT

Cisplatin-induced ototoxicity risk in pediatric cancer patients is primarily associated with the GSTM1 (non-null) genotype, which has been linked to an increased susceptibility to hearing damage due to cisplatin. Other genes such as TPMT and COMT also play a role but require further validation. The biological mechanism likely involves impaired detoxification of reactive metabolites generated by cisplatin, leading to oxidative stress and cellular damage in the auditory system. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could help identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower ototoxicity profile.

**Search topics the model chose:** `cisplatin ototoxicity gstm1`; `tpmt cisplatin ototoxicity`; `comt variant ototoxicity`

<details><summary>Papers retrieved</summary>

- `PMID:38518393` **[NEW]** — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity gstm1`
- `PMID:41637682` **[NEW]** — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `llm_topic:tpmt cisplatin ototoxicity`
- `PMID:40222694` **[NEW]** — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:comt variant ototoxicity`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42633148` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42631829` **[NEW]** — **Inner Ear Organoids: Recent Progress and Challenges.** — *Stem cell reviews and reports · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` **[NEW]** — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:18775689` **[NEW]** — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:16621695` **[NEW]** — **Cloning and characterization of a new multi-stress inducible metallothionein gene in Tetrahymena pyriformis.** — *Protist · 2006*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:COMT rs4646316`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:COMT rs4646316`
- `PMID:42597480` **[NEW]** — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42577562` **[NEW]** — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42634570` **[NEW]** — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2`
- `PMID:42634542` **[NEW]** — **Mumio Potentiates Temozolomide by Inducing Apoptosis and Ferroptosis in Glioblastoma Cells.** — *Current pharmaceutical design · 2026*
  - via `llm_topic:NRF2`
- `PMID:42635394` **[NEW]** — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`
- `PMID:42635355` **[NEW]** — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`

</details>

<sub>KG: 31 entities / 86 relations · 30 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** GSTM1 (non-null), TPMT, COMT

Cisplatin-induced ototoxicity risk in pediatric cancer patients is primarily associated with the GSTM1 (non-null) genotype, which has been linked to an increased susceptibility to hearing damage due to cisplatin. Other genes such as TPMT and COMT also play a role but require further validation. The biological mechanism likely involves impaired detoxification of reactive metabolites generated by cisplatin, leading to oxidative stress and cellular damage in the auditory system. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could help identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower ototoxicity profile.

**Search topics the model chose:** `cisplatin ototoxicity gstm1`; `tpmt cisplatin ototoxicity`; `comt variant ototoxicity`

<details><summary>Papers retrieved</summary>

- `PMID:38518393` **[NEW]** — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity gstm1`
- `PMID:41637682` **[NEW]** — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `llm_topic:tpmt cisplatin ototoxicity`
- `PMID:40222694` **[NEW]** — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:comt variant ototoxicity`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42633148` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42631829` **[NEW]** — **Inner Ear Organoids: Recent Progress and Challenges.** — *Stem cell reviews and reports · 2026*
  - via `llm_topic:ototoxicity`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` **[NEW]** — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:18775689` **[NEW]** — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:16621695` **[NEW]** — **Cloning and characterization of a new multi-stress inducible metallothionein gene in Tetrahymena pyriformis.** — *Protist · 2006*
  - via `llm_topic:TPMT TPMT*1`
- `PMID:41077199` — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:COMT rs4646316`
- `PMID:36802061` — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:COMT rs4646316`
- `PMID:42597480` **[NEW]** — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42577562` **[NEW]** — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTT1`
- `PMID:42634570` **[NEW]** — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2`
- `PMID:42634542` **[NEW]** — **Mumio Potentiates Temozolomide by Inducing Apoptosis and Ferroptosis in Glioblastoma Cells.** — *Current pharmaceutical design · 2026*
  - via `llm_topic:NRF2`
- `PMID:42635394` **[NEW]** — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`
- `PMID:42635355` **[NEW]** — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing research`

</details>

<sub>KG: 31 entities / 86 relations · 30 references</sub>

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

#### Phase 6 — open search, abstracts

**Genes surfaced:** TPMT

The TPMT variant is implicated in the increased risk of cisplatin-induced ototoxicity in your daughter. This genetic variation affects drug metabolism, leading to reduced detoxification and potentially higher levels of cisplatin in her system, thereby increasing the likelihood of hearing loss. For patient safety, pre-treatment screening for TPMT variants should be conducted to identify patients at high risk. Dose adjustments or alternative agents such as carboplatin may need to be considered based on genetic profiles.

**Search topics the model chose:** `cisplatin ototoxicity tpmt`; `neuroblastoma hearing loss risk`; `tpmt variant cisplatin toxicity`

<details><summary>Papers retrieved</summary>

- `PMID:41637682` **[NEW]** — **TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.** — *JCO oncology practice · 2026*
  - via `llm_topic:cisplatin ototoxicity tpmt`
- `PMID:42504125` **[NEW]** — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `llm_topic:neuroblastoma hearing loss risk`
- `PMID:28406961` **[NEW]** — **Pharmacogenetic variants in TPMT alter cellular responses to cisplatin in inner ear cell lines.** — *PloS one · 2017*
  - via `llm_topic:tpmt variant cisplatin toxicity`
- `PMID:42560154` **[NEW]** — **Clinical Functional Assignment of TPMT and NUDT15 Alleles by the Clinical Pharmacogenetics Implementation Consortium Pharmacogene Curation Expert Panel.** — *Clinical pharmacology and therapeutics · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42560047` **[NEW]** — **Pharmacogenomic biomarkers in oncology: evidence, clinical utility, and barriers to implementation.** — *Journal of chemotherapy (Florence, Italy) · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634987` **[NEW]** — **Unveiling the neurodevelopmental toxicity of PFOA and PFOS: evidence from integration of in silico and in vitro study.** — *Toxicology mechanisms and methods · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42634612` **[NEW]** — **Radiographic overestimation of inferior vena cava involvement in pediatric neuroblastoma: a case report.** — *Journal of surgical case reports · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42634792` **[NEW]** — **Hearing Aids Use Preferences Among Older Adults with Hearing Loss: A Discrete Choice Experiment.** — *Patient preference and adherence · 2026*
  - via `llm_topic:audiologist`
- `PMID:42625608` **[NEW]** — **Factors influencing the professional quality of life in South African audiologists.** — *Frontiers in psychology · 2026*
  - via `llm_topic:audiologist`
- `PMID:42635394` **[NEW]** — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635355` **[NEW]** — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:hearing loss`
- `PMID:42635234` **[NEW]** — **Discovering reference-missing cell types in bulk transcriptomics.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic reason`
- `PMID:42634009` **[NEW]** — **Immune-Enriched Versus Matrix-Remodeling Microenvironments in Psammoma Body-Rich and Psammoma Body-Poor WHO Grade I Meningiomas: An Exploratory Transcriptomic Study.** — *Neuropathology : official journal of the Japanese Society of Neuropathology · 2026*
  - via `llm_topic:genetic reason`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` **[NEW]** — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:36672743` **[NEW]** — **Molecular Characterization of Tropomyosin and Its Potential Involvement in Muscle Contraction in Pacific Abalone.** — *Genes · 2022*
  - via `llm_topic:TPMT*1`
- `PMID:18775689` **[NEW]** — **Duplex pyrosequencing of the TPMT*3C and TPMT*6 alleles in Korean and Vietnamese populations.** — *Clinica chimica acta; international journal of clinical chemistry · 2008*
  - via `llm_topic:TPMT*1`

</details>

<sub>KG: 30 entities / 86 relations · 26 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** TPMT, ACYP2 (rs1872328), GSTM1

The TPMT variant is a key genetic factor implicated in the ototoxicity associated with cisplatin treatment for Neuroblastoma. This variant affects drug metabolism, potentially leading to higher levels of cisplatin and increased risk of hearing loss due to impaired detoxification pathways. Additionally, other genetic variants such as ACYP2 (rs1872328) and GSTM1 also modulate the response to cisplatin, further exacerbating ototoxic effects. For drug discovery and patient safety, pre-treatment biomarker screening for TPMT and related genes is crucial to identify high-risk patients who may benefit from dose adjustments or alternative agents with lower ototoxic potential.

**Search topics the model chose:** `TPMT variant ototoxicity`; `cisplatin neuroblastoma hearing`; `ACYP2 cisplatin ototoxicity`

<details><summary>Papers retrieved</summary>

- `PMID:40222694` **[NEW]** — **Pharmacogenomics in pediatric oncology patients with solid tumors related to chemotherapy-induced toxicity: A systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - via `llm_topic:TPMT variant ototoxicity`
- `PMID:42504125` **[NEW]** — **Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With Cancer Assessed by the SIOP Boston 2012 Ototoxicity Criteria.** — *Pediatric blood & cancer · 2026*
  - via `llm_topic:cisplatin neuroblastoma hearing`
- `PMID:37726872` **[NEW]** — **Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced Ototoxicity: Canadian Pharmacogenomics Network for Drug Safety 2022 Update.** — *Therapeutic drug monitoring · 2023*
  - via `llm_topic:ACYP2 cisplatin ototoxicity`
- `PMID:42560154` **[NEW]** — **Clinical Functional Assignment of TPMT and NUDT15 Alleles by the Clinical Pharmacogenetics Implementation Consortium Pharmacogene Curation Expert Panel.** — *Clinical pharmacology and therapeutics · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42560047` **[NEW]** — **Pharmacogenomic biomarkers in oncology: evidence, clinical utility, and barriers to implementation.** — *Journal of chemotherapy (Florence, Italy) · 2026*
  - via `llm_topic:TPMT variant`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634987` **[NEW]** — **Unveiling the neurodevelopmental toxicity of PFOA and PFOS: evidence from integration of in silico and in vitro study.** — *Toxicology mechanisms and methods · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42634612` **[NEW]** — **Radiographic overestimation of inferior vena cava involvement in pediatric neuroblastoma: a case report.** — *Journal of surgical case reports · 2026*
  - via `llm_topic:Neuroblastoma`
- `PMID:42635394` **[NEW]** — **Age-Related Changes in Middle-Ear Sound Transmission: Insights From Wideband Acoustic Immittance, Distortion Product Otoacoustic Emissions, and Air-Bone Gap Analysis.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing loss`
- `PMID:42635355` **[NEW]** — **The Intelligibility-Based Repeat-Recall Test: I. Bayesian-Guided Estimation of Multiple Speech Reception Thresholds.** — *Ear and hearing · 2026*
  - via `llm_topic:Hearing loss`
- `PMID:36802061` **[NEW]** — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:31666714` **[NEW]** — **Genetic variation of cisplatin-induced ototoxicity in non-cranial-irradiated pediatric patients using a candidate gene approach: The International PanCareLIFE Study.** — *The pharmacogenomics journal · 2020*
  - via `llm_topic:ACYP2 rs1872328`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42091970` **[NEW]** — **Genetic susceptibility and gene-environment interactions in gastric cancer among ethnic populations of Northeast India.** — *Scientific reports · 2026*
  - via `llm_topic:GSTM1 GSTM1 non-null`
- `PMID:42634458` **[NEW]** — **[Perioperative Safety Analysis of Preoperative Targeted Therapy in Patients with ALK-positive Non-small Cell Lung Cancer].** — *Zhongguo fei ai za zhi = Chinese journal of lung cancer · 2026*
  - via `llm_topic:Brain Neoplasms`
- `PMID:42634231` **[NEW]** — **Refractory Hyperammonemic Encephalopathy as a Paraneoplastic Presentation of Fibrolamellar Hepatocellular Carcinoma: A Case Report.** — *The American journal of case reports · 2026*
  - via `llm_topic:Brain Neoplasms`
- `PMID:42635414` **[NEW]** — **The Ergonomics of Endoscopic Ear Surgery: An International Survey.** — *Otology & neurotology : official publication of the American Otological Society, American Neurotology Society [and] European Academy of Otology and Neurotology · 2026*
  - via `llm_topic:Deafness`
- `PMID:42633998` **[NEW]** — **Transcanal Cochlear Implantation Under Endoscopic Guidance with Canal Closure in a Pediatric Patient with CHARGE Syndrome: A Case Report and Surgical Technique.** — *Acta medica Okayama · 2026*
  - via `llm_topic:Deafness`

</details>

<sub>KG: 31 entities / 86 relations · 28 references</sub>

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

#### Phase 6 — open search, abstracts

**Genes surfaced:** GSTT1

The adverse reaction of inner ear damage following Platinol treatment is likely influenced by the GSTT1 status, as indicated by a study published in Hearing Research (2024). The GSTT1 null genotype has been associated with increased susceptibility to cisplatin-induced ototoxicity. This suggests that genetic polymorphisms affecting glutathione S-transferase activity may impair the detoxification of reactive metabolites generated during cisplatin treatment, leading to greater cellular damage in the inner ear. For drug discovery and patient safety, pre-treatment screening for GSTT1 status could help identify patients at higher risk for ototoxicity, allowing for dose adjustments or consideration of alternative agents such as carboplatin.

**Search topics the model chose:** `cisplatin ototoxicity GSTT1`; `GSTT1 status hearing loss`; `cisplatin pharmacogenomics GSTT1`; `cisplatin ototoxicity gstt1`; `gstt1 status hearing loss`

<details><summary>Papers retrieved</summary>

- `PMID:38518393` **[NEW]** — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity gstt1`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:gstt1 status hearing loss`
- `PMID:40342074` **[NEW]** — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `llm_topic:cisplatin pharmacogenomics GSTT1`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:Platinol`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:Platinol`
- `PMID:42627828` **[NEW]** — **Tox regulates hair cell stereocilia development and Cdh23 expression in mice and zebrafish.** — *Proceedings of the National Academy of Sciences of the United States of America · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42621021` **[NEW]** — **NADPH oxidase 3 inhibition preserves hearing in mice after stereotactic radiosurgery.** — *Molecular therapy. Nucleic acids · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42597480` **[NEW]** — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42511983` **[NEW]** — **A Multilevel Redox-Based Prognostic Model for Asthma Severity: From Genotype to Serum Biomarkers.** — *Biomedicines · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42633148` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42555790` **[NEW]** — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42123691` **[NEW]** — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` **[NEW]** — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` **[NEW]** — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` **[NEW]** — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634570` **[NEW]** — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2 genes`
- `PMID:42633538` **[NEW]** — **Platycodon grandiflorus decoction against lipopolysaccharide (LPS)-induced acute lung injury via Keap1/Nrf2/ARE signaling pathway.** — *Pakistan journal of pharmaceutical sciences · 2026*
  - via `llm_topic:NRF2 genes`

</details>

<sub>KG: 33 entities / 86 relations · 28 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** GSTT1

The GSTT1 null genotype is implicated in the increased risk for permanent inner ear damage caused by Platinol (cisplatin). The likely biological mechanism involves reduced glutathione S-transferase activity, which normally detoxifies reactive metabolites of cisplatin that can cause ototoxicity. This genetic predisposition highlights the importance of pre-treatment biomarker screening to identify patients at higher risk for adverse effects, potentially allowing for dose adjustment or selection of alternative agents such as carboplatin, which has a lower incidence of ototoxicity.

**Search topics the model chose:** `cisplatin ototoxicity GSTT1`; `GSTT1 status hearing loss`; `cisplatin pharmacogenomics GSTT1`; `cisplatin ototoxicity gstt1`; `gstt1 status hearing loss`

<details><summary>Papers retrieved</summary>

- `PMID:38518393` **[NEW]** — **Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibility to cisplatin-induced ototoxicity: A preliminary study.** — *Hearing research · 2024*
  - via `llm_topic:cisplatin ototoxicity gstt1`
- `PMID:42382212/PMC13316012` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:gstt1 status hearing loss+pmc_xml`
- `PMID:42382212` **[NEW]** — **Interactive Effects of Occupational Hearing Loss and Glutathion S-Transferase M1 Genotype on Tinnitus Among Noise-exposed Steelworkers.** — *Safety and health at work · 2026*
  - via `llm_topic:GSTT1 status hearing loss`
- `PMID:40342074` **[NEW]** — **Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With Head and Neck Squamous Cell Carcinoma Undergoing Definitive Chemoradiotherapy.** — *Head & neck · 2025*
  - via `llm_topic:cisplatin pharmacogenomics GSTT1`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:Platinol`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:Platinol`
- `PMID:42627828` **[NEW]** — **Tox regulates hair cell stereocilia development and Cdh23 expression in mice and zebrafish.** — *Proceedings of the National Academy of Sciences of the United States of America · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42621021` **[NEW]** — **NADPH oxidase 3 inhibition preserves hearing in mice after stereotactic radiosurgery.** — *Molecular therapy. Nucleic acids · 2026*
  - via `llm_topic:inner ear damage`
- `PMID:42597480` **[NEW]** — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42511983` **[NEW]** — **A Multilevel Redox-Based Prognostic Model for Asthma Severity: From Genotype to Serum Biomarkers.** — *Biomedicines · 2026*
  - via `llm_topic:GSTT1 status`
- `PMID:42633148` **[NEW]** — **Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL family protein expression.** — *Military Medical Research · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42555790` **[NEW]** — **Cisplatin's Silent Toxicity: Hearing Loss, Ethics, and the Nursing Voice.** — *Clinical journal of oncology nursing · 2026*
  - via `llm_topic:cisplatin-induced ototoxicity`
- `PMID:42123691` **[NEW]** — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` **[NEW]** — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` **[NEW]** — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` **[NEW]** — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634570` **[NEW]** — **The Impact of Microbial Toxins on NRF2 Signaling, Focusing on Stem Cells: Mechanisms and Therapeutic Potential.** — *Current molecular medicine · 2026*
  - via `llm_topic:NRF2 genes`
- `PMID:42633538` **[NEW]** — **Platycodon grandiflorus decoction against lipopolysaccharide (LPS)-induced acute lung injury via Keap1/Nrf2/ARE signaling pathway.** — *Pakistan journal of pharmaceutical sciences · 2026*
  - via `llm_topic:NRF2 genes`

</details>

<sub>KG: 33 entities / 86 relations · 29 references</sub>

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

#### Phase 6 — open search, abstracts

**Genes surfaced:** ERCC1, GSTP1, GSTM3

Cisplatin-induced peripheral neuropathy is influenced by genetic factors such as ERCC1 (rs11615), GSTP1, and GSTM3. These genes likely modulate the metabolism or cellular response to cisplatin, affecting neuronal toxicity and susceptibility to CIPN. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help predict risk and tailor treatment plans, including dose adjustments or alternative agents with similar efficacy but lower neurotoxicity.

**Search topics the model chose:** `cisplatin neuropathy genetics`; `ERCC1 cisplatin toxicity`; `GSTP1 peripheral neuropathy`; `cisplatin peripheral neuropathy genetics`; `GSTM3 cisplatin toxicity`

<details><summary>Papers retrieved</summary>

- `PMID:42363989` **[NEW]** — **Ex vivo modulation of monocyte/macrophage phenotypes by all-trans retinoic acid in chemotherapy-induced peripheral neuropathy.** — *Molecular biology reports · 2026*
  - via `llm_topic:cisplatin peripheral neuropathy genetics`
- `PMID:39560009` **[NEW]** — **Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limitations.** — *Personalized medicine · 2024*
  - via `llm_topic:GSTM3 cisplatin toxicity`
- `PMID:41984466` **[NEW]** — **Biowaste-Archetyped Hierarchical Calcium Carbonate Nanoreactors Induce Tumor Bioenergetic Crisis and Reverse Cisplatin Resistance via Mitochondrial Metabolic Reprogramming.** — *ACS applied materials & interfaces · 2026*
  - via `llm_topic:ERCC1 cisplatin toxicity`
- `PMID:42494534` **[NEW]** — **Why pharmacogenomic biomarkers for chemotherapy-induced peripheral neuropathy fail: a systematic review of genetic associations, replication, and clinical translation.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:GSTP1 peripheral neuropathy`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635220` **[NEW]** — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` **[NEW]** — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42635172` **[NEW]** — **Mediation of Smoking and Cardiometabolic Factors on Diabetic Peripheral Neuropathy.** — *Nursing research · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42634428` **[NEW]** — **Clinical Pharmacology of Eplontersen, the First Approved GalNAc-Conjugated Antisense Oligonucleotide.** — *Journal of clinical pharmacology · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42123691` **[NEW]** — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` **[NEW]** — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` **[NEW]** — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` **[NEW]** — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634682` **[NEW]** — **Severe Pulmonary Differentiation Syndrome Despite Corticosteroid Prophylaxis in Acute Promyelocytic Leukemia: Clinical Improvement With Pulse Methylprednisolone Therapy and High-Flow Nasal Cannula.** — *Cureus · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42629042` **[NEW]** — **Retinoic acid priming enhances myogenesis of bovine muscle stem cells for cultivated meat production by modulating mitochondrial function.** — *Food research international (Ottawa, Ont.) · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42621781` **[NEW]** — **METTL3-mediated m6A modification of circMtmr7 contributes to paclitaxel-induced peripheral neuropathy in the dorsal horn.** — *The Journal of physiology · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`
- `PMID:42609802` **[NEW]** — **The Ethanol-Insoluble Low-Molecular-Weight Fraction LEP-4 Derived From Lentinula edodes Mycelia Extract Attenuates Oxaliplatin-Evoked Allodynia in Mice.** — *Advances in pharmacological and pharmaceutical sciences · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`

</details>

<sub>KG: 32 entities / 86 relations · 25 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** ERCC1, GSTP1, GSTM3

Cisplatin-induced peripheral neuropathy is influenced by genetic factors such as ERCC1 (rs11615), GSTP1, and GSTM3. These genes likely modulate the metabolism or cellular response to cisplatin, affecting neuronal toxicity and susceptibility to CIPN. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help predict risk and tailor treatment plans, including dose adjustments or alternative agents with similar efficacy but lower neurotoxicity.

**Search topics the model chose:** `cisplatin neuropathy genetics`; `ERCC1 cisplatin toxicity`; `GSTP1 peripheral neuropathy`; `cisplatin peripheral neuropathy genetics`; `GSTM3 cisplatin toxicity`

<details><summary>Papers retrieved</summary>

- `PMID:42363989` **[NEW]** — **Ex vivo modulation of monocyte/macrophage phenotypes by all-trans retinoic acid in chemotherapy-induced peripheral neuropathy.** — *Molecular biology reports · 2026*
  - via `llm_topic:cisplatin peripheral neuropathy genetics`
- `PMID:39560009` **[NEW]** — **Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limitations.** — *Personalized medicine · 2024*
  - via `llm_topic:GSTM3 cisplatin toxicity`
- `PMID:41984466` **[NEW]** — **Biowaste-Archetyped Hierarchical Calcium Carbonate Nanoreactors Induce Tumor Bioenergetic Crisis and Reverse Cisplatin Resistance via Mitochondrial Metabolic Reprogramming.** — *ACS applied materials & interfaces · 2026*
  - via `llm_topic:ERCC1 cisplatin toxicity`
- `PMID:42494534` **[NEW]** — **Why pharmacogenomic biomarkers for chemotherapy-induced peripheral neuropathy fail: a systematic review of genetic associations, replication, and clinical translation.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:GSTP1 peripheral neuropathy`
- `PMID:42634497` **[NEW]** — **Concurrent chemoradiotherapy for metastatic vulvar extramammary Paget's disease involving supraclavicular nodes: a case report.** — *Radiation oncology journal · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42634368` **[NEW]** — **HE4 Silence Combined with DDP in the Treatment of Ovarian Cancer, Especially Platinum-resistant Ovarian Cancer.** — *Current cancer drug targets · 2026*
  - via `llm_topic:cisplatin`
- `PMID:42635220` **[NEW]** — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` **[NEW]** — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42635172` **[NEW]** — **Mediation of Smoking and Cardiometabolic Factors on Diabetic Peripheral Neuropathy.** — *Nursing research · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42634428` **[NEW]** — **Clinical Pharmacology of Eplontersen, the First Approved GalNAc-Conjugated Antisense Oligonucleotide.** — *Journal of clinical pharmacology · 2026*
  - via `llm_topic:peripheral neuropathy`
- `PMID:42123691` **[NEW]** — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` **[NEW]** — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:30112115` **[NEW]** — **Association between genetic polymorphisms and platinum-induced ototoxicity in children.** — *Oncotarget · 2018*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:26857559` **[NEW]** — **A pharmacogenetic pilot study reveals MTHFR, DRD3, and MDR1 polymorphisms as biomarker candidates for slow atorvastatin metabolizers.** — *BMC cancer · 2016*
  - via `llm_topic:GSTM3 rs1799735`
- `PMID:42634682` **[NEW]** — **Severe Pulmonary Differentiation Syndrome Despite Corticosteroid Prophylaxis in Acute Promyelocytic Leukemia: Clinical Improvement With Pulse Methylprednisolone Therapy and High-Flow Nasal Cannula.** — *Cureus · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42629042` **[NEW]** — **Retinoic acid priming enhances myogenesis of bovine muscle stem cells for cultivated meat production by modulating mitochondrial function.** — *Food research international (Ottawa, Ont.) · 2026*
  - via `llm_topic:all-trans retinoic acid`
- `PMID:42621781` **[NEW]** — **METTL3-mediated m6A modification of circMtmr7 contributes to paclitaxel-induced peripheral neuropathy in the dorsal horn.** — *The Journal of physiology · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`
- `PMID:42609802` **[NEW]** — **The Ethanol-Insoluble Low-Molecular-Weight Fraction LEP-4 Derived From Lentinula edodes Mycelia Extract Attenuates Oxaliplatin-Evoked Allodynia in Mice.** — *Advances in pharmacological and pharmaceutical sciences · 2026*
  - via `llm_topic:chemotherapy-induced peripheral neuropathy CIPN`

</details>

<sub>KG: 32 entities / 86 relations · 25 references</sub>

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

#### Phase 6 — open search, abstracts

**Genes surfaced:** SLC28A3, GSTP1

The severe cardiotoxicity observed after doxorubicin treatment in a pediatric lymphoma patient may be influenced by genetic variants such as SLC28A3 (rs7853758) and GSTP1 (rs1695). These genes are associated with the transport and metabolism of doxorubicin, respectively. Variants in these genes could alter drug handling and increase susceptibility to cardiotoxicity. However, due to limited evidence and ambiguous clinical significance, further research is needed to establish definitive associations. For patient safety, genetic screening for SLC28A3 and GSTP1 variants might be considered alongside monitoring cardiac function during treatment. Alternative agents or dose adjustments could also be explored based on individual genetic profiles.

**Search topics the model chose:** `doxorubicin cardiotoxicity SLC28A3`; `GSTP1 doxorubicin toxicity`

<details><summary>Papers retrieved</summary>

- `PMID:42246857` **[NEW]** — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:42176227` **[NEW]** — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:41864056` **[NEW]** — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `llm_topic:GSTP1 doxorubicin toxicity`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` **[NEW]** — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635325` **[NEW]** — **Genetic Markers of Early Skeletal Muscle Loss in Adolescent and Young Adult Cancer Patients Treated with Anthracyclines.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42633171` **[NEW]** — **Disseminated intravascular coagulation in chimeric antigen receptor T-cell therapy: a 6-year nationwide analysis of clinical outcomes and health care resource utilization in patients with hematologic malignancies.** — *Research and practice in thrombosis and haemostasis · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42635460` **[NEW]** — **Clinical Assessment of Smokers with Persistent Dyspnoea but Unremarkable Spirometry: The Added Value of Diffusing Capacity for Carbon Monoxide.** — *COPD · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42635141` **[NEW]** — **Undetected Heart Failure in Cardiology: Prevalence, Characteristics, and Outcome.** — *European journal of preventive cardiology · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42633868` **[NEW]** — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` **[NEW]** — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` **[NEW]** — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` **[NEW]** — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:33274195` **[NEW]** — **Anthracycline-Induced Cardiotoxicity in Breast Cancer Patients from Southern Sri Lanka: An Echocardiographic Analysis.** — *BioMed research international · 2020*
  - via `llm_topic:early-onset chronic progressive cardiotoxicity`

</details>

<sub>KG: 18 entities / 68 relations · 27 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** SLC28A3, GSTP1

The severe cardiotoxicity observed after doxorubicin treatment in a pediatric lymphoma patient may be influenced by genetic variants such as SLC28A3 (rs7853758) and GSTP1 (rs1695). These genes are associated with the transport and metabolism of doxorubicin, respectively. Variants in these genes could alter drug handling and increase susceptibility to cardiotoxicity. However, due to limited evidence and ambiguous clinical significance, further research is needed to establish definitive associations. For patient safety, genetic screening for SLC28A3 and GSTP1 variants might be considered alongside monitoring cardiac function during treatment. Alternative agents or dose adjustments could also be explored based on individual genetic profiles.

**Search topics the model chose:** `doxorubicin cardiotoxicity SLC28A3`; `GSTP1 doxorubicin toxicity`

<details><summary>Papers retrieved</summary>

- `PMID:42246857` **[NEW]** — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:42176227` **[NEW]** — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:doxorubicin cardiotoxicity SLC28A3`
- `PMID:41864056` **[NEW]** — **Immunohistochemical biomarkers to predict adjuvant chemotherapy response in patients with early breast cancer in the MATADOR trial (BOOG 2005-02).** — *Breast (Edinburgh, Scotland) · 2026*
  - via `llm_topic:GSTP1 doxorubicin toxicity`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` **[NEW]** — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635325` **[NEW]** — **Genetic Markers of Early Skeletal Muscle Loss in Adolescent and Young Adult Cancer Patients Treated with Anthracyclines.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42633171` **[NEW]** — **Disseminated intravascular coagulation in chimeric antigen receptor T-cell therapy: a 6-year nationwide analysis of clinical outcomes and health care resource utilization in patients with hematologic malignancies.** — *Research and practice in thrombosis and haemostasis · 2026*
  - via `llm_topic:pediatric lymphoma`
- `PMID:42635460` **[NEW]** — **Clinical Assessment of Smokers with Persistent Dyspnoea but Unremarkable Spirometry: The Added Value of Diffusing Capacity for Carbon Monoxide.** — *COPD · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42635141` **[NEW]** — **Undetected Heart Failure in Cardiology: Prevalence, Characteristics, and Outcome.** — *European journal of preventive cardiology · 2026*
  - via `llm_topic:shortness of breath`
- `PMID:42633868` **[NEW]** — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` **[NEW]** — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` **[NEW]** — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` **[NEW]** — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:33274195` **[NEW]** — **Anthracycline-Induced Cardiotoxicity in Breast Cancer Patients from Southern Sri Lanka: An Echocardiographic Analysis.** — *BioMed research international · 2020*
  - via `llm_topic:early-onset chronic progressive cardiotoxicity`

</details>

<sub>KG: 18 entities / 68 relations · 27 references</sub>

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

#### Phase 6 — open search, abstracts

**Genes surfaced:** SLC28A3 (rs7853758), RARG (rs2229774)

The genes/variants SLC28A3 (rs7853758) and RARG (rs2229774) are implicated in anthracycline-induced cardiotoxicity, with moderate evidence suggesting their predictive value. The biological mechanism likely involves altered nucleoside transport or receptor activity affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants could help identify high-risk patients who may benefit from dose adjustments or alternative agents to mitigate cardiotoxicity risk.

**Search topics the model chose:** `anthracycline cardiotoxicity SLC28A3`; `RARG cardiotoxicity neoplasms`; `GSTP1 rs1695 cardiotoxicity`; `RARG rs2229774 cancer`

<details><summary>Papers retrieved</summary>

- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:anthracycline cardiotoxicity SLC28A3`
- `PMID:42279262` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774 cancer`
- `PMID:42246857` **[NEW]** — **Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogenetics and survival among breast cancer patients in Zimbabwe.** — *South African medical journal = Suid-Afrikaanse tydskrif vir geneeskunde · 2026*
  - via `llm_topic:RARG cardiotoxicity neoplasms`
- `PMID:33425072` **[NEW]** — **Genetic Variability of Antioxidative Mechanisms and Cardiotoxicity after Adjuvant Radiotherapy in HER2-Positive Breast Cancer Patients.** — *Disease markers · 2020*
  - via `llm_topic:GSTP1 rs1695 cardiotoxicity`
- `PMID:42618256` **[NEW]** — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `llm_topic:Anthracycline-induced cardiotoxicity`
- `PMID:42615446` **[NEW]** — **A Simple Clinical Risk Score to Improve Prediction of Anthracycline-Induced Cardiotoxicity.** — *JACC. CardioOncology · 2026*
  - via `llm_topic:Anthracycline-induced cardiotoxicity`
- `PMID:41537578` **[NEW]** — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:40413218` **[NEW]** — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42353582` **[NEW]** — **Oxidative DNA Damage as an Integrative Marker of Redox Dysfunction Associated with Doxorubicin-Induced Cardiotoxicity in Pediatric Leukemia.** — *Current issues in molecular biology · 2026*
  - via `llm_topic:CBR3 rs1056892`
- `PMID:42527396` **[NEW]** — **Effects of CYP3A4, CYP3A5, and ABCB1 genetic variants on tacrolimus metabolism during the early period after kidney transplantation.** — *The pharmacogenomics journal · 2026*
  - via `llm_topic:ABCB1 rs1045642`
- `PMID:41083112` **[NEW]** — **Associations between host efflux pump gene polymorphisms (ABCB1, ABCC1, ABCG2) and drug-resistant tuberculosis in a Chinese cohort.** — *Gene · 2025*
  - via `llm_topic:ABCC2 rs8187710`

</details>

<sub>KG: 16 entities / 65 relations · 23 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** SLC28A3 (rs7853758), RARG (rs2229774), GSTP1 (rs1695)

The genes/variants SLC28A3 (rs7853758), RARG (rs2229774), and GSTP1 (rs1695) are implicated in anthracycline-induced cardiotoxicity. The biological mechanism likely involves altered transport, receptor activity, or detoxification pathways that affect cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help identify patients at higher risk of cardiotoxicity, enabling dose adjustments or the use of alternative agents to mitigate this adverse effect.

**Search topics the model chose:** `anthracycline cardiotoxicity SLC28A3`; `RARG anthracycline cardiotoxicity`; `GSTP1 osteosarcoma cardiotoxicity`; `RARG rs2229774 cancer`

<details><summary>Papers retrieved</summary>

- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:anthracycline cardiotoxicity SLC28A3`
- `PMID:42279262/PMC13255899` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774 cancer+pmc_xml`
- `PMID:42279262` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG anthracycline cardiotoxicity`
- `PMID:36536332` **[NEW]** — **Pharmacogenetics of chemotherapy treatment response and -toxicities in patients with osteosarcoma: a systematic review.** — *BMC cancer · 2022*
  - via `llm_topic:GSTP1 osteosarcoma cardiotoxicity`
- `PMID:42618256` **[NEW]** — **Comparative analysis of the cardiotoxicity induced by doxorubicin and epirubicin and exploratory investigations of clinical parameters indicating the cardiotoxicity in healthy dogs.** — *The Journal of veterinary medical science · 2026*
  - via `llm_topic:anthracycline-induced cardiotoxicity`
- `PMID:42615446` **[NEW]** — **A Simple Clinical Risk Score to Improve Prediction of Anthracycline-Induced Cardiotoxicity.** — *JACC. CardioOncology · 2026*
  - via `llm_topic:anthracycline-induced cardiotoxicity`
- `PMID:41537578` **[NEW]** — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:40413218` **[NEW]** — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42353582` **[NEW]** — **Oxidative DNA Damage as an Integrative Marker of Redox Dysfunction Associated with Doxorubicin-Induced Cardiotoxicity in Pediatric Leukemia.** — *Current issues in molecular biology · 2026*
  - via `llm_topic:CBR3 rs1056892`
- `PMID:42527396` **[NEW]** — **Effects of CYP3A4, CYP3A5, and ABCB1 genetic variants on tacrolimus metabolism during the early period after kidney transplantation.** — *The pharmacogenomics journal · 2026*
  - via `llm_topic:ABCB1 rs1045642`
- `PMID:41083112` **[NEW]** — **Associations between host efflux pump gene polymorphisms (ABCB1, ABCC1, ABCG2) and drug-resistant tuberculosis in a Chinese cohort.** — *Gene · 2025*
  - via `llm_topic:ABCC2 rs8187710`
- `PMID:42594534` **[NEW]** — **Feedback activation of MAPK-ERK1/2 signaling causes resistance to trastuzumab-deruxtecan in endometrial cancers.** — *Gynecologic oncology · 2026*
  - via `llm_topic:HER2-targeted antibodies`
- `PMID:42591779` **[NEW]** — **Sequential HER2-targeted antibody-drug conjugate therapy for acquired resistance in a 55-year-old male kidney transplant recipient with metastatic urothelial carcinoma: a case report.** — *Translational cancer research · 2026*
  - via `llm_topic:HER2-targeted antibodies`

</details>

<sub>KG: 16 entities / 65 relations · 25 references</sub>

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

#### Phase 6 — open search, abstracts

**Genes surfaced:** CYP2D6*4

The adverse reaction observed in your son is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of doxorubicin, exacerbating cardiotoxicity. The biological mechanism involves altered drug metabolism leading to increased toxicity. For patient safety, pre-treatment genetic screening for CYP2D6 variants is recommended to identify high-risk patients who might benefit from dose adjustments or alternative treatments with lower cardiotoxic potential.

**Search topics the model chose:** `doxorubicin cardiotoxicity CYP2D6`; `SLC28A3 heart failure`; `GSTP1 neoplasm risk`; `SLC28A3 doxorubicin heart failure`

<details><summary>Papers retrieved</summary>

- `PMID:38196322` **[NEW]** — **Clinical significance of coadministration of moderate to strong CYP enzyme inhibitors with doxorubicin in breast cancer patients receiving AC chemotherapy.** — *Journal of oncology pharmacy practice : official publication of the International Society of Oncology Pharmacy Practitioners · 2025*
  - via `llm_topic:doxorubicin cardiotoxicity CYP2D6`
- `PMID:27197003` **[NEW]** — **Recommendations for genetic testing to reduce the incidence of anthracycline-induced cardiotoxicity.** — *British journal of clinical pharmacology · 2016*
  - via `llm_topic:SLC28A3 doxorubicin heart failure`
- `PMID:33900042` **[NEW]** — **Pharmacogenetic testing to guide therapeutic decision-making and improve outcomes for children undergoing anthracycline-based chemotherapy.** — *Basic & clinical pharmacology & toxicology · 2022*
  - via `llm_topic:SLC28A3 heart failure`
- `PMID:42530245` **[NEW]** — **Transcriptomic and Single-Cell Analyses Reveal a Prognostic Mitochondria- and Immunity-Related Risk Signature in Osteosarcoma.** — *Frontiers in bioscience (Landmark edition) · 2026*
  - via `llm_topic:GSTP1 neoplasm risk`
- `PMID:42217759` **[NEW]** — **Antiplatelet activity of novel aminoestrogens: R-β-mefenetame as a candidate for safer estrogen-based therapies.** — *The Journal of steroid biochemistry and molecular biology · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:41532000` **[NEW]** — **Personalizing Treatment for Acute Alcoholic Hallucinosis: Clinical Utility of Integrated Pharmacogenetic Testing, Metabolic Phenotyping, and microRNA Biomarkers.** — *Psychopharmacology bulletin · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` **[NEW]** — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635550` **[NEW]** — **Clinical validation of the nursing diagnosis of inadequate nutritional intake in children with cancer.** — *International journal of nursing knowledge · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635508` **[NEW]** — **Eating Experiences During Cancer Treatment in Adolescents and Young Adults: A Systematic Literature Review and Meta-Synthesis.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635410` **[NEW]** — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:heart failure`
- `PMID:42635407` **[NEW]** — **MxA expression in systemic lupus erythematosus -associated myocarditis indicates type I interferon pathway activation.** — *Immunological medicine · 2026*
  - via `llm_topic:heart failure`
- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` **[NEW]** — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` **[NEW]** — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42634505` **[NEW]** — **Innovative Insights into Osteosarcoma: Unraveling the Role of LncRNAs, miRNAs, and CircRNAs in Tumorigenesis and Therapeutic Resistance.** — *Current gene therapy · 2026*
  - via `llm_topic:osteosarcoma`
- `PMID:42634348` **[NEW]** — **Development of a Prognostic Model Based on SCISSOR+ Osteoblastic Osteosarcoma Cell-Associated Genes.** — *Current medicinal chemistry · 2026*
  - via `llm_topic:osteosarcoma`

</details>

<sub>KG: 15 entities / 78 relations · 29 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** CYP2D6*4

The adverse reaction observed in your son is likely influenced by the CYP2D6*4 genetic variant, which reduces CYP2D6 enzyme activity and may lead to higher levels of doxorubicin, exacerbating cardiotoxicity. The biological mechanism involves altered drug metabolism leading to increased toxicity. For patient safety, pre-treatment genetic screening for CYP2D6 variants is recommended to identify high-risk patients who might benefit from dose adjustments or alternative treatments with lower cardiotoxic potential.

**Search topics the model chose:** `doxorubicin cardiotoxicity CYP2D6`; `SLC28A3 heart failure`; `GSTP1 neoplasm risk`; `SLC28A3 doxorubicin heart failure`

<details><summary>Papers retrieved</summary>

- `PMID:38196322` **[NEW]** — **Clinical significance of coadministration of moderate to strong CYP enzyme inhibitors with doxorubicin in breast cancer patients receiving AC chemotherapy.** — *Journal of oncology pharmacy practice : official publication of the International Society of Oncology Pharmacy Practitioners · 2025*
  - via `llm_topic:doxorubicin cardiotoxicity CYP2D6`
- `PMID:27197003` **[NEW]** — **Recommendations for genetic testing to reduce the incidence of anthracycline-induced cardiotoxicity.** — *British journal of clinical pharmacology · 2016*
  - via `llm_topic:SLC28A3 doxorubicin heart failure`
- `PMID:33900042` **[NEW]** — **Pharmacogenetic testing to guide therapeutic decision-making and improve outcomes for children undergoing anthracycline-based chemotherapy.** — *Basic & clinical pharmacology & toxicology · 2022*
  - via `llm_topic:SLC28A3 heart failure`
- `PMID:42530245` **[NEW]** — **Transcriptomic and Single-Cell Analyses Reveal a Prognostic Mitochondria- and Immunity-Related Risk Signature in Osteosarcoma.** — *Frontiers in bioscience (Landmark edition) · 2026*
  - via `llm_topic:GSTP1 neoplasm risk`
- `PMID:42217759` **[NEW]** — **Antiplatelet activity of novel aminoestrogens: R-β-mefenetame as a candidate for safer estrogen-based therapies.** — *The Journal of steroid biochemistry and molecular biology · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:41532000` **[NEW]** — **Personalizing Treatment for Acute Alcoholic Hallucinosis: Clinical Utility of Integrated Pharmacogenetic Testing, Metabolic Phenotyping, and microRNA Biomarkers.** — *Psychopharmacology bulletin · 2026*
  - via `llm_topic:CYP2D6*4`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` **[NEW]** — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635550` **[NEW]** — **Clinical validation of the nursing diagnosis of inadequate nutritional intake in children with cancer.** — *International journal of nursing knowledge · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635508` **[NEW]** — **Eating Experiences During Cancer Treatment in Adolescents and Young Adults: A Systematic Literature Review and Meta-Synthesis.** — *Journal of adolescent and young adult oncology · 2026*
  - via `llm_topic:Neoplasm`
- `PMID:42635410` **[NEW]** — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:heart failure`
- `PMID:42635407` **[NEW]** — **MxA expression in systemic lupus erythematosus -associated myocarditis indicates type I interferon pathway activation.** — *Immunological medicine · 2026*
  - via `llm_topic:heart failure`
- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:41537578` **[NEW]** — **Cardioprotective SNPs in SLC28A3 and lncRNA SLC28A3-AS1 result in transcriptional changes and alternative splicing to reduce doxorubicin cytotoxicity.** — *Human molecular genetics · 2026*
  - via `llm_topic:SLC28A3 rs7853758`
- `PMID:42599307` **[NEW]** — **Genetic susceptibility to mercury in the amazon: A cross-sectional approach to snps analyses in exposed riverine populations.** — *Genetics and molecular biology · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42558143` **[NEW]** — **Association of oxidative stress-related gst gene polymorphisms with periodontitis susceptibility: A systematic review and meta-analysis.** — *Journal of advanced periodontology & implant dentistry · 2026*
  - via `llm_topic:GSTP1 rs1695`
- `PMID:42279262` **[NEW]** — **Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical Implications Across Solid and Hematological Malignancies.** — *Cancers · 2026*
  - via `llm_topic:RARG rs2229774`
- `PMID:40413218` **[NEW]** — **Influence of genetic biomarkers on cardiac diseases in childhood cancer survivors: a systematic review.** — *The pharmacogenomics journal · 2025*
  - via `llm_topic:RARG rs2229774`
- `PMID:42634505` **[NEW]** — **Innovative Insights into Osteosarcoma: Unraveling the Role of LncRNAs, miRNAs, and CircRNAs in Tumorigenesis and Therapeutic Resistance.** — *Current gene therapy · 2026*
  - via `llm_topic:osteosarcoma`
- `PMID:42634348` **[NEW]** — **Development of a Prognostic Model Based on SCISSOR+ Osteoblastic Osteosarcoma Cell-Associated Genes.** — *Current medicinal chemistry · 2026*
  - via `llm_topic:osteosarcoma`

</details>

<sub>KG: 15 entities / 78 relations · 29 references</sub>

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

#### Phase 6 — open search, abstracts

**Genes surfaced:** GSTM1

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by her GSTM1 genotype, as functional studies suggest that GSTM1 may play a role in anthracycline-induced cardiotoxicity. The biological mechanism involves the potential modulation of doxorubicin metabolism and detoxification pathways by GSTM1, which could exacerbate or mitigate cardiac strain and heart muscle damage. For drug discovery and patient safety, pre-treatment screening for GSTM1 status may help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or consideration of alternative agents to minimize cardiac injury.

**Search topics the model chose:** `adriamycin cardiotoxicity gstm1`; `doxorubicin heart damage genetics`; `anthracycline toxicity slc28a3`

<details><summary>Papers retrieved</summary>

- `PMID:38510289` **[NEW]** — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `llm_topic:adriamycin cardiotoxicity gstm1`
- `PMID:42559407` **[NEW]** — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `llm_topic:doxorubicin heart damage genetics`
- `PMID:42176227` **[NEW]** — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:anthracycline toxicity slc28a3`
- `PMID:42635315` **[NEW]** — **Baseline podocyte-associated state and persistent cell-matrix transcriptional programs are associated with BALB/c substrain differences in adriamycin nephropathy.** — *Animal models and experimental medicine · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42635410` **[NEW]** — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42634934` **[NEW]** — **Multimodal Framework of Left Heart-Pulmonary Vascular Remodeling Underlying Right Ventricular Failure in PH-HFpEF.** — *Circulation. Heart failure · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42633868` **[NEW]** — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` **[NEW]** — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42577562` **[NEW]** — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42561509` **[NEW]** — **Loki Zupa alleviates type 2-high acute asthma airway inflammation by regulating the glutathione metabolism-ferroptosis axis.** — *Phytomedicine : international journal of phytotherapy and phytopharmacology · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42522562` **[NEW]** — **Meta-Analysis of Genome-Wide Association Studies of Doxorubicin-Induced Arrhythmia Identifies MMP16 and KCTD15 as Risk Loci.** — *Circulation. Genomic and precision medicine · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42522188` **[NEW]** — **Inhibition of late sodium current prevents pathological hyperactivation of calcium/calmodulin-dependent protein kinase IIδ in a murine model of acute doxorubicin-related cardiotoxicity.** — *British journal of pharmacology · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42520516` **[NEW]** — **Machine learning, WGCNA and molecular docking identify SLC transporter genes as biomarkers and drug targets in Helicobacter pylori-associated carcinogenesis.** — *Bioorganic chemistry · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42634868` **[NEW]** — **Prunetin Attenuates Dexamethasone-Induced Pancreatic β-Cell Apoptosis: Modulation of Oxidative Stress and MAPK Signaling but Not Phosphorylated C-Abl Levels.** — *Cell biochemistry and function · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42631444` **[NEW]** — **Low-Cost Nucleic-Acid-Based Radial Flow Assay for the Detection of GSTP1 Promoter DNA Methylation in Prostate Cancer.** — *ACS applied bio materials · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42555353` **[NEW]** — **ID2 Unlocks retinoic acid signaling to promote eosinophil maturation by antagonizing TCF3.** — *Cell reports · 2026*
  - via `llm_topic:RARG`
- `PMID:42434795` **[NEW]** — **Rh-Induced Oxygen Vacancies in a PdRh/SnO2 Heterointerface for Enhanced MEMS Hydrogen Detection.** — *ACS sensors · 2026*
  - via `llm_topic:RARG`

</details>

<sub>KG: 13 entities / 65 relations · 27 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** GSTM1, SLC28A3

The adverse cardiac effects observed in your daughter after Adriamycin treatment are likely influenced by genetic factors such as GSTM1, which is a risk factor for doxorubicin-induced cardiotoxicity. The biological mechanism involves the role of transporters like SLC28A3 and detoxification enzymes like those encoded by GSTM1, which can affect drug uptake, distribution, metabolism, and excretion, thereby modulating the extent of cardiac damage caused by Adriamycin. For drug discovery and patient safety, pre-treatment genetic screening for variants in genes such as GSTM1 and SLC28A3 could help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or the use of alternative agents to mitigate adverse effects.

**Search topics the model chose:** `adriamycin cardiotoxicity gstm1`; `doxorubicin heart damage genetics`; `anthracycline toxicity slc28a3`

<details><summary>Papers retrieved</summary>

- `PMID:38510289/PMC10950437` **[NEW]** — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `llm_topic:adriamycin cardiotoxicity gstm1+pmc_xml`
- `PMID:42559407/PMC13440645` **[NEW]** — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `llm_topic:doxorubicin heart damage genetics+pmc_xml`
- `PMID:38510289` **[NEW]** — **Functional Validation of Doxorubicin-Induced Cardiotoxicity-Related Genes.** — *JACC. CardioOncology · 2024*
  - via `llm_topic:adriamycin cardiotoxicity gstm1`
- `PMID:42559407` **[NEW]** — **CCR2 deficiency protects against doxorubicin-induced cardiac dysfunction through enhanced IL12B-dependent autophagy.** — *Theranostics · 2026*
  - via `llm_topic:doxorubicin heart damage genetics`
- `PMID:42176227` **[NEW]** — **Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharmacogenomic Modifiers, and Translational Strategies.** — *Cardiovascular toxicology · 2026*
  - via `llm_topic:anthracycline toxicity slc28a3`
- `PMID:42635315` **[NEW]** — **Baseline podocyte-associated state and persistent cell-matrix transcriptional programs are associated with BALB/c substrain differences in adriamycin nephropathy.** — *Animal models and experimental medicine · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:Adriamycin`
- `PMID:42635410` **[NEW]** — **Impact of systemic inflammation on exercise haemodynamics in unexplained dyspnoea and heart failure with preserved ejection fraction.** — *Acta cardiologica · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42634934` **[NEW]** — **Multimodal Framework of Left Heart-Pulmonary Vascular Remodeling Underlying Right Ventricular Failure in PH-HFpEF.** — *Circulation. Heart failure · 2026*
  - via `llm_topic:cardiac strain`
- `PMID:42633868` **[NEW]** — **RGS6 drives myocyte loss in the diabetic heart via a KLF4/miR-30e/CaMKII-dependent mechanism.** — *Molecular and cellular endocrinology · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42625194` **[NEW]** — **Pirfenidone restores metabolic hormones and cardiac autophagy via p-AMPK in MASH.** — *Journal of translational medicine · 2026*
  - via `llm_topic:heart muscle damage`
- `PMID:42577562` **[NEW]** — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42561509` **[NEW]** — **Loki Zupa alleviates type 2-high acute asthma airway inflammation by regulating the glutathione metabolism-ferroptosis axis.** — *Phytomedicine : international journal of phytotherapy and phytopharmacology · 2026*
  - via `llm_topic:GSTM1`
- `PMID:42522562` **[NEW]** — **Meta-Analysis of Genome-Wide Association Studies of Doxorubicin-Induced Arrhythmia Identifies MMP16 and KCTD15 as Risk Loci.** — *Circulation. Genomic and precision medicine · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42522188` **[NEW]** — **Inhibition of late sodium current prevents pathological hyperactivation of calcium/calmodulin-dependent protein kinase IIδ in a murine model of acute doxorubicin-related cardiotoxicity.** — *British journal of pharmacology · 2026*
  - via `llm_topic:doxorubicin-related Cardiotoxicity`
- `PMID:42549829` **[NEW]** — **Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Chinese early‑stage breast cancer patients: a candidate gene study.** — *Future oncology (London, England) · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42520516` **[NEW]** — **Machine learning, WGCNA and molecular docking identify SLC transporter genes as biomarkers and drug targets in Helicobacter pylori-associated carcinogenesis.** — *Bioorganic chemistry · 2026*
  - via `llm_topic:SLC28A3`
- `PMID:42634868` **[NEW]** — **Prunetin Attenuates Dexamethasone-Induced Pancreatic β-Cell Apoptosis: Modulation of Oxidative Stress and MAPK Signaling but Not Phosphorylated C-Abl Levels.** — *Cell biochemistry and function · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42631444` **[NEW]** — **Low-Cost Nucleic-Acid-Based Radial Flow Assay for the Detection of GSTP1 Promoter DNA Methylation in Prostate Cancer.** — *ACS applied bio materials · 2026*
  - via `llm_topic:GSTP1`
- `PMID:42555353` **[NEW]** — **ID2 Unlocks retinoic acid signaling to promote eosinophil maturation by antagonizing TCF3.** — *Cell reports · 2026*
  - via `llm_topic:RARG`
- `PMID:42434795` **[NEW]** — **Rh-Induced Oxygen Vacancies in a PdRh/SnO2 Heterointerface for Enhanced MEMS Hydrogen Detection.** — *ACS sensors · 2026*
  - via `llm_topic:RARG`

</details>

<sub>KG: 13 entities / 65 relations · 29 references</sub>

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

#### Phase 6 — open search, abstracts

**Genes surfaced:** ERCC1 (rs11615), CYBA (rs4673)

Doxorubicin-induced mucositis is influenced by genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing the risk of developing this adverse reaction. The biological mechanism likely involves these genes affecting DNA repair processes or oxidative stress responses, thereby altering cellular sensitivity to doxorubicin-induced damage. For drug discovery and patient safety, pre-treatment genetic screening for these variants could help identify patients at higher risk, allowing for dose adjustments or consideration of alternative agents with a lower mucositis risk profile.

**Search topics the model chose:** `anthracycline mucositis genetics`; `genetic predisposition mucositis`

<details><summary>Papers retrieved</summary>

- `PMID:42614547` **[NEW]** — **Shared genetic architecture between Crohn's disease and IgA nephropathy: implications for a gut-immune-kidney axis.** — *Frontiers in immunology · 2026*
  - via `llm_topic:genetic predisposition mucositis`
- `PMID:42579038` **[NEW]** — **Influenza A(H1N1) triggered atypical hemolytic uremic syndrome in a child with homozygous CD46 variant successfully treated with ravulizumab: a case report.** — *CEN case reports · 2026*
  - via `llm_topic:genetic predisposition mucositis`
- `PMID:41782384` **[NEW]** — **Piezo1 Channel Mediates Mechanically Programmable Drug Delivery to Potentiate Intravesical Chemotherapy.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:40243204` **[NEW]** — **Tritrichomonas muris sensitizes the intestinal epithelium to doxorubicin-induced apoptosis.** — *American journal of physiology. Gastrointestinal and liver physiology · 2025*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` **[NEW]** — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635616` **[NEW]** — **When Surgical Intervention Becomes a Risk: Severe Drug-Induced Gingival Overgrowth and Clinical Decision-Making in Alpers-Huttenlocher Syndrome.** — *Special care in dentistry : official publication of the American Association of Hospital Dentists, the Academy of Dentistry for the Handicapped, and the American Society for Geriatric Dentistry · 2026*
  - via `llm_topic:mucositis`
- `PMID:42635600` **[NEW]** — **BRD4 contributes to the cytokine-induced acquisition of an IL-13RA2-positive inflammatory fibroblast phenotype.** — *Journal of Crohn's & colitis · 2026*
  - via `llm_topic:mucositis`
- `PMID:42123691` **[NEW]** — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` **[NEW]** — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42548792` **[NEW]** — **Pharmacogenomic variation and chemotherapy-related toxicity profiles in pediatric patients with cancer in Tanzania: a cross-sectional study.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:CYBA rs4673`
- `PMID:39960941` **[NEW]** — **Association between rs4673 and blood pressure response to acute saline infusion in Chinese population.** — *Medicine · 2025*
  - via `llm_topic:CYBA rs4673`
- `PMID:42635220` **[NEW]** — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` **[NEW]** — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`

</details>

<sub>KG: 11 entities / 26 relations · 20 references</sub>

#### Phase 7 — open search + full text

**Genes surfaced:** ERCC1, CYBA

Doxorubicin-induced mucositis is influenced by genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response. These variants likely affect DNA repair mechanisms or oxidative stress responses, thereby increasing susceptibility to mucosal damage from doxorubicin. For patient safety, pre-treatment screening for these genetic markers could help identify individuals at higher risk of developing mucositis, allowing for dose adjustments or alternative chemotherapy agents to be considered.

**Search topics the model chose:** `anthracycline mucositis genetics`; `genetic predisposition mucositis`

<details><summary>Papers retrieved</summary>

- `PMID:42614547/PMC13481795` **[NEW]** — **Shared genetic architecture between Crohn's disease and IgA nephropathy: implications for a gut-immune-kidney axis.** — *Frontiers in immunology · 2026*
  - via `llm_topic:genetic predisposition mucositis+pmc_xml`
- `PMID:42579038` **[NEW]** — **Influenza A(H1N1) triggered atypical hemolytic uremic syndrome in a child with homozygous CD46 variant successfully treated with ravulizumab: a case report.** — *CEN case reports · 2026*
  - via `llm_topic:genetic predisposition mucositis`
- `PMID:41782384` **[NEW]** — **Piezo1 Channel Mediates Mechanically Programmable Drug Delivery to Potentiate Intravesical Chemotherapy.** — *Advanced science (Weinheim, Baden-Wurttemberg, Germany) · 2026*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:40243204` **[NEW]** — **Tritrichomonas muris sensitizes the intestinal epithelium to doxorubicin-induced apoptosis.** — *American journal of physiology. Gastrointestinal and liver physiology · 2025*
  - via `llm_topic:anthracycline mucositis genetics`
- `PMID:42634559` **[NEW]** — **Synergistic Nanomedicine-Microcarrier for Transarterial Chemoembolization Against Hepatocellular Carcinoma.** — *Current drug delivery · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42633489` **[NEW]** — **Zn-Ni metal-organic framework nanosheets@graphene oxide nanocomposite: A promising voltammetric platform for sensitive determination of doxorubicin.** — *ADMET & DMPK · 2026*
  - via `llm_topic:doxorubicin`
- `PMID:42635616` **[NEW]** — **When Surgical Intervention Becomes a Risk: Severe Drug-Induced Gingival Overgrowth and Clinical Decision-Making in Alpers-Huttenlocher Syndrome.** — *Special care in dentistry : official publication of the American Association of Hospital Dentists, the Academy of Dentistry for the Handicapped, and the American Society for Geriatric Dentistry · 2026*
  - via `llm_topic:mucositis`
- `PMID:42635600` **[NEW]** — **BRD4 contributes to the cytokine-induced acquisition of an IL-13RA2-positive inflammatory fibroblast phenotype.** — *Journal of Crohn's & colitis · 2026*
  - via `llm_topic:mucositis`
- `PMID:42123691` **[NEW]** — **Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemotherapy in Patients with Gastric and Gastroesophageal Junction Adenocarcinoma.** — *International journal of molecular sciences · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:41786212` **[NEW]** — **Investigating Genetic Risk to Oxaliplatin-Induced Sinusoidal Obstruction Syndrome in Colorectal Cancer Through Routinely Available Next-Generation Sequencing Data.** — *Modern pathology : an official journal of the United States and Canadian Academy of Pathology, Inc · 2026*
  - via `llm_topic:ERCC1 rs11615`
- `PMID:42548792` **[NEW]** — **Pharmacogenomic variation and chemotherapy-related toxicity profiles in pediatric patients with cancer in Tanzania: a cross-sectional study.** — *Frontiers in pharmacology · 2026*
  - via `llm_topic:CYBA rs4673`
- `PMID:39960941` **[NEW]** — **Association between rs4673 and blood pressure response to acute saline infusion in Chinese population.** — *Medicine · 2025*
  - via `llm_topic:CYBA rs4673`
- `PMID:42635220` **[NEW]** — **Modelling time-varying genetic effects on binary disease risk via functional Mendelian randomization.** — *Bioinformatics (Oxford, England) · 2026*
  - via `llm_topic:genetic predisposition`
- `PMID:42634522` **[NEW]** — **Descriptive Analysis of Genetic Variants in Individuals Without a Clinical Diagnosis of Alzheimer's Disease in a Population from Southwestern Colombia.** — *Current Alzheimer research · 2026*
  - via `llm_topic:genetic predisposition`

</details>

<sub>KG: 11 entities / 26 relations · 20 references</sub>

---

