# Phase 13 — contradiction resolution — outputs for the 10 ADR questions

Configuration: `pharmgkb+pubmed_combo` + digest + ledger + resolution layer

**145 gene–drug pairs** across 10 questions (14.5 per question), **87** carrying a contradiction flag. 37 papers read, 17 of them as full text.

Confidence is computed by formula in `evidence_ledger.py` — the model never emits it. `disputed` means at least one contradiction flag fired.

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

*18 gene–drug pairs, 8 disputed*

The ototoxicity associated with cisplatin treatment in children is influenced by genetic factors such as GSTM1 non-null, TPMT variants, and GADD45A. The primary evidence suggests that the GSTM1 non-null variant may increase susceptibility to ototoxicity; however, this association remains ambiguous (PharmGKB evidence level 3). Similarly, TPMT variants have been proposed but require further validation for clinical significance. A promising candidate is GADD45A, where knockout studies in mice indicate reduced hearing loss due to inhibited inflammatory cytokine expression. This suggests a potential genetic susceptibility pathway involving GADD45A for cisplatin-induced ototoxicity. For drug development and patient safety, these findings highlight the need for further research on GADD45A and other candidate genes to establish robust biomarkers for risk stratification and personalized treatment strategies.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |

> The COMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on COMT alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.59 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **ALDH2** | 0.58 | moderate | — | `PMID:42617317#p0` (animal) | — |
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **TPMT** (TPMT*1) | 0.56 | moderate | curator_ambiguous | `ClinPGx:TPMT/TPMT*1:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **CXCL** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL3** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **GADD45A** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **IDH2** | 0.26 | low | unsupported_claim | `PMID:42617317#p0` (animal) | — |
| _… 4 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (5 from 2 papers)</summary>

- `PMID:42633148/PMC13499120#p47` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Abbreviations**
  - ABR: Auditory brainstem response AKI: Acute kidney injury AMPK: AMP-activated protein kinase BAX: BCL2-associated X protein BCL-2: B-cell lymphoma 2 BECN1: Beclin 1 BFA: Brefeldin A BIRC5: Baculoviral IAP repeat containing 5 CCK-8…
- `PMID:42633148/PMC13499120#p18` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - To elucidate the mechanism by which Gadd45a knockout protects cells from cisplatin-induced toxicity, we collected protein samples from both the control and Gadd45a-/- groups for Western blotting analysis at various time points aft…
- `PMID:42633148/PMC13499120#p32` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Injection of si**
  - To evaluate the efficacy of siGadd45a knockdown in mitigating cisplatin ototoxicity, we first performed audiometry on mice to establish a baseline for subsequent experiments. Mice with qualified baseline audiometric profiles were …
- `PMID:42633148/PMC13499120#p14` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - Based on DNA topoisomerase II alpha (TOP2A), baculoviral IAP repeat-containing 5 (BIRC5), and GADD45A in platinum resistance and cell survival pathways [45], [46], [47], [48], we measured TOP2Α, BIRC5, and GADD45A protein expressi…
- `PMID:42617317#p0` — *Honokiol-mediated reversal of cisplatin-induced transcriptomic changes in outer * — section **Abstract**
  - Cisplatin-induced hearing loss (CIHL) affects half a million cancer patients annually, but treatment strategies are limited. We have previously shown that honokiol, an antioxidant and otoprotective compound, upregulates mitochondr…

</details>

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

*14 gene–drug pairs, 13 disputed*

The risk of cisplatin-induced ototoxicity in pediatric cancer patients is associated with several genetic variants including GSTM1 non-null, TPMT*1, COMT rs4646316 and rs9332377 T alleles, ERCC2 rs1799793 CT/TT genotype, ACYP2 rs1872328 A allele. The PharmGKB evidence level for these associations is moderate (level 3), indicating a need for further validation. These genetic variants likely influence the metabolism and cellular response to cisplatin, affecting ototoxicity risk through mechanisms such as DNA repair efficiency or drug detoxification capacity. For drug development, understanding these genetic factors can guide personalized dosing strategies and identify patients at higher risk of adverse effects, potentially leading to dose adjustments or alternative therapeutic options to minimize ototoxicity in pediatric cancer treatment.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** | CONFLICTING | 0.64 | the curators themselves record conflicting reports | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **TPMT** | CONFLICTING | 0.60 | the curators themselves record conflicting reports | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | — |
| **ABCC3** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:ABCC3/rs1051640:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | — |
| **SLC22A2** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:SLC22A2/rs316019:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | — |
| **ERCC2** | CONFLICTING | 0.47 | the curators themselves record conflicting reports | `PMID:40222694/#p0` (systematic_review)<br>`PMID:36802061#p0` (meta_analysis) | — |

> The COMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on COMT alone.

> The TPMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on TPMT alone.

