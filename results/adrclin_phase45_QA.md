# ADR clinical QA — Phase 4 & Phase 5 results

Complete run over all 10 ADR questions with the new retrieval phases. These are **new results only** — no answers from earlier ClinPGx-only (phase 3) runs are reused.

| Phase | Configuration | What it retrieves |
|---|---|---|
| **Phase 4** | `AMG_KB_SOURCE=pharmgkb+pubmed` | ClinPGx tables, then PubMed — the exact PMIDs `relationships.tsv` cites for the retrieved gene–drug pairs (`via: clinpgx_citation`), topped up by a live search. Abstracts only. |
| **Phase 5** | `+ AMG_PUBMED_FULLTEXT=1` | Same, plus PubMed abstracts used at the reasoning stage upgraded to PMC full text (JATS XML; OA PDF fallback), capped at `AMG_FULLTEXT_MAX_CHARS`. |

Every retrieved item is referenced with a stable id (`ClinPGx:GENE/variant:Llevel`, `PMID:xxx`, `PMID:xxx/PMCxxx`) and persisted per question in the `references` / `evidence_log` fields of the results JSONL.

## Coverage and retrieval statistics

| # | Question | P4 | P5 | Refs (P5) | PubMed | Full text | KG entities |
|---|---|---|---|---|---|---|---|
| Q1 | I am a child receiving cisplatin for cancer and developed hearin... | YES | YES | 22 | 13 | 0 | 31 |
| Q2 | What genes or variants have been linked to cisplatin ototoxicity... | YES | YES | 25 | 17 | 0 | 28 |
| Q3 | My daughter carries a TPMT variant and is on cisplatin for her N... | YES | YES | 25 | 15 | 0 | 29 |
| Q4 | After several cycles of Platinol, my child has permanent inner e... | YES | YES | 24 | 14 | 1 | 33 |
| Q5 | Can cisplatin cause a genetic predisposition to peripheral neuro... | YES | YES | 22 | 15 | 0 | 32 |
| Q6 | After receiving doxorubicin for pediatric lymphoma, my child dev... | YES | YES | 22 | 13 | 0 | 18 |
| Q7 | Which pharmacogenomic biomarkers predict anthracycline-induced c... | YES | YES | 27 | 15 | 0 | 16 |
| Q8 | My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm ... | YES | YES | 20 | 13 | 0 | 15 |
| Q9 | My daughter took Adriamycin and now has cardiac strain and heart... | YES | YES | 21 | 13 | 0 | 16 |
| Q10 | Could doxorubicin cause a genetic predisposition to mucositis?... | YES | YES | 24 | 15 | 1 | 14 |
| | **Total (phase 5)** | | | **232** | **143** | **2** | |

**How PubMed evidence was reached** (retrieval events, both phases):

| Route | Events | Meaning |
|---|---|---|
| `clinpgx_citation` | 360 | the PMID ClinPGx itself cites for the gene-drug pair (phase-4 verification) |
| `esearch` | 56 | live PubMed search on the query text (top-up when citations run short) |
| `clinpgx_citation+pmc_xml` | 2 | ClinPGx-cited PMID upgraded to PMC full text (phase 5) |

### Limitations of this run

- **Full text is scarce.** Phase 5 attempts a full-text upgrade for the top 2 PubMed items per question at the reasoning stage (at most 20 attempts here); only **2** succeeded. Most pharmacogenomics papers ClinPGx cites are older and not open-access in PMC, so retrieval falls back to abstracts rather than inventing content.
- **The live-search top-up is noisy.** When ClinPGx cites fewer PMIDs than the result cap, the remainder comes from an esearch on the raw question text; for long patient-style questions this sometimes returns off-topic recent papers. The ClinPGx-cited PMIDs (`via: clinpgx_citation`) are the reliable part of the phase-4 evidence.
- **Entity-level retrieval pulls unrelated drugs.** Each extracted entity is searched separately, which surfaces ClinPGx rows for other drugs (e.g. capecitabine/DPYD rows inside a cisplatin question). They are logged, so their influence stays auditable.

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** ACYP2, GSTM1

The genetic variants ACYP2 (rs1872328) and GSTM1 are implicated in cisplatin-induced ototoxicity, with stronger evidence supporting the role of rs1872328. The biological mechanism likely involves impaired cellular detoxification or increased sensitivity to cisplatin's cytotoxic effects due to these genetic variations. For drug discovery and patient safety, pre-treatment screening for ACYP2 (rs1872328) could help identify patients at higher risk of ototoxicity, potentially allowing dose adjustments or the use of alternative agents such as carboplatin, which has a lower incidence of this side effect.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:ACYP2/rs1872328:L3` — ACYP2 (rs1872328): PharmGKB evidence level 3 linking it to cisplatin-related Brain Neoplasms, Hearing Loss. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L3` — TPMT (TPMT*1): PharmGKB evidence level 3 linking it to cisplatin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MT-RNR1/rs267606617:L1A` — MT-RNR1 (rs267606617): PharmGKB evidence level 1A linking it to tobramycin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L1A` — TPMT (TPMT*1): PharmGKB evidence level 1A linking it to azathioprine-related Dose reduction. ClinPGx relationship: ambiguous.
- `ClinPGx:DPYD/rs17376848:L1A` — DPYD (rs17376848): PharmGKB evidence level 1A linking it to capecitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:DPYD/rs2297595:L1A` — DPYD (rs2297595): PharmGKB evidence level 1A linking it to capecitabine-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:25665007` (clinpgx_citation) — **Common variants in ACYP2 influence susceptibility to cisplatin-induced hearing loss.** — *Nature genetics · 2015*
  - [PMID 25665007] (Nature genetics, 2015) Common variants in ACYP2 influence susceptibility to cisplatin-induced hearing loss. Taking a genome-wide association study approach, we identified inherited genetic variations in ACYP2 associated with cisplatin-related ototoxicity (rs18723…
- `PMID:26928270` (clinpgx_citation) — **Replication of a genetic variant in ACYP2 associated with cisplatin-induced hearing loss in patients with osteosarcoma.** — *Pharmacogenetics and genomics · 2016*
  - [PMID 26928270] (Pharmacogenetics and genomics, 2016) Replication of a genetic variant in ACYP2 associated with cisplatin-induced hearing loss in patients with osteosarcoma. Irreversible hearing loss is a frequent side effect of the chemotherapeutic agent cisplatin and shows cons…
- `PMID:28445188` (clinpgx_citation) — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - [PMID 28445188] (Pharmacogenetics and genomics, 2017) TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity. Cisplatin ototoxicity affects 42-88% of treated children. Catechol-O-methyltransferase (COMT), thiopurine methyltransferas…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:42599282` (esearch) — **Three-dimensional Clay Model to Process Eyelid, Ear, and Urethral Mohs Layers.** — *Dermatologic surgery : official publication for American Society for Dermatologic Surgery [et al.] · 2026*
  - [PMID 42599282] (Dermatologic surgery : official publication for American Society for Dermatologic Surgery [et al.], 2026) Three-dimensional Clay Model to Process Eyelid, Ear, and Urethral Mohs Layers.…
- `PMID:42599278` (esearch) — **Histopathology and Clinical Features of SPARK Nevi in a Multi-Institutional Cohort.** — *International journal of surgical pathology · 2026*
  - [PMID 42599278] (International journal of surgical pathology, 2026) Histopathology and Clinical Features of SPARK Nevi in a Multi-Institutional Cohort. Background/ObjectivesSpitz nevus with architectural features of a Clark/dysplastic nevus ("SPARK nevus") is an uncommon melanocy…
- `PMID:12127547` (clinpgx_citation) — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - [PMID 12127547] (Bioorganic & medicinal chemistry letters, 2002) Decoding region bubble size and aminoglycoside antibiotic binding. Aminoglycoside antibiotics promiscuously bind to structurally diverse RNA molecules containing internal bubbles and bulges with affinities in the mi…
- `PMID:18830133` (clinpgx_citation) — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - [PMID 18830133] (Pharmacogenetics and genomics, 2008) Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population. In adult cystic fibrosis patient populations, gram-negative bacteria, particularly Pseudomonas aeruginosa, frequently require aggres…
- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:10376773` (clinpgx_citation) — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - [PMID 10376773] (Pharmacogenetics, 1999) Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal. The thiopurine methyltransferase (TPMT) genetic polymorphism has been shown to have a highly significant clinical i…
- `PMID:10734022` (clinpgx_citation) — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - [PMID 10734022] (Gastroenterology, 2000) Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease. The effects of 6-mercaptopurine (6-MP) are mediated via its intracellular conversion to 6-thioguanine (6-TG) and 6-methylmercaptopurine…
- `PMID:12209976` (clinpgx_citation) — **Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation.** — *International journal of cancer · 2002*
  - [PMID 12209976] (International journal of cancer, 2002) Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation. Dihydropyrimidine dehydrogenase (DPD) is the init…
- `PMID:17000685` (clinpgx_citation) — **Pharmacogenetics of capecitabine in advanced breast cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 17000685] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Pharmacogenetics of capecitabine in advanced breast cancer patients. Germinal gene polymorphisms can explain a part of the interpatient pharmacodynamic variabili…

</details>

<sub>KG: 32 entities / 86 relations · 24 references (15 PubMed) · 39 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** GSTM1, GSTP1

The genetic variants GSTM1 null and GSTP1 Ile/Val or Val/Val genotypes are implicated in increased susceptibility to cisplatin-induced hearing loss and tinnitus. The biological mechanism involves the role of glutathione S-transferases (GSTs) in detoxifying reactive metabolites generated by cisplatin, which can lead to ototoxicity if these enzymes are less effective due to genetic polymorphisms. For drug discovery and patient safety, pre-treatment screening for GSTM1 null status and GSTP1 genotypes could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or the use of alternative agents such as carboplatin.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L3` — TPMT (TPMT*1): PharmGKB evidence level 3 linking it to cisplatin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:COMT/rs4646316:L3` — COMT (rs4646316): PharmGKB evidence level 3 linking it to cisplatin-related Drug Toxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MT-RNR1/rs267606617:L1A` — MT-RNR1 (rs267606617): PharmGKB evidence level 1A linking it to tobramycin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L1A` — TPMT (TPMT*1): PharmGKB evidence level 1A linking it to azathioprine-related Dose reduction. ClinPGx relationship: ambiguous.
- `ClinPGx:COMT/rs165599:L3` — COMT (rs165599): PharmGKB evidence level 3 linking it to risperidone-related Schizophrenia. ClinPGx relationship: ambiguous.
- `ClinPGx:COMT/rs4680:L3` — COMT (rs4680): PharmGKB evidence level 3 linking it to antipsychotics-related Tardive Dyskinesia. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:23274376` (clinpgx_citation) — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - [PMID 23274376] (Journal of pediatric hematology/oncology, 2013) Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms. Cisplatin-induced ototoxicity, an important dose-limiting side effect, has proven hi…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:12127547` (clinpgx_citation) — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - [PMID 12127547] (Bioorganic & medicinal chemistry letters, 2002) Decoding region bubble size and aminoglycoside antibiotic binding. Aminoglycoside antibiotics promiscuously bind to structurally diverse RNA molecules containing internal bubbles and bulges with affinities in the mi…
- `PMID:18830133` (clinpgx_citation) — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - [PMID 18830133] (Pharmacogenetics and genomics, 2008) Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population. In adult cystic fibrosis patient populations, gram-negative bacteria, particularly Pseudomonas aeruginosa, frequently require aggres…
- `PMID:10376773` (clinpgx_citation) — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - [PMID 10376773] (Pharmacogenetics, 1999) Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal. The thiopurine methyltransferase (TPMT) genetic polymorphism has been shown to have a highly significant clinical i…
- `PMID:10734022` (clinpgx_citation) — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - [PMID 10734022] (Gastroenterology, 2000) Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease. The effects of 6-mercaptopurine (6-MP) are mediated via its intracellular conversion to 6-thioguanine (6-TG) and 6-methylmercaptopurine…
- `PMID:19451915` (clinpgx_citation) — **Candidate-gene association analysis of response to risperidone in African-American and white patients with schizophrenia.** — *The pharmacogenomics journal · 2009*
  - [PMID 19451915] (The pharmacogenomics journal, 2009) Candidate-gene association analysis of response to risperidone in African-American and white patients with schizophrenia. Clinical trial data were evaluated for the association between 22 single-nucleotide polymorphisms (SNPs) …
- `PMID:22935916` (clinpgx_citation) — **Association between a COMT polymorphism and clinical response to risperidone treatment: a pharmacogenetic study.** — *Psychiatric genetics · 2012*
  - [PMID 22935916] (Psychiatric genetics, 2012) Association between a COMT polymorphism and clinical response to risperidone treatment: a pharmacogenetic study. A total of 130 Chinese schizophrenic patients (45 male, 85 female) were enrolled in the study. Clinical efficacy was deter…
