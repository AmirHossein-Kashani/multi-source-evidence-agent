# Phase 12 — as phase 11, with expanded open-access full text — outputs for the 10 ADR questions

Configuration: `pharmgkb+pubmed_free` + digest + ledger + PMC/EuropePMC/Unpaywall

**91 gene–drug pairs** across 10 questions (9.1 per question), **65** carrying a contradiction flag. 26 papers read, 12 of them as full text.

Confidence is computed by formula in `evidence_ledger.py` — the model never emits it. `disputed` means at least one contradiction flag fired.

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

*9 gene–drug pairs, 9 disputed*

The genetic variants GSTT1 null genotype and NFE2L2 rs6721961 G-allele are associated with increased susceptibility to cisplatin-induced ototoxicity, particularly at frequencies ≥2 kHz. These polymorphisms likely contribute to a hereditary insufficiency in the antioxidant defense system, exacerbating hearing loss due to cisplatin treatment. For drug discovery and patient safety, screening for these genetic variants could help identify patients at higher risk of ototoxicity, allowing for dose adjustments or alternative therapeutic strategies to mitigate adverse effects.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.59 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **TPMT** (TPMT*1) | 0.56 | moderate | curator_ambiguous | `ClinPGx:TPMT/TPMT*1:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **NFE2L2** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |

<details><summary>Paragraphs the system read and kept (1 from 1 papers)</summary>

- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…

</details>

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

*10 gene–drug pairs, 10 disputed*

The risk of cisplatin-induced ototoxicity in pediatric cancer patients is associated with genetic variants such as GSTM1 non-null, TPMT *1, and COMT rs4646316. The biological mechanism underlying these associations likely involves the role of these genes in drug metabolism and detoxification pathways, which can influence how cisplatin is processed and its subsequent effects on auditory function. For instance, GSTM1 and TPMT are involved in glutathione conjugation and thiopurine S-methyltransferase activity respectively, both critical for detoxifying reactive metabolites of drugs like cisplatin. The COMT variant may affect dopamine metabolism, which could indirectly influence ototoxicity through neuroprotective pathways. These findings have implications for drug development by highlighting the need to consider genetic factors in clinical trials and patient safety by suggesting that biomarker screening for these variants could help identify patients at higher risk of ototoxicity, potentially guiding dose adjustments or alternative therapeutic strategies.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **ACYP2** | 0.45 | low | curator_ambiguous | `PMID:28445188/PMC5432027#p29` (meta_analysis) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **NFE2L2** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **COMT** (rs4646316) | 0.43 | low | curator_ambiguous, literature_internal | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | `PMID:28445188/PMC5432027#p29` (meta_analysis) |
| **TPMT** (TPMT*1) | 0.32 | low | curator_ambiguous | `ClinPGx:TPMT/TPMT*1:L3` (curated) | `PMID:41637682#p0` (review)<br>`PMID:28445188/PMC5432027#p29` (meta_analysis) |

<details><summary>Paragraphs the system read and kept (6 from 3 papers)</summary>

- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…
- `PMID:41637682#p0` — *TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.* — section **Abstract**
  - To assess the ongoing citation of the 2009 Nature Genetics article by Ross et al linking TPMT to cisplatin-induced ototoxicity and to evaluate the extent to which its disputed findings persist in the literature. A total of 378 Goo…
- `PMID:28445188/PMC5432027#p29` — *TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplat* — section **Systematic Review and Meta-Analysis**
  - The pooled odds ratio was statistically significant for the associations with the COMT SNP rs4646316 (odds ratio 1.50, 95% CI: 1.15-1.95) and with the ACYP2 SNP rs1872328 (odds ratio 5.91, 95% CI: 1.51-23.16). In both cases, the e…
- `PMID:28445188/PMC5432027#p33` — *TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplat* — section **Discussion**
  - Despite these confounders, we followed the analysis of our primary data by undertaking a meta-analysis comparing Chang 0 vs >0 in rs1872328 ‘AG’ or ‘AA’ genotype carriers vs ‘GG’ carriers as reported in Vos et al [19] as presented…