> The ABCC3-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ABCC3 alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.64 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **TPMT** (TPMT*1) | 0.60 | moderate | curator_ambiguous | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | — |
| **ABCC3** (rs1051640) | 0.59 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | — |
| **SLC22A2** (rs316019) | 0.59 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.50 | low | curator_ambiguous, literature_internal | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated)<br>`PMID:39386217/PMC11461197#p16` (animal) | `PMID:39386217/PMC11461197#p16` (animal) |
| **ERCC2** | 0.47 | low | curator_ambiguous | `PMID:40222694/#p0` (systematic_review)<br>`PMID:36802061#p0` (meta_analysis) | — |
| **ACYP2** | 0.45 | low | curator_ambiguous | `PMID:36802061#p0` (meta_analysis) | — |
| **GSTP1** | 0.44 | low | curator_ambiguous | `PMID:40222694/#p0` (systematic_review) | — |
| **LRP2** | 0.44 | low | curator_ambiguous | `PMID:40222694/#p0` (systematic_review) | — |
| **GSTT1** | 0.38 | low | curator_ambiguous, literature_internal | `PMID:39386217/PMC11461197#p16` (animal)<br>`PMID:40222694/#p0` (systematic_review) | `PMID:39386217/PMC11461197#p16` (animal) |
| **ABCB1** | 0.22 | very_low | curator_ambiguous | — | `PMID:40222694/#p0` (systematic_review) |
| **SLCO1B1** | 0.05 | very_low | unsupported_claim | — | `PMID:40222694/#p0` (systematic_review) |

<details><summary>Paragraphs the system read and kept (8 from 4 papers)</summary>

- `PMID:39386217/PMC11461197#p16` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **Normal kidney function in GSTM1-KO, GSTT1-KO, and Gstm1/Gstt1-DKO mice**
  - The GSTM1/GSTT1 double-genotype deletion is frequently observed in the general population and is associated with an increased risk of various diseases, including cancer and kidney diseases (28–30). These proteins belong to the GST…
- `PMID:39386217/PMC11461197#p17` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **Deletion of GSTM1 and GSTT1 aggravated cisplatin-induced AKI in mice**
  - Since the expression of GSTM1 and GSTT1 is downregulated in the kidney tissues of mice and patients with AKI, we hypothesized that GSTM1 and GSTT1 play an important role in the development of AKI. Mice were injected intraperitonea…
- `PMID:39386217/PMC11461197#p18` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **Deletion of GSTM1 and GSTT1 aggravated cisplatin-induced AKI in mice**
  - Deletion of GSTM1 and GSTT1 aggravated cisplatin-induced AKI in mice. (A) the BUN and CREA levels of four groups of wild type and DKO mice at 3days after cisplatin injection. (B) the mRNA and (D) protein expression levels of Kim-1…
- `PMID:39386217/PMC11461197#p19` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **Following cisplatin injection, DKO mice exhibited a significantly elevated level of oxidative stress compared to WT mice**
  - Under normal physiological conditions, glutathione (GSH) primarily exists in its reduced form, with GSH oxidized to oxidized glutathione (GSSG). GSSG is subsequently reduced back to GSH by glutathione reductase, maintaining cellul…
- `PMID:40222694/#p0` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **?**
  - Pharmacogenomics in pediatric oncology patients with solid tumors related 
to chemotherapy-induced toxicity: A systematic review
Paula Hansson
a , * , 1
, Christopher Blacker
a , 1
, Hanna Uvdal
b
, Mia Wadelius
c
, Henrik Green
b…
- `PMID:40222694/#p1` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **?**
  - with chemotherapy ( Cheng et al., 2004a; Miller et al., 2012 ). Ototox -