- `PMID:42597480` (esearch) — **Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness.** — *Frontiers in immunology · 2026*
  - [PMID 42597480] (Frontiers in immunology, 2026) Beyond HLA: an exploratory pilot study of non-HLA antibodies, HLA sensitization, and GSTT1 genotype in platelet transfusion refractoriness. Platelet transfusion refractoriness (PTR) is a common and clinically challenging condition w…
- `PMID:42577562` (esearch) — **Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra.** — *Cureus · 2026*
  - [PMID 42577562] (Cureus, 2026) Genetic Polymorphisms in the Glutathione S-transferase Gene With the Association of Lung Cancer: A Hospital-Based Case-Control Study in Southwestern Maharashtra. Background Lung cancer is one of the leading causes of cancer-related mortality globall…

</details>

<sub>KG: 31 entities / 86 relations · 22 references (13 PubMed) · 40 retrieval events</sub>

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** GSTM1

The non-null genotype of GSTM1 is strongly associated with an increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, suggesting a critical role for glutathione S-transferase activity in the detoxification process. The biological mechanism likely involves impaired cellular defense against oxidative stress and reduced ability to mitigate cisplatin's toxic effects on auditory hair cells. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could inform personalized dosing strategies or alternative therapeutic options to minimize ototoxicity risk in susceptible patients.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L3` — TPMT (TPMT*1): PharmGKB evidence level 3 linking it to cisplatin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:COMT/rs4646316:L3` — COMT (rs4646316): PharmGKB evidence level 3 linking it to cisplatin-related Drug Toxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MT-RNR1/rs267606617:L1A` — MT-RNR1 (rs267606617): PharmGKB evidence level 1A linking it to tobramycin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L1A` — TPMT (TPMT*1): PharmGKB evidence level 1A linking it to azathioprine-related Dose reduction. ClinPGx relationship: ambiguous.
- `ClinPGx:UGT1A1/UGT1A1*1:L1A` — UGT1A1 (UGT1A1*1): PharmGKB evidence level 1A linking it to FOLFIRI-related Neutropenia. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:23274376` (clinpgx_citation) — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - [PMID 23274376] (Journal of pediatric hematology/oncology, 2013) Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms. Cisplatin-induced ototoxicity, an important dose-limiting side effect, has proven hi…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:12127547` (clinpgx_citation) — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - [PMID 12127547] (Bioorganic & medicinal chemistry letters, 2002) Decoding region bubble size and aminoglycoside antibiotic binding. Aminoglycoside antibiotics promiscuously bind to structurally diverse RNA molecules containing internal bubbles and bulges with affinities in the mi…
- `PMID:18830133` (clinpgx_citation) — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - [PMID 18830133] (Pharmacogenetics and genomics, 2008) Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population. In adult cystic fibrosis patient populations, gram-negative bacteria, particularly Pseudomonas aeruginosa, frequently require aggres…
- `PMID:10376773` (clinpgx_citation) — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - [PMID 10376773] (Pharmacogenetics, 1999) Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal. The thiopurine methyltransferase (TPMT) genetic polymorphism has been shown to have a highly significant clinical i…
- `PMID:10734022` (clinpgx_citation) — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - [PMID 10734022] (Gastroenterology, 2000) Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease. The effects of 6-mercaptopurine (6-MP) are mediated via its intracellular conversion to 6-thioguanine (6-TG) and 6-methylmercaptopurine…
- `PMID:41077199` (esearch) — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - [PMID 41077199] (Critical reviews in oncology/hematology, 2025) The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review. Variation in the prevalence and severity of late effects in similarly treated childhood cancer survivors…
- `PMID:36802061` (esearch) — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - [PMID 36802061] (Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery, 2023) Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy. The objective of t…
- `PMID:42542098` (esearch) — **Proteomic profiling of root microsomal membrane fractions reveals distinct RBOHC- and RBOHF-associated responses to cadmium in Arabidopsis.** — *Ecotoxicology and environmental safety · 2026*
  - [PMID 42542098] (Ecotoxicology and environmental safety, 2026) Proteomic profiling of root microsomal membrane fractions reveals distinct RBOHC- and RBOHF-associated responses to cadmium in Arabidopsis. Cadmium (Cd) is a toxic heavy metal for plants, and although its mechanisms o…
- `PMID:42529344` (esearch) — **Integrative transcriptomic and proteomic analysis reveals the regulatory mechanisms underlying oilseed rape resistance to Leptosphaeria biglobosa.** — *Frontiers in plant science · 2026*
  - [PMID 42529344] (Frontiers in plant science, 2026) Integrative transcriptomic and proteomic analysis reveals the regulatory mechanisms underlying oilseed rape resistance to Leptosphaeria biglobosa. Blackleg disease caused by Leptosphaeria species is a major constraint to rapeseed…
- `PMID:42033883` (esearch) — **Post-treatment paternity in testicular cancer survivors: Do demographic variables matter?** — *Cancer epidemiology · 2026*
  - [PMID 42033883] (Cancer epidemiology, 2026) Post-treatment paternity in testicular cancer survivors: Do demographic variables matter? Few commonly available factors are known which independently of treatment are associated with post- diagnosis paternity in Testicular Cancer Survi…
- `PMID:40324110` (esearch) — **Key Updates in Testicular Cancer: Optimizing Survivorship and Survival.** — *American Society of Clinical Oncology educational book. American Society of Clinical Oncology. Annual Meeting · 2025*
  - [PMID 40324110] (American Society of Clinical Oncology educational book. American Society of Clinical Oncology. Annual Meeting, 2025) Key Updates in Testicular Cancer: Optimizing Survivorship and Survival. Testicular cancer is a rare but highly curable malignancy, predominantly a…
- `PMID:11990381` (clinpgx_citation) — **UGT1A1*28 polymorphism as a determinant of irinotecan disposition and toxicity.** — *The pharmacogenomics journal · 2002*
  - [PMID 11990381] (The pharmacogenomics journal, 2002) UGT1A1*28 polymorphism as a determinant of irinotecan disposition and toxicity. The metabolism of irinotecan (CPT-11) involves sequential activation to SN-38 and detoxification to the pharmacologically inactive SN-38 glucuronid…
- `PMID:15007088` (clinpgx_citation) — **Genetic variants in the UDP-glucuronosyltransferase 1A1 gene predict the risk of severe neutropenia of irinotecan.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2004*
  - [PMID 15007088] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2004) Genetic variants in the UDP-glucuronosyltransferase 1A1 gene predict the risk of severe neutropenia of irinotecan. Severe toxicity is commonly observed in cancer p…

</details>

<sub>KG: 28 entities / 86 relations · 25 references (17 PubMed) · 36 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** GSTM1

The non-null genotype of GSTM1 is strongly associated with an increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, suggesting a critical role for glutathione S-transferase activity in the detoxification process. The biological mechanism likely involves impaired cellular defense against oxidative stress and reduced ability to mitigate cisplatin's toxic effects on auditory hair cells. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could inform personalized dosing strategies or alternative therapeutic options to minimize ototoxicity risk in susceptible patients.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L3` — TPMT (TPMT*1): PharmGKB evidence level 3 linking it to cisplatin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:COMT/rs4646316:L3` — COMT (rs4646316): PharmGKB evidence level 3 linking it to cisplatin-related Drug Toxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MT-RNR1/rs267606617:L1A` — MT-RNR1 (rs267606617): PharmGKB evidence level 1A linking it to tobramycin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L1A` — TPMT (TPMT*1): PharmGKB evidence level 1A linking it to azathioprine-related Dose reduction. ClinPGx relationship: ambiguous.
- `ClinPGx:UGT1A1/UGT1A1*1:L1A` — UGT1A1 (UGT1A1*1): PharmGKB evidence level 1A linking it to FOLFIRI-related Neutropenia. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:23274376` (clinpgx_citation) — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - [PMID 23274376] (Journal of pediatric hematology/oncology, 2013) Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms. Cisplatin-induced ototoxicity, an important dose-limiting side effect, has proven hi…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:12127547` (clinpgx_citation) — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - [PMID 12127547] (Bioorganic & medicinal chemistry letters, 2002) Decoding region bubble size and aminoglycoside antibiotic binding. Aminoglycoside antibiotics promiscuously bind to structurally diverse RNA molecules containing internal bubbles and bulges with affinities in the mi…
- `PMID:18830133` (clinpgx_citation) — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - [PMID 18830133] (Pharmacogenetics and genomics, 2008) Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population. In adult cystic fibrosis patient populations, gram-negative bacteria, particularly Pseudomonas aeruginosa, frequently require aggres…
- `PMID:10376773` (clinpgx_citation) — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - [PMID 10376773] (Pharmacogenetics, 1999) Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal. The thiopurine methyltransferase (TPMT) genetic polymorphism has been shown to have a highly significant clinical i…
- `PMID:10734022` (clinpgx_citation) — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - [PMID 10734022] (Gastroenterology, 2000) Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease. The effects of 6-mercaptopurine (6-MP) are mediated via its intracellular conversion to 6-thioguanine (6-TG) and 6-methylmercaptopurine…
- `PMID:41077199` (esearch) — **The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review.** — *Critical reviews in oncology/hematology · 2025*
  - [PMID 41077199] (Critical reviews in oncology/hematology, 2025) The influence of genetic variation on late effects in childhood cancer survivors: An updated systematic review. Variation in the prevalence and severity of late effects in similarly treated childhood cancer survivors…
- `PMID:36802061` (esearch) — **Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy.** — *Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery · 2023*
  - [PMID 36802061] (Otolaryngology--head and neck surgery : official journal of American Academy of Otolaryngology-Head and Neck Surgery, 2023) Systematic Review and Meta-Analysis of the Influence of Genetic Variation on Ototoxicity in Platinum-Based Chemotherapy. The objective of t…
- `PMID:42542098` (esearch) — **Proteomic profiling of root microsomal membrane fractions reveals distinct RBOHC- and RBOHF-associated responses to cadmium in Arabidopsis.** — *Ecotoxicology and environmental safety · 2026*
  - [PMID 42542098] (Ecotoxicology and environmental safety, 2026) Proteomic profiling of root microsomal membrane fractions reveals distinct RBOHC- and RBOHF-associated responses to cadmium in Arabidopsis. Cadmium (Cd) is a toxic heavy metal for plants, and although its mechanisms o…
- `PMID:42529344` (esearch) — **Integrative transcriptomic and proteomic analysis reveals the regulatory mechanisms underlying oilseed rape resistance to Leptosphaeria biglobosa.** — *Frontiers in plant science · 2026*
  - [PMID 42529344] (Frontiers in plant science, 2026) Integrative transcriptomic and proteomic analysis reveals the regulatory mechanisms underlying oilseed rape resistance to Leptosphaeria biglobosa. Blackleg disease caused by Leptosphaeria species is a major constraint to rapeseed…
- `PMID:42033883` (esearch) — **Post-treatment paternity in testicular cancer survivors: Do demographic variables matter?** — *Cancer epidemiology · 2026*
  - [PMID 42033883] (Cancer epidemiology, 2026) Post-treatment paternity in testicular cancer survivors: Do demographic variables matter? Few commonly available factors are known which independently of treatment are associated with post- diagnosis paternity in Testicular Cancer Survi…
- `PMID:40324110` (esearch) — **Key Updates in Testicular Cancer: Optimizing Survivorship and Survival.** — *American Society of Clinical Oncology educational book. American Society of Clinical Oncology. Annual Meeting · 2025*
  - [PMID 40324110] (American Society of Clinical Oncology educational book. American Society of Clinical Oncology. Annual Meeting, 2025) Key Updates in Testicular Cancer: Optimizing Survivorship and Survival. Testicular cancer is a rare but highly curable malignancy, predominantly a…
- `PMID:11990381` (clinpgx_citation) — **UGT1A1*28 polymorphism as a determinant of irinotecan disposition and toxicity.** — *The pharmacogenomics journal · 2002*
  - [PMID 11990381] (The pharmacogenomics journal, 2002) UGT1A1*28 polymorphism as a determinant of irinotecan disposition and toxicity. The metabolism of irinotecan (CPT-11) involves sequential activation to SN-38 and detoxification to the pharmacologically inactive SN-38 glucuronid…
- `PMID:15007088` (clinpgx_citation) — **Genetic variants in the UDP-glucuronosyltransferase 1A1 gene predict the risk of severe neutropenia of irinotecan.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2004*
  - [PMID 15007088] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2004) Genetic variants in the UDP-glucuronosyltransferase 1A1 gene predict the risk of severe neutropenia of irinotecan. Severe toxicity is commonly observed in cancer p…

</details>

<sub>KG: 28 entities / 86 relations · 25 references (17 PubMed) · 36 retrieval events</sub>

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** TPMT, ACYP2 (rs1872328), GSTM1