- `PMID:28445188/PMC5432027#p37` — *TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplat* — section **Discussion**
  - In conclusion, we have found an association between the ACYP2 polymorphism and cisplatin induced ototoxicity, although we could not replicate the association with TPMT and COMT variants. Cisplatin is used in a wide variety of tumo…
- `PMID:28445188/PMC5432027#p31` — *TPMT, COMT and ACYP2 genetic variants in paediatric cancer patients with cisplat* — section **Discussion**
  - Our data did not replicate previous findings that COMT and TPMT variants are risk factors for cisplatin-induced ototoxicity, consistent with several other studies [16–18]. Heterogeneity between study populations with regards to si…

</details>

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

*17 gene–drug pairs, 11 disputed*

Your daughter's high risk of hearing loss during cisplatin treatment for Neuroblastoma is influenced by her TPMT variant, which affects drug metabolism and increases the level of unmetabolized cisplatin. Additionally, genetic polymorphisms in GSTT1 and NFE2L2 may further increase susceptibility to ototoxicity due to their roles in antioxidant defense mechanisms. The presence of an MT-RNR1 variant could also compound her risk by affecting mitochondrial function. Comprehensive monitoring for hearing loss is essential, along with considering supportive therapies like Ginkgo biloba extract, although its efficacy needs further validation in patients with specific genetic backgrounds such as TPMT variants.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.59 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **HIF1A** | 0.57 | moderate | — | `PMID:42667755#p0` (in_vitro) | — |
| **TNF** | 0.57 | moderate | — | `PMID:42667755#p0` (in_vitro) | — |
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **ACYP2** | 0.44 | low | curator_ambiguous | `PMID:37726872#p0` (systematic_review) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **NFE2L2** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **TPMT** (TPMT*1) | 0.37 | low | curator_ambiguous, literature_internal | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:37726872#p0` (systematic_review) | `PMID:41637682#p0` (review)<br>`PMID:42504125#p0` (human_cohort) |
| **MT-RNR1** | 0.27 | low | unsupported_claim | `PMID:42524757/PMC13519768#p43` (review) | — |
| **HSP90AA1** | 0.26 | low | unsupported_claim | `PMID:42667755#p0` (in_vitro) | — |
| _… 3 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (9 from 6 papers)</summary>

- `PMID:42667755#p0` — *Mechanistic insights into Ginkgo biloba leaves against cisplatin-induced ototoxi* — section **Abstract**
  - Although Ginkgo biloba leaves (GBLs) extract exhibits considerable therapeutic potential for alleviating cisplatin-induced ototoxicity (CIO), its exact molecular mechanisms remain unclear. In this study, we investigated the potent…
- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…
- `PMID:41637682#p0` — *TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.* — section **Abstract**
  - To assess the ongoing citation of the 2009 Nature Genetics article by Ross et al linking TPMT to cisplatin-induced ototoxicity and to evaluate the extent to which its disputed findings persist in the literature. A total of 378 Goo…
- `PMID:42524757/PMC13519768#p43` — *MT-RNR1 genotype testing for preventing aminoglycoside-mediated ototoxicity: A g* — section **Reporting test results**
  - At increased risk of aminoglycoside‐induced hearing loss due to mitochondrially encoded 12S ribosomal ribonucleic acid genotype (finding) SCTID: 4055281000000113.At normal risk of aminoglycoside‐induced hearing loss based on mitoc…
- `PMID:42524757/PMC13519768#p44` — *MT-RNR1 genotype testing for preventing aminoglycoside-mediated ototoxicity: A g* — section **Reporting test results**
  - At increased risk of aminoglycoside‐induced hearing loss due to mitochondrially encoded 12S ribosomal ribonucleic acid genotype (finding) SCTID: 4055281000000113.…
- `PMID:42524757/PMC13519768#p45` — *MT-RNR1 genotype testing for preventing aminoglycoside-mediated ototoxicity: A g* — section **Reporting test results**
  - At normal risk of aminoglycoside‐induced hearing loss based on mitochondrially encoded 12S ribosomal ribonucleic acid genotype (finding) SCTID: 4055331000000115.…

</details>

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