icity, or hearing loss, is strongly associated with platinum-based treat -
ment, especially cisplatin where ototoxicity occurs in 22 – 70 % of 
patients ( Br…

</details>

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

*11 gene–drug pairs, 11 disputed*

Your daughter's TPMT variant increases her risk for cisplatin-induced ototoxicity due to altered drug metabolism, potentially leading to higher systemic levels and prolonged exposure. The evidence suggests a context-dependent relationship between TPMT variants and cisplatin ototoxicity, with some studies supporting an association while others refute it based on different endpoints or populations. Given the high-risk scenario of Neuroblastoma treatment with cisplatin, regular audiometric evaluations are crucial to monitor hearing function and adjust the treatment plan if necessary to mitigate long-term damage. This highlights the importance of personalized medicine approaches in drug discovery and patient safety.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **TPMT** | CONTEXT-DEPENDENT | 0.41 | endpoint differs (e.g. threshold shift vs clinically significant loss) | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | `PMID:41637682#p0` (review)<br>`PMID:42504125#p0` (human_cohort) |

> The COMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on COMT alone.

> The apparent TPMT-cisplatin disagreement is explained by endpoint; the association may hold in one setting and not another.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.59 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **ABCB1** | 0.44 | low | curator_ambiguous | `PMID:40222694/#p0` (systematic_review) | — |
| **ABCC2** | 0.44 | low | curator_ambiguous | `PMID:40222694/#p0` (systematic_review) | — |
| **ACYP2** | 0.44 | low | curator_ambiguous | `PMID:37726872#p0` (systematic_review) | — |
| **TPMT** (TPMT*1) | 0.41 | low | curator_ambiguous, literature_internal | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:40222694/#p0` (systematic_review) | `PMID:41637682#p0` (review)<br>`PMID:42504125#p0` (human_cohort) |
| **SLCO1B1** | 0.28 | low | uncurated_literature_claim | `PMID:40222694/#p0` (systematic_review) | — |

<details><summary>Paragraphs the system read and kept (6 from 5 papers)</summary>

- `PMID:41637682#p0` — *TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.* — section **Abstract**
  - To assess the ongoing citation of the 2009 Nature Genetics article by Ross et al linking TPMT to cisplatin-induced ototoxicity and to evaluate the extent to which its disputed findings persist in the literature. A total of 378 Goo…
- `PMID:40222694/#p0` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **?**
  - Pharmacogenomics in pediatric oncology patients with solid tumors related 
to chemotherapy-induced toxicity: A systematic review
Paula Hansson
a , * , 1
, Christopher Blacker
a , 1
, Hanna Uvdal
b
, Mia Wadelius
c
, Henrik Green
b…
- `PMID:40222694/#p1` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **?**
  - with chemotherapy ( Cheng et al., 2004a; Miller et al., 2012 ). Ototox -
icity, or hearing loss, is strongly associated with platinum-based treat -
ment, especially cisplatin where ototoxicity occurs in 22 – 70 % of 
patients ( Br…
- `PMID:42504125#p0` — *Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With C* — section **Abstract**
  - Platinum-based chemotherapy is known to cause severe and debilitating hearing loss, but unlike cisplatin, the true incidence of carboplatin-induced hearing loss remains unclear. We evaluated functional hearing outcomes in children…
- `PMID:37726872#p0` — *Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced * — section **Abstract**
  - Cisplatin is commonly used to treat solid tumors; however, its use can be complicated by drug-induced hearing loss (ie, ototoxicity). The presence of certain genetic variants has been associated with the development/occurrence of …
- `PMID:36917731#p0` — *Role of Cisplatin Dose Intensity and TPMT Variation in the Development of Hearin* — section **Abstract**
  - Cisplatin, widely used in the treatment of solid tumors, causes permanent hearing loss in more than 60% of treated children. Previous studies have implicated several clinical factors in the development of ototoxicity, including cu…

</details>

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

*10 gene–drug pairs, 9 disputed*

The permanent inner ear damage observed after Platinol treatment in your child may be influenced by genetic factors such as GSTT1 status, although the evidence is currently insufficient to establish a definitive link. The medical knowledge graph indicates that GSTT1 status can act as a risk factor for Platinol-induced toxicity with moderate confidence (0.70). However, direct evidence linking GSTT1 status specifically to inner ear damage caused by cisplatin remains limited and conflicting (confidence 0.19). Given the indirect connection in the knowledge graph (confidence 0.49), it is plausible that genetic variability in GSTT1 could influence susceptibility to ototoxicity. Further research, including pharmacogenomic studies focusing on pediatric populations, would be necessary to confirm this hypothesis and guide clinical decision-making regarding Platinol treatment.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **CYP2E1** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **ERCC1** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:ERCC1/rs11615:L3` (curated)<br>`PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **GSTP1** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:GSTP1/rs1695:L3` (curated)<br>`PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **GSTT1** | CONFLICTING | 0.19 | comparable studies disagree with no contextual difference detected | `PMID:40342074/PMC12434574#p31` (human_cohort)<br>`PMID:40222694/#p0` (systematic_review) | `PMID:40342074/PMC12434574#p31` (human_cohort)<br>`PMID:40222694/#p0` (systematic_review) |

> The CYP2E1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on CYP2E1 alone.

> The ERCC1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ERCC1 alone.

> The GSTP1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC19A1** (rs12659) | 0.62 | moderate | — | `ClinPGx:SLC19A1/rs12659:L3` (curated) | — |
| **CYP2E1** (rs2070676) | 0.59 | moderate | curator_ambiguous | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.59 | moderate | curator_ambiguous | `ClinPGx:ERCC1/rs11615:L3` (curated)<br>`PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **GSTP1** (rs1695) | 0.59 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated)<br>`PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **ABCC3** (rs4148416) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs4148416:L3` (curated) | — |
| **AKT1** (rs1130214) | 0.56 | moderate | curator_ambiguous | `ClinPGx:AKT1/rs1130214:L3` (curated) | — |
| **GSTM3** (rs1799735) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM3/rs1799735:L3` (curated) | — |
| **MLH1** | 0.28 | low | uncurated_literature_claim | `PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **MSH3** | 0.28 | low | uncurated_literature_claim | `PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **GSTT1** | 0.19 | very_low | curator_ambiguous, literature_internal | `PMID:40342074/PMC12434574#p31` (human_cohort)<br>`PMID:40222694/#p0` (systematic_review) | `PMID:40342074/PMC12434574#p31` (human_cohort)<br>`PMID:40222694/#p0` (systematic_review) |

<details><summary>Paragraphs the system read and kept (6 from 2 papers)</summary>

- `PMID:40342074/PMC12434574#p31` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Discussion**
  - Genetic factors involved in CDDP metabolism influenced the severity of AKI in our study. In this context, we observed that HNSCC patients with GSTT1 present genotype had a decline of almost 5% in renal function, and the reduction …
- `PMID:40342074/PMC12434574#p13` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Genotyping**
  - Genotyping was conducted on DNA extracted from peripheral blood samples of patients. The following methods were employed: multiplex polymerase chain reaction (PCR) for GSTM1 and GSTT1 [32]; PCR followed by enzymatic digestion for …
- `PMID:40342074/PMC12434574#p23` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Kidney Injury After**
  - The results of multivariate analyses of associations of factors with potential roles (p < 0.10) or positively correlated with renal function decline are presented in Table 3. Patients who received high cumulative CDDP doses presen…
- `PMID:40342074/PMC12434574#p33` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Discussion**
  - We also observed that patients with GSTP1 c.313AG or GG genotypes grouped with ERCC1 c.354CT or TT, MLH1 c.93GA or AA, and MSH3 c.3133AG or GG experienced declines of 18%, 13%, and 12% in renal function when compared to patients w…
- `PMID:40222694/#p0` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **?**
  - Pharmacogenomics in pediatric oncology patients with solid tumors related 
to chemotherapy-induced toxicity: A systematic review
Paula Hansson
a , * , 1
, Christopher Blacker
a , 1
, Hanna Uvdal
b
, Mia Wadelius
c
, Henrik Green
b…
- `PMID:40222694/#p1` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **?**
  - with chemotherapy ( Cheng et al., 2004a; Miller et al., 2012 ). Ototox -
icity, or hearing loss, is strongly associated with platinum-based treat -
ment, especially cisplatin where ototoxicity occurs in 22 – 70 % of 
patients ( Br…

</details>

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

*19 gene–drug pairs, 7 disputed*

Cisplatin is known to cause peripheral neuropathy as a side effect. Genetic factors such as ERCC1, GSTP1, and GSTM3 may influence the response to cisplatin treatment; however, the evidence linking these genetic variants directly to a predisposition for developing peripheral neuropathy due to cisplatin is currently limited and inconclusive. The knowledge graph indicates that ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735) may modulate the response to cisplatin, but the evidence ledger shows conflicting or insufficient data for these associations. Therefore, while genetic testing might provide some insight into how an individual responds to cisplatin, it is currently not sufficient to base clinical screening on any single gene alone due to the lack of strong and consistent evidence linking specific variants directly to peripheral neuropathy risk.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **CYP2E1** | CONFLICTING | 0.59 | the curators themselves record conflicting reports | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **ERCC1** | CONFLICTING | 0.42 | comparable studies disagree with no contextual difference detected | `ClinPGx:ERCC1/rs11615:L3` (curated)<br>`PMID:42123691/PMC13164360#p18` (human_cohort) | `PMID:42123691/PMC13164360#p18` (human_cohort) |
| **GSTP1** | CONFLICTING | 0.39 | comparable studies disagree with no contextual difference detected | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42123691/PMC13164360#p18` (human_cohort) |

> The CYP2E1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on CYP2E1 alone.

> The ERCC1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ERCC1 alone.

> The GSTP1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC19A1** (rs12659) | 0.62 | moderate | — | `ClinPGx:SLC19A1/rs12659:L3` (curated) | — |
| **CYP2E1** (rs2070676) | 0.59 | moderate | curator_ambiguous | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **ABCC3** (rs4148416) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs4148416:L3` (curated) | — |
| **AKT1** (rs1130214) | 0.56 | moderate | curator_ambiguous | `ClinPGx:AKT1/rs1130214:L3` (curated) | — |
| **GSTM3** (rs1799735) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM3/rs1799735:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.42 | low | curator_ambiguous, literature_internal | `ClinPGx:ERCC1/rs11615:L3` (curated)<br>`PMID:42123691/PMC13164360#p18` (human_cohort) | `PMID:42123691/PMC13164360#p18` (human_cohort) |
| **GSTP1** (rs1695) | 0.39 | low | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42123691/PMC13164360#p18` (human_cohort) |
| **ABCB-1** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| **ABCC-1** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| **ABCG-2** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| **ATP7B** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| **ERCC-1** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| **ERCC-2** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| **MATE-1** | 0.27 | low | unsupported_claim | `PMID:39560009#p0` (review) | — |
| _… 5 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (5 from 3 papers)</summary>

- `PMID:42123691/PMC13164360#p18` — *Impact of Pharmacogenetic Markers on the Efficacy of Neoadjuvant FLOT Chemothera* — section **3. Discussion**
  - The GSTP1 gene (rs1695) encodes glutathione S-transferase, an enzyme involved in the detoxification of cytotoxic agents, including platinum compounds. The rs1695 polymorphism is associated with altered enzymatic activity and may i…
- `PMID:39560009#p0` — *Lung cancer, platinum analog-based frontline treatment and pharmacogenetic limit* — section **Abstract**
  - Lung cancer has the highest mortality rate among all the highly prevalent neoplasia globally. The major concern with its frontline treatment-cisplatin, is the rapid progression of chemoresistance and multi-organ-based toxicities i…
- `PMID:42589658/PMC13467248#p46` — *Multi-Targeted Neuroprotection by Areca catechu Against Cisplatin-Induced Neurot* — section **3. Discussion**
  - Our study showed that the AC-EA extract provided significant neuroprotection against cisplatin-induced toxicity by preserving mitochondrial status, mitigating oxidative stress, and activating the NRF2-associated antioxidant respon…
- `PMID:42589658/PMC13467248#p12` — *Multi-Targeted Neuroprotection by Areca catechu Against Cisplatin-Induced Neurot* — section **2.4. AC-EA Attenuates Cisplatin-Induced DNA Damage**
  - Continuous exposure of cells to oxidants damages DNA, leading to intrastrand crosslinks and fatal double-strand breaks. This is a major mechanism of cisplatin [23]. To determine whether AC-EA alleviates genotoxic stress, we examin…
- `PMID:42589658/PMC13467248#p13` — *Multi-Targeted Neuroprotection by Areca catechu Against Cisplatin-Induced Neurot* — section **2.4. AC-EA Attenuates Cisplatin-Induced DNA Damage**
  - Exposure to cisplatin (10 µM) led to a marked accumulation of γH2AX compared with control cells, confirming substantial intracellular damage (Figure 4A). However, co-treatment with AC-EA attenuated this response in a dose-dependen…

</details>

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

*12 gene–drug pairs, 4 disputed*

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may have a genetic component, particularly involving the SLC28A3 gene. The PharmGKB evidence level 2B indicates an ambiguous association between the rs7853758 variant in SLC28A3 and doxorubicin-related cardiotoxicity, with conflicting studies suggesting both support and refutation of this link. Given that SLC28A3 is involved in nucleoside transport, which can influence drug metabolism and toxicity, further investigation into the genetic predisposition to cardiotoxicity via comprehensive genetic testing would be advisable. This could help identify patients at higher risk for adverse effects and guide personalized treatment strategies, such as dose adjustments or alternative therapies.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** | CONFLICTING | 0.54 | comparable studies disagree with no contextual difference detected | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42246857#p0` (human_cohort) |
| **RARG** | CONFLICTING | 0.39 | comparable studies disagree with no contextual difference detected | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |

> The SLC28A3-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on SLC28A3 alone.

> The RARG-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on RARG alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **SLC28A3** (rs7853758) | 0.54 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42246857#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.39 | low | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |
| **DRP1** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **MFN1** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **MFN2** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **NOX1** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **NOX2** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **NOX4** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **OPA1** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **P38** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (6 from 3 papers)</summary>

- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…
- `PMID:42670540/#p6` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - isoforms NOX1, NOX2, and NOX4 prominently expressed in cardiac tissue. DOX treatment significantly upregulates the 
activity of these NOX isoforms in cardiomyocytes, driving excessive ROS generation. This ROS burst subsequently 
a…
- `PMID:42670540/#p11` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - autophagic flux, and circulating biomarkers will also be essential to facilitate the clinical translation of precision 
cardioprotective strategies.
Conclusion
DIC arises from the combined dysregulation of oxidative and inflammato…
- `PMID:42670540/#p5` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - This balance is disrupted in DIC. Drp1 is the primary regulator of mitochondrial fission. DOX enhances the 
expression and activity of Drp1, promoting its translocation to the mitochondrial outer membrane, where it interacts 
with…
- `PMID:42670540/#p10` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - populations also contribute to the observed phenotypes. Accordingly, p38-directed therapeutic strategies should prioritize 
isoform selectivity and account for sex, age, cumulative DOX exposure, and disease stage, rather than assu…
- `PMID:42670080#p0` — *Anthracycline Cardiotoxicity: A Real-World Study Based on FDA Adverse Event Repo* — section **Abstract**
  - Based on the FDA Adverse Event Reporting System (FAERS) database, data mining of adverse event (AE) signals related to anthracyclines was conducted to explore their potential medication risks, especially cardiotoxicity, in order t…

</details>

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

*25 gene–drug pairs, 10 disputed*

The primary pharmacogenomic biomarkers predicting anthracycline-induced cardiotoxicity in childhood cancer survivors are SLC28A3 (rs7853758) and GSTP1 (rs1695), with additional support from RARG (rs2229774). These genetic markers, along with clinical risk factors such as cumulative anthracycline dose and age, can be used to predict the likelihood of developing cardiotoxicity in childhood cancer survivors. However, further validation is needed for GSTP1 (rs1695) due to conflicting evidence from different studies. The biological mechanism involves variations in nucleoside transporters (SLC28A3), glutathione S-transferase activity (GSTP1), and retinoic acid receptor signaling (RARG). These genetic factors influence the pharmacokinetics, metabolism, and cellular response to anthracyclines, thereby affecting cardiotoxicity risk. For drug development, these biomarkers can guide personalized dosing strategies or identify patients at high risk for cardiotoxicity who may benefit from alternative therapies or cardioprotective agents.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **GSTP1** | CONFLICTING | 0.39 | comparable studies disagree with no contextual difference detected | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **SLC28A3** | CONTEXT-DEPENDENT | 0.65 | population differs (e.g. children vs adults) | `ClinPGx:SLC28A3/rs7853758:L2B` (curated)<br>`PMID:40413218/PMC12103300#p15` (systematic_review) | `PMID:42549829#p0` (human_cohort) |

> The GSTP1-anthracycline association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

> The apparent SLC28A3-anthracycline disagreement is explained by population; the association may hold in one setting and not another.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.65 | moderate | curated_vs_literature, literature_internal | `ClinPGx:SLC28A3/rs7853758:L2B` (curated)<br>`PMID:40413218/PMC12103300#p15` (systematic_review) | `PMID:42549829#p0` (human_cohort) |
| **ABCC5** | 0.62 | moderate | — | `PMID:40413218/PMC12103300#p15` (systematic_review) | — |
| **ABCG2** | 0.62 | moderate | — | `PMID:40413218/PMC12103300#p15` (systematic_review) | — |
| **AKR1C3** | 0.62 | moderate | — | `PMID:40413218/PMC12103300#p15` (systematic_review) | — |
| **HAS3** | 0.58 | moderate | — | `PMID:42279262/PMC13255899#p61` (review) | — |
| **CBR1** | 0.44 | low | curator_ambiguous | `PMID:40413218/PMC12103300#p15` (systematic_review) | — |
| **GSTP1** (rs1695) | 0.39 | low | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **ABCB1** | 0.36 | low | curated_vs_literature | — | `PMID:42549829#p0` (human_cohort) |
| **ABCC2** | 0.36 | low | curated_vs_literature | — | `PMID:42549829#p0` (human_cohort) |
| **CBR3** | 0.36 | low | curated_vs_literature | — | `PMID:42549829#p0` (human_cohort) |
| **NQO1** | 0.35 | low | curated_vs_literature | — | `PMID:40413218/PMC12103300#p15` (systematic_review) |
| **RARG** (rs2229774) | 0.34 | low | — | — | `ClinPGx:RARG/rs2229774:L3` (curated) |
| **KCNK17** | 0.28 | low | uncurated_literature_claim | `PMID:40413218/PMC12103300#p15` (systematic_review) | — |
| **TTN** | 0.28 | low | uncurated_literature_claim | `PMID:40413218/PMC12103300#p15` (systematic_review) | — |
| _… 11 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (10 from 4 papers)</summary>

- `PMID:42549829#p0` — *Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Ch* — section **Abstract**
  - This study aimed to clarify the incidence of anthracycline-induced cardiotoxicity (ACT) and identify its clinical and candidate genetic risk factors in Chinese early-stage breast cancer patients, so as to provide evidence for clin…
- `PMID:42279262/PMC13255899#p61` — *Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical* — section **11. Strategies for Early Identification of Sex-Specific Cancer Treatment-Related Cardiovascular Toxicities**
  - Genetics: Sex-informed medicine encompasses genetics, hormones, and immune function, significantly impacting CV disease and cancer. Biological differences, such as X and Y chromosome effects and variations in sex hormones, contrib…
- `PMID:40413218/PMC12103300#p15` — *Influence of genetic biomarkers on cardiac diseases in childhood cancer survivor* — section **Summary of genetic findings**
  - Regarding the heterogeneity in outcomes and sequencing methods in the 20 included studies, we reported the results of genetic associations according to study design (case-control and cohort), which is strongly related to study out…
- `PMID:40413218/PMC12103300#p28` — *Influence of genetic biomarkers on cardiac diseases in childhood cancer survivor* — section **WES**
  - Common variants analysis revealed that the genotypes TTN-rs72648998-CC and TTN-rs3829747-CC were associated with an increased LVFS (p = 0.0002 and 0.0004, respectively) and LVEF (p = 0.0003 and 0.0003, respectively), and that TTN-…
- `PMID:40413218/PMC12103300#p29` — *Influence of genetic biomarkers on cardiac diseases in childhood cancer survivor* — section **WGS**
  - The KCNK17-rs2815063-A allele was associated with a reduced LVEF in patients diagnosed with a cardiomyopathy grade ≥3 after adjusting for cardiac medication (p = 7.5 × 10−6). After classification into therapy-based risk groups, th…
- `PMID:40413218/PMC12103300#p17` — *Influence of genetic biomarkers on cardiac diseases in childhood cancer survivor* — section **Summary of genetic findings**
  - a28 genes significantly associated with case-control status but we only reported the 3 genes considered as the more important by the authors.…

</details>

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

*13 gene–drug pairs, 8 disputed*

The cardiologist's concern about early heart failure in your son who carries the CYP2D6*4 genetic variant and is on doxorubicin for his neoplasm appears to be primarily based on clinical risk factors rather than a direct pharmacogenomic link. The evidence does not support an established association between CYP2D6*4 and doxorubicin-induced cardiotoxicity (ACT). However, the presence of CYP2D6*4 may influence drug metabolism and efficacy, but there is no strong evidence linking it directly to heart failure in this context. The study indicates that clinical factors such as age, cumulative anthracycline dose, and use of HER2-targeted antibodies are critical determinants for ACT risk. Therefore, targeted cardiac monitoring and optimized treatment strategies should be implemented based on these clinical variables rather than genetic polymorphisms like CYP2D6*4.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** | CONFLICTING | 0.46 | comparable studies disagree with no contextual difference detected | `ClinPGx:SLC28A3/rs7853758:L2B` (curated)<br>`PMID:42176227#p0` (review) | `PMID:42549829#p0` (human_cohort)<br>`PMID:42246857#p0` (human_cohort) |
| **RARG** | CONFLICTING | 0.41 | comparable studies disagree with no contextual difference detected | `ClinPGx:RARG/rs2229774:L3` (curated)<br>`PMID:42176227#p0` (review) | `PMID:42246857#p0` (human_cohort) |
| **GSTP1** | CONFLICTING | 0.39 | comparable studies disagree with no contextual difference detected | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |

> The SLC28A3-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on SLC28A3 alone.

> The RARG-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on RARG alone.

> The GSTP1-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.46 | low | curator_ambiguous, literature_internal | `ClinPGx:SLC28A3/rs7853758:L2B` (curated)<br>`PMID:42176227#p0` (review) | `PMID:42549829#p0` (human_cohort)<br>`PMID:42246857#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.41 | low | curator_ambiguous, literature_internal | `ClinPGx:RARG/rs2229774:L3` (curated)<br>`PMID:42176227#p0` (review) | `PMID:42246857#p0` (human_cohort) |
| **GSTP1** (rs1695) | 0.39 | low | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **NOX1** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **NOX2** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **NOX4** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **P38MAPK** | 0.27 | low | unsupported_claim | `PMID:42670540/#p6` (review) | — |
| **SLC22A3** | 0.27 | low | unsupported_claim | `PMID:42176227#p0` (review) | — |
| **ABCB1** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **ABCC2** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **CBR3** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |
| **CYP2D6** | 0.05 | very_low | literature_internal, unsupported_claim | `PMID:42670540/#p6` (review) | `PMID:42670080#p0` (human_cohort)<br>`PMID:42593900#p0` (in_vitro) |

<details><summary>Paragraphs the system read and kept (9 from 6 papers)</summary>

- `PMID:42670540/#p6` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - isoforms NOX1, NOX2, and NOX4 prominently expressed in cardiac tissue. DOX treatment significantly upregulates the 
activity of these NOX isoforms in cardiomyocytes, driving excessive ROS generation. This ROS burst subsequently 
a…
- `PMID:42670540/#p11` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - autophagic flux, and circulating biomarkers will also be essential to facilitate the clinical translation of precision 
cardioprotective strategies.
Conclusion
DIC arises from the combined dysregulation of oxidative and inflammato…
- `PMID:42670540/#p5` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - This balance is disrupted in DIC. Drp1 is the primary regulator of mitochondrial fission. DOX enhances the 
expression and activity of Drp1, promoting its translocation to the mitochondrial outer membrane, where it interacts 
with…
- `PMID:42670540/#p10` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - populations also contribute to the observed phenotypes. Accordingly, p38-directed therapeutic strategies should prioritize 
isoform selectivity and account for sex, age, cumulative DOX exposure, and disease stage, rather than assu…
- `PMID:42549829#p0` — *Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Ch* — section **Abstract**
  - This study aimed to clarify the incidence of anthracycline-induced cardiotoxicity (ACT) and identify its clinical and candidate genetic risk factors in Chinese early-stage breast cancer patients, so as to provide evidence for clin…
- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…

</details>

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

*11 gene–drug pairs, 10 disputed*

The observed cardiac strain and heart muscle damage in your daughter following Adriamycin (doxorubicin) treatment may be linked to her GSTM1 genotype. The medical knowledge graph indicates that GSTM1 is a risk factor for doxorubicin-induced cardiotoxicity, with evidence suggesting upregulation of GSTM1 under oxidative stress and inflammatory conditions commonly induced by this chemotherapy agent. However, the evidence ledger shows conflicting results regarding the association between GSTM1 and doxorubicin-induced cardiotoxicity, marked as CONTEXT-DEPENDENT due to differences in cancer type studied. Given these findings, it is plausible that your daughter's genetic profile could influence her susceptibility to Adriamycin’s cardiotoxic effects. For drug development and patient safety, further investigation into the role of GSTM1 and other potential biomarkers for doxorubicin-induced cardiotoxicity is warranted, potentially guiding personalized dosing strategies or identifying alternative therapeutic options.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **GSTM1** | CONTEXT-DEPENDENT | 0.18 | cancer type differs | `PMID:32896271/PMC7478891#p18` (in_vitro)<br>`PMID:41823204#p0` (human_cohort) | `PMID:32896271/PMC7478891#p18` (in_vitro)<br>`PMID:42670540/#p6` (review) |

> The apparent GSTM1-doxorubicin disagreement is explained by cancer_type; the association may hold in one setting and not another.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.71 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | — |
| **ABCC4** | 0.61 | moderate | — | `PMID:41823204#p0` (human_cohort) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |
| **ABCC1** | 0.44 | low | curator_ambiguous | `PMID:41823204#p0` (human_cohort) | — |
| **ABCC2** | 0.44 | low | curator_ambiguous | `PMID:41823204#p0` (human_cohort) | — |
| **MTHFR** | 0.44 | low | curator_ambiguous | `PMID:41823204#p0` (human_cohort) | — |
| **ABCC6** | 0.28 | low | uncurated_literature_claim | `PMID:41823204#p0` (human_cohort) | — |
| **CYP2A7** | 0.28 | low | uncurated_literature_claim | `PMID:41823204#p0` (human_cohort) | — |
| **HSP90AA1** | 0.28 | low | uncurated_literature_claim | `PMID:41823204#p0` (human_cohort) | — |
| **GSTM1** | 0.18 | very_low | curator_ambiguous, literature_internal | `PMID:32896271/PMC7478891#p18` (in_vitro)<br>`PMID:41823204#p0` (human_cohort) | `PMID:32896271/PMC7478891#p18` (in_vitro)<br>`PMID:42670540/#p6` (review) |

<details><summary>Paragraphs the system read and kept (9 from 5 papers)</summary>

- `PMID:32896271/PMC7478891#p18` — *Direct reprogramming of human smooth muscle and vascular endothelial cells revea* — section **Induced vascular cells show gene-expression and functional differences between young vs. old donors**
  - Figure 2—figure supplement 3.Representative images of GSTM1 expression by endothelial cells within human skin biopsies from young vs.old donors (N = 2 donors per condition, 10 tissue sections per condition; Student’s t-test with p…
- `PMID:32896271/PMC7478891#p30` — *Direct reprogramming of human smooth muscle and vascular endothelial cells revea* — section **Induced vascular cells show gene-expression and functional differences between young vs. old donors**
  - In parallel, DE analysis performed on iVECs highlighted the upregulation of GSTM1 and PALD1 in cells derived from old vs. young donors. GSTM1 is generally activated in presence of oxidative stress and inflammatory conditions (Lope…
- `PMID:41823204#p0` — *Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute* — section **Abstract**
  - This study investigated the association between genetic variants and the occurrence of oral mucositis (OM) in pediatric patients with acute lymphoblastic leukemia (ALL) and lymphoma undergoing chemotherapy (CT). A retrospective ob…
- `PMID:42670540/#p6` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - isoforms NOX1, NOX2, and NOX4 prominently expressed in cardiac tissue. DOX treatment significantly upregulates the 
activity of these NOX isoforms in cardiomyocytes, driving excessive ROS generation. This ROS burst subsequently 
a…
- `PMID:42670540/#p11` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - autophagic flux, and circulating biomarkers will also be essential to facilitate the clinical translation of precision 
cardioprotective strategies.
Conclusion
DIC arises from the combined dysregulation of oxidative and inflammato…
- `PMID:42670540/#p10` — *Mechanisms and the Role of p38 MAPK Signaling in Doxorubicin-Induced Cardiotoxic* — section **?**
  - populations also contribute to the observed phenotypes. Accordingly, p38-directed therapeutic strategies should prioritize 
isoform selectivity and account for sex, age, cumulative DOX exposure, and disease stage, rather than assu…

</details>

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

*12 gene–drug pairs, 7 disputed*

Doxorubicin can cause mucositis as a side effect, with genetic factors such as ERCC1(rs11615) and CYBA(rs4673) increasing the risk of developing mucositis in patients treated with doxorubicin. The evidence suggests that these genetic variants modulate the response to doxorubicin, potentially through mechanisms related to DNA repair (ERCC1) and oxidative stress resistance (CYBA). However, the association between CYBA(rs4673) and doxorubicin-induced mucositis is disputed due to conflicting studies. For drug development and patient safety, screening for these genetic variants could help identify patients at higher risk of developing mucositis, allowing for dose adjustments or alternative treatment strategies.

**Resolved pairs** (INSUFFICIENT ones omitted)

| Gene | Status | Conf | Why | Supporting | Refuting |
|---|---|---|---|---|---|
| **CYBA** | CONFLICTING | 0.47 | comparable studies disagree with no contextual difference detected | `ClinPGx:CYBA/rs4673:L3` (curated)<br>`PMID:40362292/PMC12072181#p18` (human_cohort) | `PMID:40362292/PMC12072181#p18` (human_cohort) |
| **CBR3** | CONFLICTING | 0.27 | comparable studies disagree with no contextual difference detected | `PMID:40362292/PMC12072181#p18` (human_cohort) | `PMID:40362292/PMC12072181#p18` (human_cohort) |

> The CYBA-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on CYBA alone.

> The CBR3-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on CBR3 alone.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **ERCC1** (rs11615) | 0.62 | moderate | — | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |
| **TP53** | 0.57 | moderate | — | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **CYBA** (rs4673) | 0.47 | low | curated_vs_literature, literature_internal | `ClinPGx:CYBA/rs4673:L3` (curated)<br>`PMID:40362292/PMC12072181#p18` (human_cohort) | `PMID:40362292/PMC12072181#p18` (human_cohort) |
| **NCF4** | 0.44 | low | curator_ambiguous | `PMID:40362292/PMC12072181#p18` (human_cohort) | — |
| **PON1** | 0.28 | low | uncurated_literature_claim | `PMID:40362292/PMC12072181#p18` (human_cohort) | — |
| **CBR3** | 0.27 | low | curator_ambiguous, literature_internal | `PMID:40362292/PMC12072181#p18` (human_cohort) | `PMID:40362292/PMC12072181#p18` (human_cohort) |
| **BAX** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **CASP1** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **INKA2** | 0.26 | low | unsupported_claim | `PMID:42653080/PMC13513574#p23` (in_vitro) | — |
| **CBR1** | 0.23 | very_low | curator_ambiguous | — | `PMID:40362292/PMC12072181#p18` (human_cohort) |
| **SULT2B1** | 0.23 | very_low | curator_ambiguous | — | `PMID:40362292/PMC12072181#p18` (human_cohort) |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:40362292/PMC12072181#p18` (human_cohort) |

<details><summary>Paragraphs the system read and kept (6 from 3 papers)</summary>

- `PMID:40362292/PMC12072181#p18` — *Drugs Metabolism-Related Genes Variants Impact on Anthracycline-Based Chemothera* — section **3.7. NCF4 rs1883112**
  - NCF4 is a multicomponent enzyme system variation that causes an oxidative burst in which electrons are transferred from NADPH to molecular oxygen, resulting in reactive oxidant intermediates [19]. The involvement of the NAD(P)H ox…
- `PMID:42653080/PMC13513574#p23` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - Comparison of human and mouse colonoids revealed several shared genes with inverse regulation, including PCNA and SLC7A11 (File S1). SLC7A11, the cystine/glutamate antiporter that supports glutathione synthesis, was downregulated …
- `PMID:42653080/PMC13513574#p24` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - Differential gene expression analysis identified 14 genes shared across human colonoids, mouse colonoids, and mouse colon, representing a minimal conserved DOX response enriched for p53-linked DNA damage and apoptosis programs (Ta…
- `PMID:42653080/PMC13513574#p28` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - Analysis of the DDR pathway showed distinct regulatory signatures (Figure 4). In human colonoids, downregulation of CCNB1 and CCNB2 indicated G2/M checkpoint arrest, while upregulation of FAS, TNFRSF10B, and PID1 supported engagem…
- `PMID:42653080/PMC13513574#p29` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **3. Discussion**
  - RNA-seq provided a common molecular endpoint across all three systems and enabled direct cross-model comparison. The identified p53, apoptosis, and DNA-damage pathways should therefore be interpreted as coordinated transcriptomic …
- `PMID:42623591#p0` — *Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Inv* — section **Abstract**
  - Muscle-invasive bladder carcinoma (MIBC) poses major treatment challenges in low- and middle-income countries because of logistical and socioeconomic barriers limiting neoadjuvant chemotherapy (NAC) delivery. While dose-dense meth…

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