The high risk of hearing loss in your daughter while on cisplatin for Neuroblastoma is likely influenced by genetic factors including TPMT, ACYP2 (rs1872328), and GSTM1. The biological mechanism involves altered drug metabolism and detoxification pathways that may exacerbate ototoxicity due to these variants. For patient safety, pre-treatment biomarker screening for these variants should be considered to identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower risk of ototoxicity.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:ACYP2/rs1872328:L3` — ACYP2 (rs1872328): PharmGKB evidence level 3 linking it to cisplatin-related Brain Neoplasms, Hearing Loss. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L3` — TPMT (TPMT*1): PharmGKB evidence level 3 linking it to cisplatin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L1A` — TPMT (TPMT*1): PharmGKB evidence level 1A linking it to azathioprine-related Dose reduction. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MT-RNR1/rs267606617:L1A` — MT-RNR1 (rs267606617): PharmGKB evidence level 1A linking it to tobramycin-related Ototoxicity. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:25665007` (clinpgx_citation) — **Common variants in ACYP2 influence susceptibility to cisplatin-induced hearing loss.** — *Nature genetics · 2015*
  - [PMID 25665007] (Nature genetics, 2015) Common variants in ACYP2 influence susceptibility to cisplatin-induced hearing loss. Taking a genome-wide association study approach, we identified inherited genetic variations in ACYP2 associated with cisplatin-related ototoxicity (rs18723…
- `PMID:26928270` (clinpgx_citation) — **Replication of a genetic variant in ACYP2 associated with cisplatin-induced hearing loss in patients with osteosarcoma.** — *Pharmacogenetics and genomics · 2016*
  - [PMID 26928270] (Pharmacogenetics and genomics, 2016) Replication of a genetic variant in ACYP2 associated with cisplatin-induced hearing loss in patients with osteosarcoma. Irreversible hearing loss is a frequent side effect of the chemotherapeutic agent cisplatin and shows cons…
- `PMID:28445188` (clinpgx_citation) — **TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity.** — *Pharmacogenetics and genomics · 2017*
  - [PMID 28445188] (Pharmacogenetics and genomics, 2017) TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplatin-induced ototoxicity. Cisplatin ototoxicity affects 42-88% of treated children. Catechol-O-methyltransferase (COMT), thiopurine methyltransferas…
- `PMID:10376773` (clinpgx_citation) — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - [PMID 10376773] (Pharmacogenetics, 1999) Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal. The thiopurine methyltransferase (TPMT) genetic polymorphism has been shown to have a highly significant clinical i…
- `PMID:10734022` (clinpgx_citation) — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - [PMID 10734022] (Gastroenterology, 2000) Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease. The effects of 6-mercaptopurine (6-MP) are mediated via its intracellular conversion to 6-thioguanine (6-TG) and 6-methylmercaptopurine…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:42598616` (esearch) — **Prenatally detected fetus in fetu with progressive imaging organization: Multimodality radiology-pathology correlation.** — *Radiology case reports · 2026*
  - [PMID 42598616] (Radiology case reports, 2026) Prenatally detected fetus in fetu with progressive imaging organization: Multimodality radiology-pathology correlation. Fetus in fetu is a rare congenital anomaly that may mimic other suprarenal masses including neuroblastoma, terato…
- `PMID:42595252` (esearch) — **URG7-Driven Homeostatic Adaptation Protects SH-SY5Y Cells from 6-OHDA Neurotoxicity.** — *Journal of molecular biology · 2026*
  - [PMID 42595252] (Journal of molecular biology, 2026) URG7-Driven Homeostatic Adaptation Protects SH-SY5Y Cells from 6-OHDA Neurotoxicity. Parkinson's disease (PD) is characterized by progressive dopaminergic neurodegeneration associated with oxidative stress, mitochondrial dysfun…
- `PMID:42592166` (esearch) — **Over-the-counter hearing aids and integrated health-monitoring sensors: a review of clinical evidence and implementation.** — *Frontiers in digital health · 2026*
  - [PMID 42592166] (Frontiers in digital health, 2026) Over-the-counter hearing aids and integrated health-monitoring sensors: a review of clinical evidence and implementation. The FDA's 2022 over-the-counter (OTC) hearing aid rule created a new access pathway for adults with mild t…
- `PMID:42581014` (esearch) — **Goal-setting in audiology: where practice aligns with, or falls short of, best practice.** — *International journal of audiology · 2026*
  - [PMID 42581014] (International journal of audiology, 2026) Goal-setting in audiology: where practice aligns with, or falls short of, best practice. To examine how clinical goal-setting is used in routine audiological practice and the extent to which practice aligns with evidence-…
- `PMID:12127547` (clinpgx_citation) — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - [PMID 12127547] (Bioorganic & medicinal chemistry letters, 2002) Decoding region bubble size and aminoglycoside antibiotic binding. Aminoglycoside antibiotics promiscuously bind to structurally diverse RNA molecules containing internal bubbles and bulges with affinities in the mi…
- `PMID:18830133` (clinpgx_citation) — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - [PMID 18830133] (Pharmacogenetics and genomics, 2008) Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population. In adult cystic fibrosis patient populations, gram-negative bacteria, particularly Pseudomonas aeruginosa, frequently require aggres…
- `PMID:42598053` (esearch) — **The road from standardized to personalized medicine: the difficult-to-treat framework as a critical waystation.** — *Frontiers in medicine · 2026*
  - [PMID 42598053] (Frontiers in medicine, 2026) The road from standardized to personalized medicine: the difficult-to-treat framework as a critical waystation. Standardized care has become the cornerstone of modern medicine. However, many patients remain symptomatic despite followi…
- `PMID:42597842` (esearch) — **HIPK4 is a novel gene associated with teratozoospermia and male infertility.** — *Human reproduction open · 2026*
  - [PMID 42597842] (Human reproduction open, 2026) HIPK4 is a novel gene associated with teratozoospermia and male infertility. Are pathogenic variants in homeodomain-interacting protein kinase (HIPK4) associated with sperm head abnormalities that cause male infertility? HIPK4 is a …
- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …

</details>

<sub>KG: 33 entities / 86 relations · 24 references (17 PubMed) · 35 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** TPMT, GSTM1

The TPMT variant and GSTM1 polymorphism are implicated in the increased risk of cisplatin-induced hearing loss. The biological mechanism involves altered drug metabolism due to reduced TPMT activity, leading to higher levels of toxic metabolites that can cause ototoxicity. Additionally, GSTM1 variants may impair detoxification pathways, further exacerbating this risk. For patient safety and drug discovery, pre-treatment genetic screening for these variants is crucial to identify high-risk patients who might benefit from dose adjustments or alternative agents with lower ototoxic potential.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L3` — TPMT (TPMT*1): PharmGKB evidence level 3 linking it to cisplatin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:COMT/rs4646316:L3` — COMT (rs4646316): PharmGKB evidence level 3 linking it to cisplatin-related Drug Toxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:TPMT/TPMT*1:L1A` — TPMT (TPMT*1): PharmGKB evidence level 1A linking it to azathioprine-related Dose reduction. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MT-RNR1/rs267606617:L1A` — MT-RNR1 (rs267606617): PharmGKB evidence level 1A linking it to tobramycin-related Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTT1/rs4630:L3` — GSTT1 (rs4630): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:GSTT1/GSTT1 non-null:L3` — GSTT1 (GSTT1 non-null): PharmGKB evidence level 3 linking it to imatinib-related Chronic myelogenous leukemia, BCR-ABL1 positive. ClinPGx relationship: associated.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:23274376` (clinpgx_citation) — **Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms.** — *Journal of pediatric hematology/oncology · 2013*
  - [PMID 23274376] (Journal of pediatric hematology/oncology, 2013) Cisplatin-induced ototoxicity in pediatric solid tumors: the role of glutathione S-transferases and megalin genetic polymorphisms. Cisplatin-induced ototoxicity, an important dose-limiting side effect, has proven hi…
- `PMID:10376773` (clinpgx_citation) — **Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal.** — *Pharmacogenetics · 1999*
  - [PMID 10376773] (Pharmacogenetics, 1999) Thiopurine methyltransferase pharmacogenetics: alternative molecular diagnosis and preliminary data from Northern Portugal. The thiopurine methyltransferase (TPMT) genetic polymorphism has been shown to have a highly significant clinical i…
- `PMID:10734022` (clinpgx_citation) — **Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease.** — *Gastroenterology · 2000*
  - [PMID 10734022] (Gastroenterology, 2000) Pharmacogenomics and metabolite measurement for 6-mercaptopurine therapy in inflammatory bowel disease. The effects of 6-mercaptopurine (6-MP) are mediated via its intracellular conversion to 6-thioguanine (6-TG) and 6-methylmercaptopurine…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:42598616` (esearch) — **Prenatally detected fetus in fetu with progressive imaging organization: Multimodality radiology-pathology correlation.** — *Radiology case reports · 2026*
  - [PMID 42598616] (Radiology case reports, 2026) Prenatally detected fetus in fetu with progressive imaging organization: Multimodality radiology-pathology correlation. Fetus in fetu is a rare congenital anomaly that may mimic other suprarenal masses including neuroblastoma, terato…
- `PMID:42595252` (esearch) — **URG7-Driven Homeostatic Adaptation Protects SH-SY5Y Cells from 6-OHDA Neurotoxicity.** — *Journal of molecular biology · 2026*
  - [PMID 42595252] (Journal of molecular biology, 2026) URG7-Driven Homeostatic Adaptation Protects SH-SY5Y Cells from 6-OHDA Neurotoxicity. Parkinson's disease (PD) is characterized by progressive dopaminergic neurodegeneration associated with oxidative stress, mitochondrial dysfun…
- `PMID:12127547` (clinpgx_citation) — **Decoding region bubble size and aminoglycoside antibiotic binding.** — *Bioorganic & medicinal chemistry letters · 2002*
  - [PMID 12127547] (Bioorganic & medicinal chemistry letters, 2002) Decoding region bubble size and aminoglycoside antibiotic binding. Aminoglycoside antibiotics promiscuously bind to structurally diverse RNA molecules containing internal bubbles and bulges with affinities in the mi…
- `PMID:18830133` (clinpgx_citation) — **Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population.** — *Pharmacogenetics and genomics · 2008*
  - [PMID 18830133] (Pharmacogenetics and genomics, 2008) Frequency of mitochondrial 12S ribosomal RNA variants in an adult cystic fibrosis population. In adult cystic fibrosis patient populations, gram-negative bacteria, particularly Pseudomonas aeruginosa, frequently require aggres…
- `PMID:21435719` (clinpgx_citation) — **Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide.** — *Leukemia research · 2011*
  - [PMID 21435719] (Leukemia research, 2011) Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide. Single nucleotide polymorphisms (SNPs) in 12 genes involving multidrug resistance,…
- `PMID:25188725` (clinpgx_citation) — **Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia.** — *Clinical pharmacology and therapeutics · 2014*
  - [PMID 25188725] (Clinical pharmacology and therapeutics, 2014) Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia. Approximately 40% of patients with chronic myeloid leukemia (CML) receiving imatinib fail treatment. The…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…

</details>

<sub>KG: 29 entities / 86 relations · 25 references (15 PubMed) · 40 retrieval events</sub>

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** GSTT1

The permanent inner ear damage observed after Platinol treatment may be influenced by the GSTT1 status, a genetic polymorphism affecting glutathione S-transferase theta 1 (GSTT1), which is involved in detoxifying and metabolizing drugs like cisplatin. Individuals with a null genotype for GSTT1 have reduced capacity to metabolize these drugs, potentially leading to higher toxicity and ototoxicity. This finding underscores the importance of pre-treatment genetic screening for GSTT1 status to predict drug metabolism efficiency and adjust dosing accordingly or consider alternative agents with lower ototoxic risk.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:LRP2/rs2228171:L3` — LRP2 (rs2228171): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM3/rs1799735:L3` — GSTM3 (rs1799735): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTT1/rs4630:L3` — GSTT1 (rs4630): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:GSTT1/GSTT1 non-null:L3` — GSTT1 (GSTT1 non-null): PharmGKB evidence level 3 linking it to imatinib-related Chronic myelogenous leukemia, BCR-ABL1 positive. ClinPGx relationship: associated.
- `ClinPGx:ERCC1/rs735482:L3` — ERCC1 (rs735482): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:CDA/rs532545:L3` — CDA (rs532545): PharmGKB evidence level 3 linking it to cytarabine-related Leukemia, Myeloid. ClinPGx relationship: ambiguous.
- `ClinPGx:CDA/rs602950:L3` — CDA (rs602950): PharmGKB evidence level 3 linking it to cytarabine-related Toxicity. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:19620936` (clinpgx_citation) — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - [PMID 19620936] (Pharmacogenetics and genomics, 2009) Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes. Genetic variations or polymorphisms within genes of the nucleotide excision repair (NER) pathway alter DNA repair capacity. Reduced DNA repa…
- `PMID:21435719` (clinpgx_citation) — **Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide.** — *Leukemia research · 2011*
  - [PMID 21435719] (Leukemia research, 2011) Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide. Single nucleotide polymorphisms (SNPs) in 12 genes involving multidrug resistance,…
- `PMID:25188725` (clinpgx_citation) — **Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia.** — *Clinical pharmacology and therapeutics · 2014*
  - [PMID 25188725] (Clinical pharmacology and therapeutics, 2014) Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia. Approximately 40% of patients with chronic myeloid leukemia (CML) receiving imatinib fail treatment. The…