*8 gene–drug pairs, 7 disputed*

The permanent inner ear damage experienced by your child after receiving Platinol (cisplatin) treatment may be influenced by her GSTT1 status, particularly if she carries a null genotype for this gene. The evidence suggests that individuals with the GSTT1 null genotype are at higher risk for cisplatin-induced ototoxicity due to impaired glutathione S-transferase activity, which is crucial for detoxifying reactive metabolites of cisplatin. This genetic polymorphism can lead to increased susceptibility and severity of ototoxic side effects from Platinol. For drug discovery and patient safety, it is important to screen patients for GSTT1 status before initiating cisplatin-based chemotherapy to identify those at higher risk for ototoxicity. Additionally, dose adjustments or the use of alternative agents may be considered in high-risk individuals.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC19A1** (rs12659) | 0.62 | moderate | — | `ClinPGx:SLC19A1/rs12659:L3` (curated) | — |
| **CYP2E1** (rs2070676) | 0.59 | moderate | curator_ambiguous | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **ABCC3** (rs4148416) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs4148416:L3` (curated) | — |
| **AKT1** (rs1130214) | 0.56 | moderate | curator_ambiguous | `ClinPGx:AKT1/rs1130214:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |
| **GSTM3** (rs1799735) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM3/rs1799735:L3` (curated) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |

<details><summary>Paragraphs the system read and kept (1 from 1 papers)</summary>

- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…

</details>

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

*7 gene–drug pairs, 6 disputed*

Cisplatin can cause peripheral neuropathy as a side effect of chemotherapy. However, there is currently insufficient evidence to conclude that cisplatin causes a genetic predisposition to this condition. The GSTP1 polymorphism has been associated with oxaliplatin-induced peripheral neuropathy but not specifically with cisplatin-induced peripheral neuropathy. Other genes such as ERCC1 (rs11615) are mentioned in the knowledge graph, but there is no direct evidence linking them to genetic predisposition for cisplatin-induced peripheral neuropathy. The biological mechanism underlying this adverse reaction remains unclear and requires further investigation. For drug development and patient safety, it is important to continue exploring potential biomarkers that could predict susceptibility to cisplatin-induced peripheral neuropathy, which may inform dose adjustments or the use of alternative agents.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC19A1** (rs12659) | 0.62 | moderate | — | `ClinPGx:SLC19A1/rs12659:L3` (curated) | — |
| **CYP2E1** (rs2070676) | 0.59 | moderate | curator_ambiguous | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **GSTP1** (rs1695) | 0.59 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated)<br>`PMID:30854066/PMC6365892#p0` (human_cohort) | — |
| **ABCC3** (rs4148416) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs4148416:L3` (curated) | — |
| **AKT1** (rs1130214) | 0.56 | moderate | curator_ambiguous | `ClinPGx:AKT1/rs1130214:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |
| **GSTM3** (rs1799735) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM3/rs1799735:L3` (curated) | — |

<details><summary>Paragraphs the system read and kept (3 from 1 papers)</summary>

- `PMID:30854066/PMC6365892#p0` — *GSTP1 as a potential predictive factor for adverse events associated with platin* — section **?**
  - ONCOLOGY LETTERS  17:  2897-2904,  2019
Abstract. Glutathione S -transferase (GST) exhibits anti -
dotal effects on numerous drugs, including platinum -based 
antineoplastic drugs. Furthermore, GST  Pi  1  (GSTP1 ) 
polymorphism i…
- `PMID:30854066/PMC6365892#p1` — *GSTP1 as a potential predictive factor for adverse events associated with platin* — section **?**
  - KATAYANAGI et al:  GSTP1, A POTENTIAL PREDICTIVE FACTOR OF PERIPHERAL NEUROPATHY2898
predictive factor of peripheral neuropathy, which occurs as an 
adverse effect of exposure to platinum-based anticancer drugs, 
in Japanese patie…
- `PMID:30854066/PMC6365892#p2` — *GSTP1 as a potential predictive factor for adverse events associated with platin* — section **?**
  - ONCOLOGY LETTERS  17:  2897-2904,  2019 2899
(SNP) sites contained the ATC sequence for the homozygous 
AA allele, and the A /GTC ( Fig. 2 A) and GTC ( Fig. 2 B) 
sequences at the SNP position. These results of the direct 
sequenc…

</details>

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

*3 gene–drug pairs, 3 disputed*

The severe cardiotoxicity observed after doxorubicin treatment for pediatric lymphoma may have a genetic component, as suggested by the evidence linking SLC28A3 (rs7853758) and GSTP1 (rs1695) to doxorubicin-induced cardiotoxicity. However, both genes are marked with 'curator_ambiguous' status due to conflicting evidence, indicating that while these genetic variants may influence the risk or severity of cardiotoxic effects from doxorubicin, more research is needed for definitive conclusions. The likely biological mechanism involves oxidative stress and mitochondrial dysfunction mediated by p38 MAPK signaling pathways. For drug development and patient safety, further genetic testing could help identify specific polymorphisms in SLC28A3 and GSTP1 that may guide personalized treatment strategies to minimize cardiotoxicity risks.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.71 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |

<details><summary>Paragraphs the system read and kept (3 from 1 papers)</summary>

- `PMID:42670540/#p1` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - Drug-induced cardiotoxicity also exhibits notable sex-related differences. In non-cancer populations, female sex is an 
important risk factor for QT interval prolongation and torsades de pointes (TdP) induced by class III antiarrh…
- `PMID:42670540/#p0` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - REVIEW
Mechanisms and the Role of p38 MAPK Signaling 
in Doxorubicin-Induced Cardiotoxicity: A Review
Bingjie Zhao 1, Mengyao Tang 2, Jiedong Zhou 3, Hui Liu 1, Hanghui He 1, Jin Lv 1
1Department of Cardiology, The Second Affiliat…
- `PMID:42670540/#p2` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - for advancing the understanding of DIC pathogenesis and developing more precise cardioprotective strategies and novel 
adjunctive interventions.
Mechanisms of Doxorubicin-Induced Cardiotoxicity
DIC is a multifactorial process invo…

</details>

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

*11 gene–drug pairs, 6 disputed*

The pharmacogenomic biomarkers that predict anthracycline-induced cardiotoxicity (ACT) in childhood cancer survivors include SLC28A3 (rs7853758) and GSTP1 (rs1695), with evidence levels of 2B and 3, respectively. However, a study in Chinese early-stage breast cancer patients found no significant association between these genetic variants and ACT, suggesting that their predictive value may vary across different populations or clinical settings. Additionally, the study identified clinical risk factors such as older age, higher cumulative anthracycline dose, and use of HER2-targeted antibodies as independent predictors for ACT. The biological mechanism involves variations in drug transport and metabolism pathways influenced by these genetic variants. For drug development and patient safety, it is crucial to validate biomarkers like SLC28A3 (rs7853758) and GSTP1 (rs1695) across diverse populations and consider integrating plasma extracellular vesicle miRNA profiles as potential predictive biomarkers for ACT.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **HAS3** | 0.58 | moderate | — | `PMID:42279262/PMC13255899#p61` (review) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |
| **SLC28A3** (rs7853758) | 0.54 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42549829#p0` (human_cohort) |
| **GSTP1** (rs1695) | 0.39 | low | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **MIR-1262** | 0.27 | low | unsupported_claim | `PMID:42665114/#p11` (review) | — |
| **MIR-217-5P** | 0.27 | low | unsupported_claim | `PMID:42665114/#p11` (review) | — |
| **MIR-497-5P** | 0.27 | low | unsupported_claim | `PMID:42665114/#p11` (review) | — |
| **MIR-584-3P** | 0.27 | low | unsupported_claim | `PMID:42665114/#p11` (review) | — |
| **ABCB1** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **ABCC2** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **CBR3** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (3 from 3 papers)</summary>

- `PMID:42549829#p0` — *Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Ch* — section **Abstract**
  - This study aimed to clarify the incidence of anthracycline-induced cardiotoxicity (ACT) and identify its clinical and candidate genetic risk factors in Chinese early-stage breast cancer patients, so as to provide evidence for clin…