- `PMID:19786980` (clinpgx_citation) — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - [PMID 19786980] (The pharmacogenomics journal, 2010) Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients. Platinum drugs are among the most active and widely used agents in the treatment of different cancers. However, the…
- `PMID:22188361` (clinpgx_citation) — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - [PMID 22188361] (Pharmacogenomics, 2012) Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins. There is a substantial difference between Asians and Caucasians in their reaction to platinum drugs. To determine whether population-r…
- `PMID:18473752` (clinpgx_citation) — **A carboxylesterase 2 gene polymorphism as predictor of capecitabine on response and time to progression.** — *Current drug metabolism · 2008*
  - [PMID 18473752] (Current drug metabolism, 2008) A carboxylesterase 2 gene polymorphism as predictor of capecitabine on response and time to progression. Capecitabine is a drug that requires the consecutive action of three enzymes: carboxylesterase 2 (CES 2), cytidine deaminase (C…
- `PMID:19458626` (clinpgx_citation) — **SNP analyses in cytarabine metabolizing enzymes in AML patients and their impact on treatment response and patient survival: identification of CDA SNP C-451T as an independent prognostic parameter for survival.** — *Leukemia · 2009*
  - [PMID 19458626] (Leukemia, 2009) SNP analyses in cytarabine metabolizing enzymes in AML patients and their impact on treatment response and patient survival: identification of CDA SNP C-451T as an independent prognostic parameter for survival.…
- `PMID:42165380` (esearch) — **Association of XPD Gene Polymorphisms with Cutaneous Melanoma Risk: A Meta-Analysis and Trial Sequence Evaluation.** — *Cancer investigation · 2026*
  - [PMID 42165380] (Cancer investigation, 2026) Association of XPD Gene Polymorphisms with Cutaneous Melanoma Risk: A Meta-Analysis and Trial Sequence Evaluation. Conflicting results have emerged regarding the relationship between XPD polymorphisms and cutaneous melanoma (CM) suscep…
- `PMID:42109639` (esearch) — **A meta-analysis and expression profiling of DNA repair gene polymorphisms in leukemia.** — *Frontiers in oncology · 2026*
  - [PMID 42109639] (Frontiers in oncology, 2026) A meta-analysis and expression profiling of DNA repair gene polymorphisms in leukemia. Genetic susceptibility is believed to contribute to leukemia development. This study aimed to systematically evaluate the association between DNA r…

</details>

<sub>KG: 33 entities / 86 relations · 23 references (13 PubMed) · 40 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** GSTT1

The permanent inner ear damage observed after Platinol treatment may be influenced by the child's GSTT1 status, a genetic polymorphism that affects drug metabolism and detoxification. The GSTT1 gene encodes glutathione S-transferase theta 1, which is involved in the conjugation of xenobiotics like cisplatin with glutathione for excretion or detoxification. Individuals lacking functional GSTT1 may have reduced capacity to metabolize Platinol efficiently, potentially increasing susceptibility to ototoxicity. For drug discovery and patient safety, pre-treatment screening for GSTT1 status could help identify patients at higher risk of adverse reactions, allowing for dose adjustments or the use of alternative agents such as carboplatin.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:LRP2/rs2228171:L3` — LRP2 (rs2228171): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM3/rs1799735:L3` — GSTM3 (rs1799735): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTT1/rs4630:L3` — GSTT1 (rs4630): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:GSTT1/GSTT1 non-null:L3` — GSTT1 (GSTT1 non-null): PharmGKB evidence level 3 linking it to imatinib-related Chronic myelogenous leukemia, BCR-ABL1 positive. ClinPGx relationship: associated.
- `ClinPGx:ERCC1/rs735482:L3` — ERCC1 (rs735482): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:CDA/rs532545:L3` — CDA (rs532545): PharmGKB evidence level 3 linking it to cytarabine-related Leukemia, Myeloid. ClinPGx relationship: ambiguous.
- `ClinPGx:CDA/rs602950:L3` — CDA (rs602950): PharmGKB evidence level 3 linking it to cytarabine-related Toxicity. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:15213713/PMC2409815` (clinpgx_citation+pmc_xml) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713 | PMC2409815 full text via pmc_xml] A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. :: Colorectal cancer is the third most common cause of death from canc…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:19620936` (clinpgx_citation) — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - [PMID 19620936] (Pharmacogenetics and genomics, 2009) Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes. Genetic variations or polymorphisms within genes of the nucleotide excision repair (NER) pathway alter DNA repair capacity. Reduced DNA repa…
- `PMID:21435719` (clinpgx_citation) — **Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide.** — *Leukemia research · 2011*
  - [PMID 21435719] (Leukemia research, 2011) Impact on response and survival of DNA repair single nucleotide polymorphisms in relapsed or refractory multiple myeloma patients treated with thalidomide. Single nucleotide polymorphisms (SNPs) in 12 genes involving multidrug resistance,…
- `PMID:25188725` (clinpgx_citation) — **Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia.** — *Clinical pharmacology and therapeutics · 2014*
  - [PMID 25188725] (Clinical pharmacology and therapeutics, 2014) Dual glutathione-S-transferase-θ1 and -μ1 gene deletions determine imatinib failure in chronic myeloid leukemia. Approximately 40% of patients with chronic myeloid leukemia (CML) receiving imatinib fail treatment. The…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:19786980` (clinpgx_citation) — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - [PMID 19786980] (The pharmacogenomics journal, 2010) Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients. Platinum drugs are among the most active and widely used agents in the treatment of different cancers. However, the…
- `PMID:22188361` (clinpgx_citation) — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - [PMID 22188361] (Pharmacogenomics, 2012) Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins. There is a substantial difference between Asians and Caucasians in their reaction to platinum drugs. To determine whether population-r…
- `PMID:18473752` (clinpgx_citation) — **A carboxylesterase 2 gene polymorphism as predictor of capecitabine on response and time to progression.** — *Current drug metabolism · 2008*
  - [PMID 18473752] (Current drug metabolism, 2008) A carboxylesterase 2 gene polymorphism as predictor of capecitabine on response and time to progression. Capecitabine is a drug that requires the consecutive action of three enzymes: carboxylesterase 2 (CES 2), cytidine deaminase (C…
- `PMID:19458626` (clinpgx_citation) — **SNP analyses in cytarabine metabolizing enzymes in AML patients and their impact on treatment response and patient survival: identification of CDA SNP C-451T as an independent prognostic parameter for survival.** — *Leukemia · 2009*
  - [PMID 19458626] (Leukemia, 2009) SNP analyses in cytarabine metabolizing enzymes in AML patients and their impact on treatment response and patient survival: identification of CDA SNP C-451T as an independent prognostic parameter for survival.…
- `PMID:42165380` (esearch) — **Association of XPD Gene Polymorphisms with Cutaneous Melanoma Risk: A Meta-Analysis and Trial Sequence Evaluation.** — *Cancer investigation · 2026*
  - [PMID 42165380] (Cancer investigation, 2026) Association of XPD Gene Polymorphisms with Cutaneous Melanoma Risk: A Meta-Analysis and Trial Sequence Evaluation. Conflicting results have emerged regarding the relationship between XPD polymorphisms and cutaneous melanoma (CM) suscep…
- `PMID:42109639` (esearch) — **A meta-analysis and expression profiling of DNA repair gene polymorphisms in leukemia.** — *Frontiers in oncology · 2026*
  - [PMID 42109639] (Frontiers in oncology, 2026) A meta-analysis and expression profiling of DNA repair gene polymorphisms in leukemia. Genetic susceptibility is believed to contribute to leukemia development. This study aimed to systematically evaluate the association between DNA r…

</details>

<sub>KG: 33 entities / 86 relations · 24 references (14 PubMed) · 40 retrieval events</sub>

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** ERCC1, GSTP1, GSTM3

Cisplatin-induced peripheral neuropathy is influenced by genetic polymorphisms such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735). These variants likely affect the drug's metabolism, DNA repair mechanisms, or cellular sensitivity to cisplatin, thereby modulating the risk of developing peripheral neuropathy. For drug discovery and patient safety, pre-treatment genetic screening for these polymorphisms can help predict susceptibility to adverse effects, allowing for dose adjustments or alternative therapeutic strategies to mitigate risks.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM3/rs1799735:L3` — GSTM3 (rs1799735): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs735482:L3` — ERCC1 (rs735482): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:CASP7/rs7921977:L3` — CASP7 (rs7921977): PharmGKB evidence level 3 linking it to gemcitabine-related Non-Small Cell Lung Carcinoma. ClinPGx relationship: ambiguous.
- `ClinPGx:CASP7/rs2227310:L3` — CASP7 (rs2227310): PharmGKB evidence level 3 linking it to gemcitabine-related Non-Small Cell Lung Carcinoma. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:19620936` (clinpgx_citation) — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - [PMID 19620936] (Pharmacogenetics and genomics, 2009) Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes. Genetic variations or polymorphisms within genes of the nucleotide excision repair (NER) pathway alter DNA repair capacity. Reduced DNA repa…
- `PMID:42598682` (esearch) — **Ultrasound-Guided Perineural Corticosteroid Injection and Dextrose Hydrodissection for Carpal Tunnel Syndrome: Current Evidence and Clinical Considerations.** — *Cureus · 2026*
  - [PMID 42598682] (Cureus, 2026) Ultrasound-Guided Perineural Corticosteroid Injection and Dextrose Hydrodissection for Carpal Tunnel Syndrome: Current Evidence and Clinical Considerations. Carpal tunnel syndrome (CTS) is the most common entrapment neuropathy and represents a subst…
- `PMID:42598352` (esearch) — **Effectiveness of Buerger Allen Exercise as an Adjunct to Standard Pharmacotherapy in Reducing Peripheral Neuropathy Symptoms Among Patients with Type 2 Diabetes Mellitus: A Randomized Controlled Pilot Study.** — *Journal of pharmacy & bioallied sciences · 2026*
  - [PMID 42598352] (Journal of pharmacy & bioallied sciences, 2026) Effectiveness of Buerger Allen Exercise as an Adjunct to Standard Pharmacotherapy in Reducing Peripheral Neuropathy Symptoms Among Patients with Type 2 Diabetes Mellitus: A Randomized Controlled Pilot Study. Diabeti…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:19786980` (clinpgx_citation) — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - [PMID 19786980] (The pharmacogenomics journal, 2010) Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients. Platinum drugs are among the most active and widely used agents in the treatment of different cancers. However, the…
- `PMID:22188361` (clinpgx_citation) — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - [PMID 22188361] (Pharmacogenomics, 2012) Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins. There is a substantial difference between Asians and Caucasians in their reaction to platinum drugs. To determine whether population-r…
- `PMID:22441531` (clinpgx_citation) — **Association of CASP7 polymorphisms and survival of patients with non-small cell lung cancer with platinum-based chemotherapy treatment.** — *Chest · 2012*
  - [PMID 22441531] (Chest, 2012) Association of CASP7 polymorphisms and survival of patients with non-small cell lung cancer with platinum-based chemotherapy treatment. CASP7 plays a crucial role in cancer development and chemotherapy efficacy. We, therefore, explored whether single…
- `PMID:42598812` (esearch) — **MLN4924 suppresses pancreatic cancer progression and enhances chemosensitivity to gemcitabine by targeting the PTGS2/EGFR-PI3K/Akt/mTOR signaling axis.** — *Anti-cancer drugs · 2026*
  - [PMID 42598812] (Anti-cancer drugs, 2026) MLN4924 suppresses pancreatic cancer progression and enhances chemosensitivity to gemcitabine by targeting the PTGS2/EGFR-PI3K/Akt/mTOR signaling axis. Pancreatic cancer is a highly lethal digestive malignancy characterized by insidious o…
- `PMID:42599160` (esearch) — **The pan-tumor landscape, allelic status, and genomic complexity of SMARCA4 alterations.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2026*
  - [PMID 42599160] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2026) The pan-tumor landscape, allelic status, and genomic complexity of SMARCA4 alterations. The clinical implications of distinct SMARCA4 alteration classes remain i…
- `PMID:42598915` (esearch) — **TLS as Predictors and Targets in Neoadjuvant Chemoimmunotherapy for NSCLC.** — *Thoracic cancer · 2026*
  - [PMID 42598915] (Thoracic cancer, 2026) TLS as Predictors and Targets in Neoadjuvant Chemoimmunotherapy for NSCLC. Tertiary lymphoid structures (TLS) have emerged as critical modulators of antitumor immunity in non-small cell lung cancer (NSCLC), with growing evidence supporting …
- `PMID:42516273` (esearch) — **Experimental study and thermodynamic modelling of the Nb-Sb system.** — *RSC advances · 2026*
  - [PMID 42516273] (RSC advances, 2026) Experimental study and thermodynamic modelling of the Nb-Sb system. Thermodynamic modelling of the Nb-Sb system was performed by the CALPHAD method, based on SGTE data of the Gibbs energy for pure elements, as well as on data from experimental…