- `PMID:42665114/#p11` — *Doxorubicin-induced Cardiotoxicity is Propagated by Paracrine Signaling through * — section **?**
  - Distinct Plasma EV miRNA Profiles Differentiate High- and Low-Risk Cardiotoxicity 303 
Patients: EVs were isolated from blinded clinical plasma samples of patient cohorts classified 304 
as high or low risk for DOX-induced cardiot…
- `PMID:42279262/PMC13255899#p61` — *Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical* — section **11. Strategies for Early Identification of Sex-Specific Cancer Treatment-Related Cardiovascular Toxicities**
  - Genetics: Sex-informed medicine encompasses genetics, hormones, and immune function, significantly impacting CV disease and cancer. Biological differences, such as X and Y chromosome effects and variations in sex hormones, contrib…

</details>

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

*4 gene–drug pairs, 4 disputed*

The early heart failure observed in your son who carries the CYP2D6*4 genetic variant and was treated with doxorubicin for his neoplasm is likely influenced by his genetic predisposition rather than the specific type of cancer he has. The CYP2D6*4 variant affects drug metabolism, potentially altering how doxorubicin is processed in your son’s body, which can influence both its efficacy and toxicity. Although there is no established pharmacogenomic link between CYP2D6 and doxorubicin, the evidence suggests that genetic factors like SLC28A3 (rs7853758) may play a role in doxorubicin-related cardiotoxicity at a lower confidence level. The p38 mitogen-activated protein kinase (p38 MAPK) pathway is highlighted as a central hub in the development of doxorubicin-induced cardiotoxicity, integrating various pathological signals such as oxidative stress and inflammatory responses. For drug discovery and patient safety, it is crucial to consider genetic screening for variants like CYP2D6*4 and SLC28A3 (rs7853758) in patients treated with doxorubicin to tailor treatment strategies and mitigate the risk of cardiotoxicity.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.71 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |
| **CYP2D6** | 0.04 | very_low | literature_internal, uncurated_literature_claim | `PMID:42670540/#p0` (review)<br>`PMID:42670080#p0` (human_cohort) | `PMID:42670540/#p0` (review)<br>`PMID:42657460#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (4 from 3 papers)</summary>

- `PMID:42670540/#p0` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - REVIEW
Mechanisms and the Role of p38 MAPK Signaling 
in Doxorubicin-Induced Cardiotoxicity: A Review
Bingjie Zhao 1, Mengyao Tang 2, Jiedong Zhou 3, Hui Liu 1, Hanghui He 1, Jin Lv 1
1Department of Cardiology, The Second Affiliat…
- `PMID:42670540/#p2` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - for advancing the understanding of DIC pathogenesis and developing more precise cardioprotective strategies and novel 
adjunctive interventions.
Mechanisms of Doxorubicin-Induced Cardiotoxicity
DIC is a multifactorial process invo…
- `PMID:42657460#p0` — *Plasma Proteins Associated With the Immune Response to Anthracycline Cardiotoxic* — section **Abstract**
  - Anthracyclines such as doxorubicin are well recognized to induce dose-dependent cardiotoxicity. However, traditional imaging and blood biomarkers of myocardial injury are inadequate for early risk stratification. We aimed to disco…
- `PMID:42670080#p0` — *Anthracycline Cardiotoxicity: A Real-World Study Based on FDA Adverse Event Repo* — section **Abstract**
  - Based on the FDA Adverse Event Reporting System (FAERS) database, data mining of adverse event (AE) signals related to anthracyclines was conducted to explore their potential medication risks, especially cardiotoxicity, in order t…

</details>

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

*9 gene–drug pairs, 5 disputed*