- `PMID:42455354` (esearch) — **Structural and biochemical characterization of a novel DinG containing an endonuclease domain.** — *Cellular and molecular life sciences : CMLS · 2026*
  - [PMID 42455354] (Cellular and molecular life sciences : CMLS, 2026) Structural and biochemical characterization of a novel DinG containing an endonuclease domain. DinG-like proteins are members of the XPD-family SF2 helicases and are widely distributed in bacteria, yet they exhib…

</details>

<sub>KG: 32 entities / 86 relations · 22 references (15 PubMed) · 36 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** ERCC1, GSTP1, GSTM3

Cisplatin-induced peripheral neuropathy is influenced by genetic polymorphisms such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735). These variants likely affect the drug's metabolism, DNA repair mechanisms, or cellular sensitivity to cisplatin, thereby modulating the risk of developing peripheral neuropathy. For drug discovery and patient safety, pre-treatment genetic screening for these polymorphisms can help predict susceptibility to adverse effects, allowing for dose adjustments or alternative therapeutic strategies to mitigate risks.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM3/rs1799735:L3` — GSTM3 (rs1799735): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs735482:L3` — ERCC1 (rs735482): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:CASP7/rs7921977:L3` — CASP7 (rs7921977): PharmGKB evidence level 3 linking it to gemcitabine-related Non-Small Cell Lung Carcinoma. ClinPGx relationship: ambiguous.
- `ClinPGx:CASP7/rs2227310:L3` — CASP7 (rs2227310): PharmGKB evidence level 3 linking it to gemcitabine-related Non-Small Cell Lung Carcinoma. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:19620936` (clinpgx_citation) — **Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes.** — *Pharmacogenetics and genomics · 2009*
  - [PMID 19620936] (Pharmacogenetics and genomics, 2009) Cisplatin pharmacogenetics, DNA repair polymorphisms, and esophageal cancer outcomes. Genetic variations or polymorphisms within genes of the nucleotide excision repair (NER) pathway alter DNA repair capacity. Reduced DNA repa…
- `PMID:42598682` (esearch) — **Ultrasound-Guided Perineural Corticosteroid Injection and Dextrose Hydrodissection for Carpal Tunnel Syndrome: Current Evidence and Clinical Considerations.** — *Cureus · 2026*
  - [PMID 42598682] (Cureus, 2026) Ultrasound-Guided Perineural Corticosteroid Injection and Dextrose Hydrodissection for Carpal Tunnel Syndrome: Current Evidence and Clinical Considerations. Carpal tunnel syndrome (CTS) is the most common entrapment neuropathy and represents a subst…
- `PMID:42598352` (esearch) — **Effectiveness of Buerger Allen Exercise as an Adjunct to Standard Pharmacotherapy in Reducing Peripheral Neuropathy Symptoms Among Patients with Type 2 Diabetes Mellitus: A Randomized Controlled Pilot Study.** — *Journal of pharmacy & bioallied sciences · 2026*
  - [PMID 42598352] (Journal of pharmacy & bioallied sciences, 2026) Effectiveness of Buerger Allen Exercise as an Adjunct to Standard Pharmacotherapy in Reducing Peripheral Neuropathy Symptoms Among Patients with Type 2 Diabetes Mellitus: A Randomized Controlled Pilot Study. Diabeti…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:19786980` (clinpgx_citation) — **Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients.** — *The pharmacogenomics journal · 2010*
  - [PMID 19786980] (The pharmacogenomics journal, 2010) Genetic polymorphisms and the efficacy and toxicity of cisplatin-based chemotherapy in ovarian cancer patients. Platinum drugs are among the most active and widely used agents in the treatment of different cancers. However, the…
- `PMID:22188361` (clinpgx_citation) — **Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins.** — *Pharmacogenomics · 2012*
  - [PMID 22188361] (Pharmacogenomics, 2012) Pharmacogenomics of cisplatin-based chemotherapy in ovarian cancer patients of different ethnic origins. There is a substantial difference between Asians and Caucasians in their reaction to platinum drugs. To determine whether population-r…
- `PMID:22441531` (clinpgx_citation) — **Association of CASP7 polymorphisms and survival of patients with non-small cell lung cancer with platinum-based chemotherapy treatment.** — *Chest · 2012*
  - [PMID 22441531] (Chest, 2012) Association of CASP7 polymorphisms and survival of patients with non-small cell lung cancer with platinum-based chemotherapy treatment. CASP7 plays a crucial role in cancer development and chemotherapy efficacy. We, therefore, explored whether single…
- `PMID:42598812` (esearch) — **MLN4924 suppresses pancreatic cancer progression and enhances chemosensitivity to gemcitabine by targeting the PTGS2/EGFR-PI3K/Akt/mTOR signaling axis.** — *Anti-cancer drugs · 2026*
  - [PMID 42598812] (Anti-cancer drugs, 2026) MLN4924 suppresses pancreatic cancer progression and enhances chemosensitivity to gemcitabine by targeting the PTGS2/EGFR-PI3K/Akt/mTOR signaling axis. Pancreatic cancer is a highly lethal digestive malignancy characterized by insidious o…
- `PMID:42599160` (esearch) — **The pan-tumor landscape, allelic status, and genomic complexity of SMARCA4 alterations.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2026*
  - [PMID 42599160] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2026) The pan-tumor landscape, allelic status, and genomic complexity of SMARCA4 alterations. The clinical implications of distinct SMARCA4 alteration classes remain i…
- `PMID:42598915` (esearch) — **TLS as Predictors and Targets in Neoadjuvant Chemoimmunotherapy for NSCLC.** — *Thoracic cancer · 2026*
  - [PMID 42598915] (Thoracic cancer, 2026) TLS as Predictors and Targets in Neoadjuvant Chemoimmunotherapy for NSCLC. Tertiary lymphoid structures (TLS) have emerged as critical modulators of antitumor immunity in non-small cell lung cancer (NSCLC), with growing evidence supporting …
- `PMID:42516273` (esearch) — **Experimental study and thermodynamic modelling of the Nb-Sb system.** — *RSC advances · 2026*
  - [PMID 42516273] (RSC advances, 2026) Experimental study and thermodynamic modelling of the Nb-Sb system. Thermodynamic modelling of the Nb-Sb system was performed by the CALPHAD method, based on SGTE data of the Gibbs energy for pure elements, as well as on data from experimental…
- `PMID:42455354` (esearch) — **Structural and biochemical characterization of a novel DinG containing an endonuclease domain.** — *Cellular and molecular life sciences : CMLS · 2026*
  - [PMID 42455354] (Cellular and molecular life sciences : CMLS, 2026) Structural and biochemical characterization of a novel DinG containing an endonuclease domain. DinG-like proteins are members of the XPD-family SF2 helicases and are widely distributed in bacteria, yet they exhib…

</details>

<sub>KG: 32 entities / 86 relations · 22 references (15 PubMed) · 36 retrieval events</sub>

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** SLC28A3 (rs7853758), GSTP1 (rs1695)

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors, particularly variants within the SLC28A3 (rs7853758) gene. This variant is associated with a reduced risk of anthracycline-induced cardiotoxicity, suggesting that its absence could contribute to increased susceptibility to doxorubicin's adverse effects. Additionally, polymorphisms in GSTP1 (rs1695) have been linked to heightened sensitivity to doxorubicin-related cardiotoxicity. These findings underscore the importance of genetic screening for these variants before initiating treatment with doxorubicin to identify patients at higher risk and potentially adjust dosing or consider alternative therapeutic options.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:MTHFR/rs1801133:L2A` — MTHFR (rs1801133): PharmGKB evidence level 2A linking it to methotrexate-related Acute lymphoblastic leukemia, Drug Toxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2B6/CYP2B6*1:L3` — CYP2B6 (CYP2B6*1): PharmGKB evidence level 3 linking it to cyclophosphamide-related Lymphoma, B-Cell. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2D6/CYP2D6*1:L1A` — CYP2D6 (CYP2D6*1): PharmGKB evidence level 1A linking it to venlafaxine-related Agitation, Alcohol-Related Disorders. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:11418485` (clinpgx_citation) — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - [PMID 11418485] (Blood, 2001) Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism. This study investigated whether a polymorphism in the 5,10-methylenetetrahydrofolate reductase (M…
- `PMID:11710708` (clinpgx_citation) — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - [PMID 11710708] (Arthritis and rheumatism, 2001) The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients. To study the possible relationship between the C677T mu…
- `PMID:42599106` (esearch) — **An acceptance-based healthy lifestyle programme for community-dwelling patients with pneumoconiosis: A waitlist pilot randomised controlled trial.** — *Pulmonology · 2026*
  - [PMID 42599106] (Pulmonology, 2026) An acceptance-based healthy lifestyle programme for community-dwelling patients with pneumoconiosis: A waitlist pilot randomised controlled trial. Respiratory symptoms such as cough and shortness of breath are prevalent among patients with pneu…
- `PMID:42598580` (esearch) — **Pneumomediastinum After Third Molar Surgery: A Case Report.** — *Cureus · 2026*
  - [PMID 42598580] (Cureus, 2026) Pneumomediastinum After Third Molar Surgery: A Case Report. Cervicofacial emphysema is defined as the pathological presence of air within the fascial spaces of the neck and face. Dental procedures are a recognized but uncommon cause, and only rarely…
- `PMID:10233212` (clinpgx_citation) — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - [PMID 10233212] (British journal of clinical pharmacology, 1999) Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers. Interindividual differences in the pharmacokinetics of venlafaxine, a new antidepressant, were shown during early clinica…
- `PMID:10774634` (clinpgx_citation) — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - [PMID 10774634] (Therapeutic drug monitoring, 2000) Venlafaxine serum levels and CYP2D6 genotype. Thirty-three patients with depression treated with 225 mg venlafaxine were genotyped for the polymorphic enzyme, debrisoquine 4-hydroxylase (CYP2D6). The relationship between drug an…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:32587261` (clinpgx_citation) — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - [PMID 32587261] (Scientific reports, 2020) Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes. Doxorubicin is a potent anticancer drug used to treat a variety of cancer types. H…

</details>

<sub>KG: 18 entities / 68 relations · 22 references (13 PubMed) · 39 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** SLC28A3 (rs7853758), GSTP1 (rs1695)

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors, particularly variants within the SLC28A3 (rs7853758) gene. This variant is associated with a reduced risk of anthracycline-induced cardiotoxicity, suggesting that its absence could contribute to increased susceptibility to doxorubicin's adverse effects. Additionally, polymorphisms in GSTP1 (rs1695) have been linked to heightened sensitivity to doxorubicin-related cardiotoxicity. These findings underscore the importance of genetic screening for these variants before initiating treatment with doxorubicin to identify patients at higher risk and potentially adjust dosing or consider alternative therapeutic options.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:MTHFR/rs1801133:L2A` — MTHFR (rs1801133): PharmGKB evidence level 2A linking it to methotrexate-related Acute lymphoblastic leukemia, Drug Toxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2B6/CYP2B6*1:L3` — CYP2B6 (CYP2B6*1): PharmGKB evidence level 3 linking it to cyclophosphamide-related Lymphoma, B-Cell. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2D6/CYP2D6*1:L1A` — CYP2D6 (CYP2D6*1): PharmGKB evidence level 1A linking it to venlafaxine-related Agitation, Alcohol-Related Disorders. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:11418485` (clinpgx_citation) — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - [PMID 11418485] (Blood, 2001) Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism. This study investigated whether a polymorphism in the 5,10-methylenetetrahydrofolate reductase (M…
- `PMID:11710708` (clinpgx_citation) — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - [PMID 11710708] (Arthritis and rheumatism, 2001) The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients. To study the possible relationship between the C677T mu…
- `PMID:42599106` (esearch) — **An acceptance-based healthy lifestyle programme for community-dwelling patients with pneumoconiosis: A waitlist pilot randomised controlled trial.** — *Pulmonology · 2026*
  - [PMID 42599106] (Pulmonology, 2026) An acceptance-based healthy lifestyle programme for community-dwelling patients with pneumoconiosis: A waitlist pilot randomised controlled trial. Respiratory symptoms such as cough and shortness of breath are prevalent among patients with pneu…
- `PMID:42598580` (esearch) — **Pneumomediastinum After Third Molar Surgery: A Case Report.** — *Cureus · 2026*
  - [PMID 42598580] (Cureus, 2026) Pneumomediastinum After Third Molar Surgery: A Case Report. Cervicofacial emphysema is defined as the pathological presence of air within the fascial spaces of the neck and face. Dental procedures are a recognized but uncommon cause, and only rarely…
- `PMID:10233212` (clinpgx_citation) — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - [PMID 10233212] (British journal of clinical pharmacology, 1999) Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers. Interindividual differences in the pharmacokinetics of venlafaxine, a new antidepressant, were shown during early clinica…
- `PMID:10774634` (clinpgx_citation) — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - [PMID 10774634] (Therapeutic drug monitoring, 2000) Venlafaxine serum levels and CYP2D6 genotype. Thirty-three patients with depression treated with 225 mg venlafaxine were genotyped for the polymorphic enzyme, debrisoquine 4-hydroxylase (CYP2D6). The relationship between drug an…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:28763429` (clinpgx_citation) — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - [PMID 28763429] (Pharmacogenetics and genomics, 2017) Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial. The major clinical side effect of the ERBB2-targeted breast cancer therapy, trastuzumab, is a decline in the left ventri…

</details>

<sub>KG: 18 entities / 68 relations · 22 references (13 PubMed) · 39 retrieval events</sub>

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** SLC28A3 (rs7853758), RARG (rs2229774), GSTP1 (rs1695)

The genes/variants implicated in anthracycline-induced cardiotoxicity include SLC28A3 (rs7853758), RARG (rs2229774), and GSTP1 (rs1695). SLC28A3 (rs7853758) is a protective variant, reducing the risk of cardiotoxicity in childhood cancer survivors. The biological mechanism likely involves altered nucleoside transport or metabolism affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help identify high-risk patients who may benefit from dose adjustments or alternative agents with lower cardiotoxic potential.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to anthracycline-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to anthracycline-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to anthracycline-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: associated.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MTHFR/rs1801133:L2A` — MTHFR (rs1801133): PharmGKB evidence level 2A linking it to methotrexate-related Acute lymphoblastic leukemia, Drug Toxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCC3/rs4148416:L3` — ABCC3 (rs4148416): PharmGKB evidence level 3 linking it to cisplatin-related Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:DPYD/rs17376848:L1A` — DPYD (rs17376848): PharmGKB evidence level 1A linking it to capecitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:DPYD/rs2297595:L1A` — DPYD (rs2297595): PharmGKB evidence level 1A linking it to capecitabine-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:35147047` (clinpgx_citation) — **Pharmacogenomic study of anthracycline-induced cardiotoxicity in Mexican pediatric patients.** — *Pharmacogenomics · 2022*
  - [PMID 35147047] (Pharmacogenomics, 2022) Pharmacogenomic study of anthracycline-induced cardiotoxicity in Mexican pediatric patients. Background: The aim of this study was to evaluate the association between well-defined genetic risk variants in SLC28A3, RARG and UGT1A6 and anthr…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:32587261` (clinpgx_citation) — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - [PMID 32587261] (Scientific reports, 2020) Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes. Doxorubicin is a potent anticancer drug used to treat a variety of cancer types. H…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:11418485` (clinpgx_citation) — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - [PMID 11418485] (Blood, 2001) Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism. This study investigated whether a polymorphism in the 5,10-methylenetetrahydrofolate reductase (M…
- `PMID:11710708` (clinpgx_citation) — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - [PMID 11710708] (Arthritis and rheumatism, 2001) The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients. To study the possible relationship between the C677T mu…
- `PMID:12209976` (clinpgx_citation) — **Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation.** — *International journal of cancer · 2002*
  - [PMID 12209976] (International journal of cancer, 2002) Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation. Dihydropyrimidine dehydrogenase (DPD) is the init…
- `PMID:17000685` (clinpgx_citation) — **Pharmacogenetics of capecitabine in advanced breast cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 17000685] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Pharmacogenetics of capecitabine in advanced breast cancer patients. Germinal gene polymorphisms can explain a part of the interpatient pharmacodynamic variabili…
- `PMID:42598301` (esearch) — **Risk of fracture among lung cancer survivors by cancer treatment modality: A population-based retrospective cohort study.** — *Journal of bone oncology · 2026*
  - [PMID 42598301] (Journal of bone oncology, 2026) Risk of fracture among lung cancer survivors by cancer treatment modality: A population-based retrospective cohort study. Evidence on fracture incidence among lung cancer (LC) survivors remains limited. We assessed fracture risk in…
- `PMID:42597694` (esearch) — **Improving Survival Prediction of Head and Neck Cancer Patients by Modeling Long-term Symptom Burden.** — *Proceedings. IEEE International Conference on Healthcare Informatics · 2026*
  - [PMID 42597694] (Proceedings. IEEE International Conference on Healthcare Informatics, 2026) Improving Survival Prediction of Head and Neck Cancer Patients by Modeling Long-term Symptom Burden. Accurate survival prediction in head and neck cancer (HNC) is essential for effective …

</details>

<sub>KG: 15 entities / 51 relations · 22 references (13 PubMed) · 35 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** SLC28A3 (rs7853758), GSTP1 (rs1695), RARG (rs2229774)

The genetic variants SLC28A3 (rs7853758), GSTP1 (rs1695), and RARG (rs2229774) are implicated in anthracycline-induced cardiotoxicity, with SLC28A3 (rs7853758) showing the strongest protective effect. The biological mechanism likely involves altered nucleoside transport or metabolism affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment screening for these variants can help identify patients at higher risk of cardiotoxicity, allowing for dose adjustments or alternative agent selection to mitigate adverse effects.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to anthracycline-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to anthracycline-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to anthracycline-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:MTHFR/rs1801133:L2A` — MTHFR (rs1801133): PharmGKB evidence level 2A linking it to methotrexate-related Acute lymphoblastic leukemia, Drug Toxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCC3/rs4148416:L3` — ABCC3 (rs4148416): PharmGKB evidence level 3 linking it to cisplatin-related Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:DPYD/rs17376848:L1A` — DPYD (rs17376848): PharmGKB evidence level 1A linking it to capecitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:DPYD/rs2297595:L1A` — DPYD (rs2297595): PharmGKB evidence level 1A linking it to capecitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:UGT1A6/rs6759892:L3` — UGT1A6 (rs6759892): PharmGKB evidence level 3 linking it to deferiprone-related Beta-thalassemia and related diseases. ClinPGx relationship: ambiguous.
- `ClinPGx:UGT1A6/rs2070959:L3` — UGT1A6 (rs2070959): PharmGKB evidence level 3 linking it to irinotecan-related Colorectal Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to phenytoin-related Dosage. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:28763429` (clinpgx_citation) — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - [PMID 28763429] (Pharmacogenetics and genomics, 2017) Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial. The major clinical side effect of the ERBB2-targeted breast cancer therapy, trastuzumab, is a decline in the left ventri…
- `PMID:11418485` (clinpgx_citation) — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - [PMID 11418485] (Blood, 2001) Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism. This study investigated whether a polymorphism in the 5,10-methylenetetrahydrofolate reductase (M…
- `PMID:11710708` (clinpgx_citation) — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - [PMID 11710708] (Arthritis and rheumatism, 2001) The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients. To study the possible relationship between the C677T mu…
- `PMID:12209976` (clinpgx_citation) — **Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation.** — *International journal of cancer · 2002*
  - [PMID 12209976] (International journal of cancer, 2002) Increased risk of grade IV neutropenia after administration of 5-fluorouracil due to a dihydropyrimidine dehydrogenase deficiency: high prevalence of the IVS14+1g>a mutation. Dihydropyrimidine dehydrogenase (DPD) is the init…
- `PMID:17000685` (clinpgx_citation) — **Pharmacogenetics of capecitabine in advanced breast cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 17000685] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Pharmacogenetics of capecitabine in advanced breast cancer patients. Germinal gene polymorphisms can explain a part of the interpatient pharmacodynamic variabili…
- `PMID:24036429` (clinpgx_citation) — **Three most common nonsynonymous UGT1A6*2 polymorphisms (Thr181Ala, Arg184Ser and Ser7Ala) and therapeutic response to deferiprone in β-thalassemia major patients.** — *Gene · 2013*
  - [PMID 24036429] (Gene, 2013) Three most common nonsynonymous UGT1A6*2 polymorphisms (Thr181Ala, Arg184Ser and Ser7Ala) and therapeutic response to deferiprone in β-thalassemia major patients. Deferiprone is used as a chelation agent in chronic iron overload in β-thalassemia patie…
- `PMID:18349289` (clinpgx_citation) — **Gilbert's Syndrome and irinotecan toxicity: combination with UDP-glucuronosyltransferase 1A7 variants increases risk.** — *Cancer epidemiology, biomarkers & prevention : a publication of the American Association for Cancer Research, cosponsored by the American Society of Preventive Oncology · 2008*
  - [PMID 18349289] (Cancer epidemiology, biomarkers & prevention : a publication of the American Association for Cancer Research, cosponsored by the American Society of Preventive Oncology, 2008) Gilbert's Syndrome and irinotecan toxicity: combination with UDP-glucuronosyltransferas…
- `PMID:15805193` (clinpgx_citation) — **Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin.** — *Proceedings of the National Academy of Sciences of the United States of America · 2005*
  - [PMID 15805193] (Proceedings of the National Academy of Sciences of the United States of America, 2005) Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin. Phenytoin and carbamazepine are effective …
- `PMID:16220110` (clinpgx_citation) — **CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population.** — *Pharmacogenetics and genomics · 2005*
  - [PMID 16220110] (Pharmacogenetics and genomics, 2005) CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population. The genetically polymorphic cytochrome P450 2C9 (CYP2C9) metabolizes many important drugs. Among them, phenytoin has …

</details>

<sub>KG: 16 entities / 65 relations · 27 references (15 PubMed) · 41 retrieval events</sub>

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** CYP2D6*4, SLC28A3

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may alter drug metabolism and increase cardiotoxicity risk. Although there's no direct pharmacogenomic link between CYP2D6 and doxorubicin, the prolonged exposure to higher levels of doxorubicin due to reduced clearance could exacerbate cardiac side effects. Additionally, screening for SLC28A3 variants like rs7853758 might provide further insights into cardiotoxicity risk. For drug discovery and patient safety, pre-treatment genetic testing should be considered to identify high-risk patients who may benefit from dose adjustments or alternative treatments.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2D6/CYP2D6*1:L1A` — CYP2D6 (CYP2D6*1): PharmGKB evidence level 1A linking it to hydrocodone-related Metabolism/PK. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:12920424` (clinpgx_citation) — **Adverse drug reactions to oxycodone and hydrocodone in CYP2D6 ultrarapid metabolizers.** — *Journal of clinical psychopharmacology · 2003*
  - [PMID 12920424] (Journal of clinical psychopharmacology, 2003) Adverse drug reactions to oxycodone and hydrocodone in CYP2D6 ultrarapid metabolizers.…
- `PMID:14998425` (clinpgx_citation) — **CYP2D6 and CYP3A4 involvement in the primary oxidative metabolism of hydrocodone by human liver microsomes.** — *British journal of clinical pharmacology · 2004*
  - [PMID 14998425] (British journal of clinical pharmacology, 2004) CYP2D6 and CYP3A4 involvement in the primary oxidative metabolism of hydrocodone by human liver microsomes. To determine the Michaelis-Menten kinetics of hydrocodone metabolism to its O- and N-demethylated products,…
- `PMID:42599271` (esearch) — **High-Grade Myoepithelial Carcinoma with EWSR1::CREB1 Fusion in the Submandibular Gland of a Young Man: Salivary or Soft Tissue Type?** — *International journal of surgical pathology · 2026*
  - [PMID 42599271] (International journal of surgical pathology, 2026) High-Grade Myoepithelial Carcinoma with EWSR1::CREB1 Fusion in the Submandibular Gland of a Young Man: Salivary or Soft Tissue Type? Myoepithelial carcinoma is an uncommon malignant tumor of neoplastic myoepithel…
- `PMID:42599237` (esearch) — **[Effect of ESR1 Somatic Mutations on SERM/SERD Binding: Insights from Molecular Docking and Molecular Dynamics Simulations].** — *Molekuliarnaia biologiia · 2026*
  - [PMID 42599237] (Molekuliarnaia biologiia, 2026) [Effect of ESR1 Somatic Mutations on SERM/SERD Binding: Insights from Molecular Docking and Molecular Dynamics Simulations]. Acquired resistance to endocrine therapy poses a major limitation in the treatment of estrogen receptor (E…
- `PMID:10233212` (clinpgx_citation) — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - [PMID 10233212] (British journal of clinical pharmacology, 1999) Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers. Interindividual differences in the pharmacokinetics of venlafaxine, a new antidepressant, were shown during early clinica…
- `PMID:10774634` (clinpgx_citation) — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - [PMID 10774634] (Therapeutic drug monitoring, 2000) Venlafaxine serum levels and CYP2D6 genotype. Thirty-three patients with depression treated with 225 mg venlafaxine were genotyped for the polymorphic enzyme, debrisoquine 4-hydroxylase (CYP2D6). The relationship between drug an…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:32587261` (clinpgx_citation) — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - [PMID 32587261] (Scientific reports, 2020) Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes. Doxorubicin is a potent anticancer drug used to treat a variety of cancer types. H…

</details>