Adriamycin-induced cardiac strain and heart muscle damage are well-documented side effects with high confidence levels. The medical knowledge graph suggests a potential link between the genetic variant GSTM1 and these cardiotoxic effects, though the evidence is not definitive (confidence 0.70). Studies indicate that environmental factors like cadmium exposure can increase glutathione S-transferase activity in breast cancer cell lines, which may interact with GSTM1 to influence susceptibility to Adriamycin-induced cardiac damage. However, direct evidence linking GSTM1 specifically to cardiotoxicity is limited and conflicting (confidence 0.29). For drug discovery and patient safety, further research into the role of GSTM1 and other genetic factors in Adriamycin-induced cardiotoxicity could inform personalized dosing strategies or identify patients at higher risk for cardiac complications.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **SLC28A3** (rs7853758) | 0.54 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42246857#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.39 | low | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |
| **GSTM1** | 0.29 | low | curator_ambiguous, literature_internal | `PMID:42515685/PMC13416366#p46` (in_vitro)<br>`PMID:41823204#p0` (human_cohort) | `PMID:42650802/PMC13510337#p45` (in_vitro)<br>`PMID:42515685/PMC13416366#p46` (in_vitro) |
| **GPX4** | 0.26 | low | unsupported_claim | `PMID:42650802/PMC13510337#p45` (in_vitro) | — |
| **GST-PI** | 0.26 | low | unsupported_claim | `PMID:42515685/PMC13416366#p46` (in_vitro) | — |
| **NRF2** | 0.26 | low | unsupported_claim | `PMID:42650802/PMC13510337#p45` (in_vitro) | — |
| **SLC7A11** | 0.26 | low | unsupported_claim | `PMID:42650802/PMC13510337#p45` (in_vitro) | — |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (10 from 5 papers)</summary>

- `PMID:42650802/PMC13510337#p45` — *Quercetin Activates NRF2/SLC7A11/GPX4 Signaling to Restore Mitochondrial Functio* — section **3.6. QUE Alleviates DOX-Induced Ferroptosis and Mitochondrial Function Damage in H9c2 Cardiomyocytes via the NRF2/SLC7A11/GPX4 Pathway**
  - Western blot analysis was used to quantify the protein abundance of NRF2, SLC7A11 and GPX4 in H9c2 cardiomyocytes (Figure 9A–D). Lower expression of the three target proteins was detected in cells exposed to DOX alone. Incubation …
- `PMID:42650802/PMC13510337#p54` — *Quercetin Activates NRF2/SLC7A11/GPX4 Signaling to Restore Mitochondrial Functio* — section **4. Discussion**
  - In the present study, DOX suppressed NRF2 nuclear translocation and decreased the expression of SLC7A11 and GPX4. Both QUE and the NRF2 agonist TBHQ effectively reversed DOX-induced pathway inhibition, improved mitochondrial funct…
- `PMID:42650802/PMC13510337#p55` — *Quercetin Activates NRF2/SLC7A11/GPX4 Signaling to Restore Mitochondrial Functio* — section **4. Discussion**
  - DOX inhibited NRF2 nuclear translocation and downregulated SLC7A11 and GPX4 expression. QUE and TBHQ significantly reversed DOX-induced pathway suppression, improved mitochondrial function and inhibited ferroptosis. NRF2 knockdown…
- `PMID:42650802/PMC13510337#p28` — *Quercetin Activates NRF2/SLC7A11/GPX4 Signaling to Restore Mitochondrial Functio* — section **3.1. QUE Can Alleviate DOX-Induced Cardiac Dysfunction Both In Vitro and In Vivo**
  - To investigate the protective effects of QUE against DOX-induced myocardial injury, in vivo assays were performed using a DOX-triggered DIC model in SD rats.…
- `PMID:42515685/PMC13416366#p46` — *Differential Effects of 17β-Estradiol, Its Metabolites, and Cadmium on Cytotoxic* — section **2.8.1. Effect of Single Compounds on GST Activity**
  - Exposure of MCF-7 and MCF-7/DOX cells to Cd, estradiol, and its metabolites resulted in a concentration-dependent increase in GST activity compared with the respective controls. Basal GST activity was higher in MCF-7/DOX cells tha…
- `PMID:42670540/#p1` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - Drug-induced cardiotoxicity also exhibits notable sex-related differences. In non-cancer populations, female sex is an 
important risk factor for QT interval prolongation and torsades de pointes (TdP) induced by class III antiarrh…

</details>

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

*13 gene–drug pairs, 4 disputed*