<sub>KG: 15 entities / 74 relations · 20 references (13 PubMed) · 39 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** CYP2D6*4, SLC28A3

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may alter drug metabolism and increase cardiotoxicity risk. Although there's no direct pharmacogenomic link between CYP2D6 and doxorubicin, the prolonged exposure to higher levels of doxorubicin due to reduced clearance could exacerbate cardiac side effects. Additionally, screening for SLC28A3 variants like rs7853758 might provide further insights into cardiotoxicity risk. For drug discovery and patient safety, pre-treatment genetic testing should be considered to identify high-risk patients who may benefit from dose adjustments or alternative treatments.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2D6/CYP2D6*1:L1A` — CYP2D6 (CYP2D6*1): PharmGKB evidence level 1A linking it to hydrocodone-related Metabolism/PK. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:12920424` (clinpgx_citation) — **Adverse drug reactions to oxycodone and hydrocodone in CYP2D6 ultrarapid metabolizers.** — *Journal of clinical psychopharmacology · 2003*
  - [PMID 12920424] (Journal of clinical psychopharmacology, 2003) Adverse drug reactions to oxycodone and hydrocodone in CYP2D6 ultrarapid metabolizers.…
- `PMID:14998425` (clinpgx_citation) — **CYP2D6 and CYP3A4 involvement in the primary oxidative metabolism of hydrocodone by human liver microsomes.** — *British journal of clinical pharmacology · 2004*
  - [PMID 14998425] (British journal of clinical pharmacology, 2004) CYP2D6 and CYP3A4 involvement in the primary oxidative metabolism of hydrocodone by human liver microsomes. To determine the Michaelis-Menten kinetics of hydrocodone metabolism to its O- and N-demethylated products,…
- `PMID:42599271` (esearch) — **High-Grade Myoepithelial Carcinoma with EWSR1::CREB1 Fusion in the Submandibular Gland of a Young Man: Salivary or Soft Tissue Type?** — *International journal of surgical pathology · 2026*
  - [PMID 42599271] (International journal of surgical pathology, 2026) High-Grade Myoepithelial Carcinoma with EWSR1::CREB1 Fusion in the Submandibular Gland of a Young Man: Salivary or Soft Tissue Type? Myoepithelial carcinoma is an uncommon malignant tumor of neoplastic myoepithel…
- `PMID:42599237` (esearch) — **[Effect of ESR1 Somatic Mutations on SERM/SERD Binding: Insights from Molecular Docking and Molecular Dynamics Simulations].** — *Molekuliarnaia biologiia · 2026*
  - [PMID 42599237] (Molekuliarnaia biologiia, 2026) [Effect of ESR1 Somatic Mutations on SERM/SERD Binding: Insights from Molecular Docking and Molecular Dynamics Simulations]. Acquired resistance to endocrine therapy poses a major limitation in the treatment of estrogen receptor (E…
- `PMID:10233212` (clinpgx_citation) — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - [PMID 10233212] (British journal of clinical pharmacology, 1999) Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers. Interindividual differences in the pharmacokinetics of venlafaxine, a new antidepressant, were shown during early clinica…
- `PMID:10774634` (clinpgx_citation) — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - [PMID 10774634] (Therapeutic drug monitoring, 2000) Venlafaxine serum levels and CYP2D6 genotype. Thirty-three patients with depression treated with 225 mg venlafaxine were genotyped for the polymorphic enzyme, debrisoquine 4-hydroxylase (CYP2D6). The relationship between drug an…
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:28763429` (clinpgx_citation) — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - [PMID 28763429] (Pharmacogenetics and genomics, 2017) Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial. The major clinical side effect of the ERBB2-targeted breast cancer therapy, trastuzumab, is a decline in the left ventri…

</details>

<sub>KG: 15 entities / 74 relations · 20 references (13 PubMed) · 39 retrieval events</sub>

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** GSTM1, SLC28A3 (rs7853758)

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by genetic factors such as the GSTM1 genotype and a synonymous coding variant rs7853758 within the SLC28A3 gene. These genetic variations may modulate an individual's susceptibility to doxorubicin-induced cardiotoxicity through mechanisms that affect drug metabolism, transport, or cellular response pathways. For future drug discovery efforts and patient safety, pre-treatment biomarker screening for these variants could help identify patients at higher risk of developing heart damage from Adriamycin, enabling dose adjustments or the use of alternative therapies to mitigate this risk.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2D6/CYP2D6*1:L1A` — CYP2D6 (CYP2D6*1): PharmGKB evidence level 1A linking it to venlafaxine-related Agitation, Alcohol-Related Disorders. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:42598455` (esearch) — **Endovascular technology for aortic arch repair: from innovation to integration.** — *Annals of cardiothoracic surgery · 2026*
  - [PMID 42598455] (Annals of cardiothoracic surgery, 2026) Endovascular technology for aortic arch repair: from innovation to integration. Treatment of aortic arch pathology is one of the most challenging areas in cardiovascular surgery due to the complex anatomy and proximity to c…
- `PMID:42597513` (esearch) — **Risk factors for cardiac dysfunction caused by anthracycline drugs in the treatment of lymphoma and the early monitoring value of three-dimensional echocardiography.** — *American journal of cancer research · 2026*
  - [PMID 42597513] (American journal of cancer research, 2026) Risk factors for cardiac dysfunction caused by anthracycline drugs in the treatment of lymphoma and the early monitoring value of three-dimensional echocardiography. Anthracyclines (ANTs) are important chemotherapeutic d…
- `PMID:10233212` (clinpgx_citation) — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - [PMID 10233212] (British journal of clinical pharmacology, 1999) Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers. Interindividual differences in the pharmacokinetics of venlafaxine, a new antidepressant, were shown during early clinica…
- `PMID:10774634` (clinpgx_citation) — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - [PMID 10774634] (Therapeutic drug monitoring, 2000) Venlafaxine serum levels and CYP2D6 genotype. Thirty-three patients with depression treated with 225 mg venlafaxine were genotyped for the polymorphic enzyme, debrisoquine 4-hydroxylase (CYP2D6). The relationship between drug an…
- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:32587261` (clinpgx_citation) — **Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes.** — *Scientific reports · 2020*
  - [PMID 32587261] (Scientific reports, 2020) Variation in RARG increases susceptibility to doxorubicin-induced cardiotoxicity in patient specific induced pluripotent stem cell-derived cardiomyocytes. Doxorubicin is a potent anticancer drug used to treat a variety of cancer types. H…

</details>

<sub>KG: 16 entities / 65 relations · 21 references (13 PubMed) · 39 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** GSTM1, SLC28A3 (rs7853758)

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by genetic factors such as the GSTM1 genotype and a synonymous coding variant rs7853758 within the SLC28A3 gene. These genetic variations may modulate an individual's susceptibility to doxorubicin-induced cardiotoxicity through mechanisms that affect drug metabolism, transport, or cellular response pathways. For future drug discovery efforts and patient safety, pre-treatment biomarker screening for these variants could help identify patients at higher risk of developing heart damage from Adriamycin, enabling dose adjustments or the use of alternative therapies to mitigate this risk.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:RARG/rs2229774:L3` — RARG (rs2229774): PharmGKB evidence level 3 linking it to doxorubicin-related Cardiotoxicity, Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:CYP2D6/CYP2D6*1:L1A` — CYP2D6 (CYP2D6*1): PharmGKB evidence level 1A linking it to venlafaxine-related Agitation, Alcohol-Related Disorders. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTM1/GSTM1 non-null:L3` — GSTM1 (GSTM1 non-null): PharmGKB evidence level 3 linking it to cisplatin-related Deafness, Ototoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC28A3/rs7867504:L3` — SLC28A3 (rs7867504): PharmGKB evidence level 3 linking it to gemcitabine-related Neoplasms. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1138272:L3` — GSTP1 (rs1138272): PharmGKB evidence level 3 linking it to cisplatin-related Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:25823784` (clinpgx_citation) — **Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma.** — *Pharmacogenomics · 2015*
  - [PMID 25823784] (Pharmacogenomics, 2015) Association of NADPH oxidase polymorphisms with anthracycline-induced cardiotoxicity in the RICOVER-60 trial of patients with aggressive CD20(+) B-cell lymphoma. To identify gene variants responsible for anthracycline-induced cardiotoxicit…
- `PMID:42598455` (esearch) — **Endovascular technology for aortic arch repair: from innovation to integration.** — *Annals of cardiothoracic surgery · 2026*
  - [PMID 42598455] (Annals of cardiothoracic surgery, 2026) Endovascular technology for aortic arch repair: from innovation to integration. Treatment of aortic arch pathology is one of the most challenging areas in cardiovascular surgery due to the complex anatomy and proximity to c…
- `PMID:42597513` (esearch) — **Risk factors for cardiac dysfunction caused by anthracycline drugs in the treatment of lymphoma and the early monitoring value of three-dimensional echocardiography.** — *American journal of cancer research · 2026*
  - [PMID 42597513] (American journal of cancer research, 2026) Risk factors for cardiac dysfunction caused by anthracycline drugs in the treatment of lymphoma and the early monitoring value of three-dimensional echocardiography. Anthracyclines (ANTs) are important chemotherapeutic d…
- `PMID:10233212` (clinpgx_citation) — **Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers.** — *British journal of clinical pharmacology · 1999*
  - [PMID 10233212] (British journal of clinical pharmacology, 1999) Effect of the CYP2D6*10 genotype on venlafaxine pharmacokinetics in healthy adult volunteers. Interindividual differences in the pharmacokinetics of venlafaxine, a new antidepressant, were shown during early clinica…
- `PMID:10774634` (clinpgx_citation) — **Venlafaxine serum levels and CYP2D6 genotype.** — *Therapeutic drug monitoring · 2000*
  - [PMID 10774634] (Therapeutic drug monitoring, 2000) Venlafaxine serum levels and CYP2D6 genotype. Thirty-three patients with depression treated with 225 mg venlafaxine were genotyped for the polymorphic enzyme, debrisoquine 4-hydroxylase (CYP2D6). The relationship between drug an…
- `PMID:17228018` (clinpgx_citation) — **Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2007*
  - [PMID 17228018] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2007) Cisplatin-induced long-term hearing impairment is associated with specific glutathione s-transferase genotypes in testicular cancer survivors. Cisplatin, a corners…
- `PMID:20530282` (clinpgx_citation) — **Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup Trial N9741.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2010*
  - [PMID 20530282] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2010) Pharmacogenetic predictors of adverse events and response to chemotherapy in metastatic colorectal cancer: results from North American Gastrointestinal Intergroup …
- `PMID:15213713` (clinpgx_citation) — **A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer.** — *British journal of cancer · 2004*
  - [PMID 15213713] (British journal of cancer, 2004) A multivariate analysis of genomic polymorphisms: prediction of clinical outcome to 5-FU/oxaliplatin combination chemotherapy in refractory colorectal cancer. In this marker evaluation study, we tested whether distinct patterns of…
- `PMID:16707601` (clinpgx_citation) — **Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2006*
  - [PMID 16707601] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2006) Glutathione S-transferase P1 polymorphism (Ile105Val) predicts cumulative neuropathy in patients receiving oxaliplatin-based chemotherapy. Glutathione S-transfer…
- `PMID:26237429` (clinpgx_citation) — **A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer.** — *Nature genetics · 2015*
  - [PMID 26237429] (Nature genetics, 2015) A coding variant in RARG confers susceptibility to anthracycline-induced cardiotoxicity in childhood cancer. Anthracyclines are used in over 50% of childhood cancer treatment protocols, but their clinical usefulness is limited by anthracycl…
- `PMID:28763429` (clinpgx_citation) — **Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial.** — *Pharmacogenetics and genomics · 2017*
  - [PMID 28763429] (Pharmacogenetics and genomics, 2017) Genome-wide association study of cardiotoxicity in the NCCTG N9831 (Alliance) adjuvant trastuzumab trial. The major clinical side effect of the ERBB2-targeted breast cancer therapy, trastuzumab, is a decline in the left ventri…

</details>

<sub>KG: 16 entities / 65 relations · 21 references (13 PubMed) · 39 retrieval events</sub>

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

#### Phase 4 — ClinPGx + PubMed check

**Genes surfaced:** ERCC1 (rs11615), CYBA (rs4673)

Doxorubicin-induced mucositis is associated with genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing susceptibility to this adverse effect. The biological mechanism likely involves impaired DNA repair or oxidative stress responses due to these genetic variations, leading to heightened toxicity from doxorubicin. For drug discovery and patient safety, pre-treatment screening for these variants could inform personalized dosing strategies or identify patients at higher risk who might benefit from mucositis prophylaxis or alternative therapies.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to doxorubicin-related Mucositis, Osteosarcoma. ClinPGx relationship: associated.
- `ClinPGx:CYBA/rs4673:L3` — CYBA (rs4673): PharmGKB evidence level 3 linking it to doxorubicin-related Anemia, Mucositis. ClinPGx relationship: associated.
- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:MTHFR/rs1801133:L2A` — MTHFR (rs1801133): PharmGKB evidence level 2A linking it to methotrexate-related Acute lymphoblastic leukemia, Drug Toxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs735482:L3` — ERCC1 (rs735482): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:ABCC3/rs4148416:L3` — ABCC3 (rs4148416): PharmGKB evidence level 3 linking it to cisplatin-related Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC19A1/rs1051266:L2A` — SLC19A1 (rs1051266): PharmGKB evidence level 2A linking it to methotrexate-related Rheumatoid arthritis. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked</summary>

- `PMID:21887680` (clinpgx_citation) — **Germline genetic polymorphisms may influence chemotherapy response and disease outcome in osteosarcoma: a pilot study.** — *Cancer · 2012*
  - [PMID 21887680] (Cancer, 2012) Germline genetic polymorphisms may influence chemotherapy response and disease outcome in osteosarcoma: a pilot study. Osteosarcoma is the most common malignant bone tumor in children and young people. Efficacy of multiagent MAP (methotrexate, doxor…
- `PMID:29507678` (clinpgx_citation) — **Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients.** — *Oncotarget · 2018*
  - [PMID 29507678] (Oncotarget, 2018) Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients. The differences in patients' response to the same medication, toxicity included, are one of the major problems in breast can…
- `PMID:16330681` (clinpgx_citation) — **NAD(P)H oxidase and multidrug resistance protein genetic polymorphisms are associated with doxorubicin-induced cardiotoxicity.** — *Circulation · 2005*
  - [PMID 16330681] (Circulation, 2005) NAD(P)H oxidase and multidrug resistance protein genetic polymorphisms are associated with doxorubicin-induced cardiotoxicity. A significant number of patients treated with anthracyclines develop cardiotoxicity (anthracycline-induced cardiotoxi…
- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:11418485` (clinpgx_citation) — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - [PMID 11418485] (Blood, 2001) Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism. This study investigated whether a polymorphism in the 5,10-methylenetetrahydrofolate reductase (M…
- `PMID:11710708` (clinpgx_citation) — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - [PMID 11710708] (Arthritis and rheumatism, 2001) The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients. To study the possible relationship between the C677T mu…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:15936011` (clinpgx_citation) — **A beneficial effect of simvastatin on DNA damage in 242T allele of the NADPH oxidase p22phox in hypercholesterolemic patients.** — *Clinica chimica acta; international journal of clinical chemistry · 2005*
  - [PMID 15936011] (Clinica chimica acta; international journal of clinical chemistry, 2005) A beneficial effect of simvastatin on DNA damage in 242T allele of the NADPH oxidase p22phox in hypercholesterolemic patients. The effect of simvastatin on DNA damage in hypercholesterolemic…
- `PMID:12411325` (clinpgx_citation) — **Polymorphism G80A in the reduced folate carrier gene and its relationship to methotrexate plasma levels and outcome of childhood acute lymphoblastic leukemia.** — *Blood · 2002*
  - [PMID 12411325] (Blood, 2002) Polymorphism G80A in the reduced folate carrier gene and its relationship to methotrexate plasma levels and outcome of childhood acute lymphoblastic leukemia. Methotrexate (MTX) is a key compound of chemotherapeutic regimens used in the treatment of …
- `PMID:12915598` (clinpgx_citation) — **Homocysteine, pharmacogenetics, and neurotoxicity in children with leukemia.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2003*
  - [PMID 12915598] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2003) Homocysteine, pharmacogenetics, and neurotoxicity in children with leukemia. Despite its clinical success, methotrexate (MTX) therapy is associated with toxicities…
- `PMID:15805193` (clinpgx_citation) — **Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin.** — *Proceedings of the National Academy of Sciences of the United States of America · 2005*
  - [PMID 15805193] (Proceedings of the National Academy of Sciences of the United States of America, 2005) Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin. Phenytoin and carbamazepine are effective …
- `PMID:16220110` (clinpgx_citation) — **CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population.** — *Pharmacogenetics and genomics · 2005*
  - [PMID 16220110] (Pharmacogenetics and genomics, 2005) CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population. The genetically polymorphic cytochrome P450 2C9 (CYP2C9) metabolizes many important drugs. Among them, phenytoin has …

</details>

<sub>KG: 14 entities / 62 relations · 23 references (14 PubMed) · 41 retrieval events</sub>

#### Phase 5 — + PMC full text

**Genes surfaced:** ERCC1 (rs11615), CYBA (rs4673)

Doxorubicin-induced mucositis is associated with genetic variants such as ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing susceptibility to this adverse effect. The biological mechanism likely involves these genes' roles in DNA repair and oxidative stress regulation, respectively, impacting cellular damage and recovery from doxorubicin exposure. For drug discovery and patient safety, pre-treatment genetic screening for these variants could help identify patients at higher risk of mucositis, allowing for dose adjustments or the use of alternative agents to mitigate this side effect.

<details><summary>ClinPGx evidence retrieved</summary>

- `ClinPGx:ERCC1/rs11615:L3` — ERCC1 (rs11615): PharmGKB evidence level 3 linking it to doxorubicin-related Mucositis, Osteosarcoma. ClinPGx relationship: associated.
- `ClinPGx:CYBA/rs4673:L3` — CYBA (rs4673): PharmGKB evidence level 3 linking it to doxorubicin-related Anemia, Mucositis. ClinPGx relationship: associated.
- `ClinPGx:SLC28A3/rs7853758:L2B` — SLC28A3 (rs7853758): PharmGKB evidence level 2B linking it to doxorubicin-related Cardiotoxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ABCB1/rs1045642:L3` — ABCB1 (rs1045642): PharmGKB evidence level 3 linking it to doxorubicin-related Multiple Myeloma. ClinPGx relationship: ambiguous.
- `ClinPGx:MTHFR/rs1801133:L2A` — MTHFR (rs1801133): PharmGKB evidence level 2A linking it to methotrexate-related Acute lymphoblastic leukemia, Drug Toxicity. ClinPGx relationship: ambiguous.
- `ClinPGx:ERCC1/rs735482:L3` — ERCC1 (rs735482): PharmGKB evidence level 3 linking it to thalidomide-related Multiple Myeloma. ClinPGx relationship: associated.
- `ClinPGx:ABCC3/rs4148416:L3` — ABCC3 (rs4148416): PharmGKB evidence level 3 linking it to cisplatin-related Osteosarcoma. ClinPGx relationship: ambiguous.
- `ClinPGx:SLC19A1/rs1051266:L2A` — SLC19A1 (rs1051266): PharmGKB evidence level 2A linking it to methotrexate-related Rheumatoid arthritis. ClinPGx relationship: ambiguous.
- `ClinPGx:GSTP1/rs1695:L3` — GSTP1 (rs1695): PharmGKB evidence level 3 linking it to cisplatin-related Ovarian Neoplasms. ClinPGx relationship: ambiguous.

</details>

<details><summary>PubMed citations checked (with full-text upgrades)</summary>

- `PMID:21887680` (clinpgx_citation) — **Germline genetic polymorphisms may influence chemotherapy response and disease outcome in osteosarcoma: a pilot study.** — *Cancer · 2012*
  - [PMID 21887680] (Cancer, 2012) Germline genetic polymorphisms may influence chemotherapy response and disease outcome in osteosarcoma: a pilot study. Osteosarcoma is the most common malignant bone tumor in children and young people. Efficacy of multiagent MAP (methotrexate, doxor…
- `PMID:29507678/PMC5823653` (clinpgx_citation+pmc_xml) — **Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients.** — *Oncotarget · 2018*
  - [PMID 29507678 | PMC5823653 full text via pmc_xml] Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients. :: Breast cancer is heterogeneous disease with distinct molecular subtypes that require many therapeutic app…
- `PMID:29507678` (clinpgx_citation) — **Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients.** — *Oncotarget · 2018*
  - [PMID 29507678] (Oncotarget, 2018) Pharmacogenetics of toxicity of 5-fluorouracil, doxorubicin and cyclophosphamide chemotherapy in breast cancer patients. The differences in patients' response to the same medication, toxicity included, are one of the major problems in breast can…
- `PMID:16330681` (clinpgx_citation) — **NAD(P)H oxidase and multidrug resistance protein genetic polymorphisms are associated with doxorubicin-induced cardiotoxicity.** — *Circulation · 2005*
  - [PMID 16330681] (Circulation, 2005) NAD(P)H oxidase and multidrug resistance protein genetic polymorphisms are associated with doxorubicin-induced cardiotoxicity. A significant number of patients treated with anthracyclines develop cardiotoxicity (anthracycline-induced cardiotoxi…
- `PMID:21900104` (clinpgx_citation) — **Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2012*
  - [PMID 21900104] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2012) Pharmacogenomic prediction of anthracycline-induced cardiotoxicity in children. Anthracycline-induced cardiotoxicity (ACT) is a serious adverse drug reaction limit…
- `PMID:23441093` (clinpgx_citation) — **Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children.** — *Pediatric blood & cancer · 2013*
  - [PMID 23441093] (Pediatric blood & cancer, 2013) Validation of variants in SLC28A3 and UGT1A6 as genetic markers predictive of anthracycline-induced cardiotoxicity in children. The use of anthracyclines as effective antineoplastic drugs is limited by the occurrence of cardiotoxic…
- `PMID:11418485` (clinpgx_citation) — **Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism.** — *Blood · 2001*
  - [PMID 11418485] (Blood, 2001) Pharmacogenetics of methotrexate: toxicity among marrow transplantation patients varies with the methylenetetrahydrofolate reductase C677T polymorphism. This study investigated whether a polymorphism in the 5,10-methylenetetrahydrofolate reductase (M…
- `PMID:11710708` (clinpgx_citation) — **The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients.** — *Arthritis and rheumatism · 2001*
  - [PMID 11710708] (Arthritis and rheumatism, 2001) The C677T mutation in the methylenetetrahydrofolate reductase gene: a genetic risk factor for methotrexate-related elevation of liver enzymes in rheumatoid arthritis patients. To study the possible relationship between the C677T mu…
- `PMID:18347182` (clinpgx_citation) — **Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients.** — *Clinical cancer research : an official journal of the American Association for Cancer Research · 2008*
  - [PMID 18347182] (Clinical cancer research : an official journal of the American Association for Cancer Research, 2008) Correlation of CDA, ERCC1, and XPD polymorphisms with response and survival in gemcitabine/cisplatin-treated advanced non-small cell lung cancer patients. Select…
- `PMID:19361884` (clinpgx_citation) — **Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients.** — *Lung cancer (Amsterdam, Netherlands) · 2010*
  - [PMID 19361884] (Lung cancer (Amsterdam, Netherlands), 2010) Effects of excision repair cross-complementation group 1 (ERCC1) single nucleotide polymorphisms on the prognosis of non-small cell lung cancer patients. Excision repair cross-complementation group 1 (ERCC1) is the lead…
- `PMID:15936011` (clinpgx_citation) — **A beneficial effect of simvastatin on DNA damage in 242T allele of the NADPH oxidase p22phox in hypercholesterolemic patients.** — *Clinica chimica acta; international journal of clinical chemistry · 2005*
  - [PMID 15936011] (Clinica chimica acta; international journal of clinical chemistry, 2005) A beneficial effect of simvastatin on DNA damage in 242T allele of the NADPH oxidase p22phox in hypercholesterolemic patients. The effect of simvastatin on DNA damage in hypercholesterolemic…
- `PMID:12411325` (clinpgx_citation) — **Polymorphism G80A in the reduced folate carrier gene and its relationship to methotrexate plasma levels and outcome of childhood acute lymphoblastic leukemia.** — *Blood · 2002*
  - [PMID 12411325] (Blood, 2002) Polymorphism G80A in the reduced folate carrier gene and its relationship to methotrexate plasma levels and outcome of childhood acute lymphoblastic leukemia. Methotrexate (MTX) is a key compound of chemotherapeutic regimens used in the treatment of …
- `PMID:12915598` (clinpgx_citation) — **Homocysteine, pharmacogenetics, and neurotoxicity in children with leukemia.** — *Journal of clinical oncology : official journal of the American Society of Clinical Oncology · 2003*
  - [PMID 12915598] (Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 2003) Homocysteine, pharmacogenetics, and neurotoxicity in children with leukemia. Despite its clinical success, methotrexate (MTX) therapy is associated with toxicities…
- `PMID:15805193` (clinpgx_citation) — **Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin.** — *Proceedings of the National Academy of Sciences of the United States of America · 2005*
  - [PMID 15805193] (Proceedings of the National Academy of Sciences of the United States of America, 2005) Genetic predictors of the maximum doses patients receive during clinical use of the anti-epileptic drugs carbamazepine and phenytoin. Phenytoin and carbamazepine are effective …
- `PMID:16220110` (clinpgx_citation) — **CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population.** — *Pharmacogenetics and genomics · 2005*
  - [PMID 16220110] (Pharmacogenetics and genomics, 2005) CYP2C9, CYP2C19, ABCB1 (MDR1) genetic polymorphisms and phenytoin metabolism in a Black Beninese population. The genetically polymorphic cytochrome P450 2C9 (CYP2C9) metabolizes many important drugs. Among them, phenytoin has …

</details>

<sub>KG: 14 entities / 62 relations · 24 references (15 PubMed) · 41 retrieval events</sub>

---