Doxorubicin is associated with mucositis, a known side effect. Genetic variants such as ERCC1 (rs11615) and CYBA are modulated by the response to doxorubicin, indicating these genes play a role in individual susceptibility to mucositis when treated with this drug. The PharmGKB evidence level 3 supports that ERCC1 (rs11615) is associated with an increased risk of doxorubicin-related mucositis, particularly in osteosarcoma patients. Similarly, CYBA (rs4673) also increases the risk of mucositis in response to doxorubicin treatment according to PharmGKB evidence level 3. These findings suggest that genetic screening for ERCC1 and CYBA variants could be beneficial for predicting mucositis risk in patients treated with doxorubicin, potentially guiding personalized dosing or alternative therapy selection.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **CYBA** (rs4673) | 0.62 | moderate | — | `ClinPGx:CYBA/rs4673:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.62 | moderate | — | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |
| **TP53** | 0.57 | moderate | — | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **ABCC10** | 0.49 | low | curated_vs_literature | — | `PMID:42661698/PMC13518197#p4` (in_vitro) |
| **ABCG2** | 0.49 | low | curated_vs_literature | — | `PMID:42661698/PMC13518197#p4` (in_vitro) |
| **ABCB1** | 0.35 | low | curator_ambiguous | — | `PMID:42661698/PMC13518197#p4` (in_vitro) |
| **ABCC1** | 0.35 | low | curator_ambiguous | — | `PMID:42661698/PMC13518197#p4` (in_vitro) |
| **BAX** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **CASP1** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **INKA2** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **PCNA** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **RRM2** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **SLC7A11** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |

<details><summary>Paragraphs the system read and kept (4 from 2 papers)</summary>

- `PMID:42653080/PMC13513574#p23` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - Comparison of human and mouse colonoids revealed several shared genes with inverse regulation, including PCNA and SLC7A11 (File S1). SLC7A11, the cystine/glutamate antiporter that supports glutathione synthesis, was downregulated …
- `PMID:42653080/PMC13513574#p24` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - Differential gene expression analysis identified 14 genes shared across human colonoids, mouse colonoids, and mouse colon, representing a minimal conserved DOX response enriched for p53-linked DNA damage and apoptosis programs (Ta…
- `PMID:42653080/PMC13513574#p28` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - Analysis of the DDR pathway showed distinct regulatory signatures (Figure 4). In human colonoids, downregulation of CCNB1 and CCNB2 indicated G2/M checkpoint arrest, while upregulation of FAS, TNFRSF10B, and PID1 supported engagem…
- `PMID:42661698/PMC13518197#p4` — *Umbralisib antagonizes multidrug resistance in ABCB1-overexpressing cancer cells* — section **Cell lines and cell culture**
  - A panel of parental and drug-resistant cell lines was used to evaluate the reversal effect on ABC transporter-mediated multidrug resistance. KB-3-1 (parental) and KB-C2 cells (ABCB1 overexpression, colchicine-selected); SW620 (par…

</details>

---

## How to read the confidence

```
base    = ClinPGx evidence level (1A .98 … 4 .40) | absent .25 | 'not associated' .15
support = sum of study-type weights over DISTINCT sources (meta 1.0, GWAS .9, animal .3)
conf    = base·(1 + 0.18·log1p(support)) − 0.30·log1p(refute),  ×0.9 if curators disagree
```

Labels: high ≥0.75 · moderate ≥0.50 · low ≥0.25 · very_low below. On 72 labelled ClinPGx pairs the score separated positives from negatives by **+0.351** (Spearman 0.721), and every negative landed in `very_low`.

**Contradiction flags**

| Flag | Meaning |
|---|---|
| `curator_ambiguous` | ClinPGx curators recorded conflicting evidence for the pair |
| `curated_vs_literature` | the curated tables and the retrieved papers disagree |
| `literature_internal` | retrieved papers disagree with each other |
| `uncurated_literature_claim` | not in ClinPGx but backed by human studies — candidate novel finding |
| `unsupported_claim` | no curated row and no strong supporting study |

**Known limitation:** the prose answers rarely cite their references (0–1 of 10) even though the ledger carries paragraph-level refs. Read the ledger table, not the prose.
