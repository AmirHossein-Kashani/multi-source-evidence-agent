# Best configurations — outputs for the 10 ADR questions

Five configurations, same questions, same model. Phase 4 is the conservative curated baseline; phases 9L, 11 and 12 add per-paper reading and the evidence ledger, which reports **every** candidate gene with a rule-computed confidence and explicit contradictions; phase 13 additionally resolves each pair to a status and explains **why** the sources disagree.

| Configuration | Setup | Genes/question | On-topic | Catches false premise |
|---|---|---|---|---|
| Phase 4 | `pharmgkb+pubmed` | 2–3 | 22% | ✅ |
| Phase 9L | `pharmgkb+pubmed_combo` + digest + ledger | 11.6 | 52% | ❌ |
| Phase 11 | `pharmgkb+pubmed_free` + digest + ledger | 9.6 | 65% | ✅ |
| Phase 12 | as phase 11 + Europe PMC / Unpaywall full text | 9.1 | 63% | ✅ |
| Phase 13 | wide retrieval + digest + ledger + resolution | 14.5 | 49% | ❌ |

Confidence is computed by formula in `evidence_ledger.py` — the model never emits it. `disputed` means at least one contradiction flag fired.

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

### Phase 4 — ClinPGx + its cited literature

*Genes named: ACYP2, GSTM1*

The genetic variants ACYP2 (rs1872328) and GSTM1 are implicated in cisplatin-induced ototoxicity, with stronger evidence supporting the role of rs1872328. The biological mechanism likely involves impaired cellular detoxification or increased sensitivity to cisplatin's cytotoxic effects due to these genetic variations. For drug discovery and patient safety, pre-treatment screening for ACYP2 (rs1872328) could help identify patients at higher risk of ototoxicity, potentially allowing dose adjustments or the use of alternative agents such as carboplatin, which has a lower incidence of this side effect.

### Phase 9L — widest net + ledger

*18 gene–drug pairs, 8 disputed*

The genetic variants GSTM1 non-null, TPMT*1, and GADD45A are suggested to influence susceptibility to cisplatin-induced ototoxicity. However, the evidence for GSTM1 non-null and TPMT*1 is ambiguous (PharmGKB level 3), indicating a need for further validation. In contrast, genetic variants affecting GADD45A expression or function may contribute more directly to ototoxicity risk due to its role in inhibiting CXCL family protein expression, which exacerbates cisplatin-induced hearing loss. The biological mechanism involves GADD45A's influence on DNA damage and apoptosis pathways, as well as autophagic activity modulation. For drug development and patient safety, screening for genetic variants impacting GADD45A could help identify patients at higher risk of ototoxicity, potentially guiding dose adjustments or the use of otoprotective agents like honokiol to mitigate adverse effects.

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
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL3** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **GADD45A** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **IDH2** | 0.26 | low | unsupported_claim | `PMID:42617317#p0` (animal) | — |
| **NF-B1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
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

### Phase 11 — most precise + ledger

*19 gene–drug pairs, 10 disputed*

The ototoxicity you experienced after receiving cisplatin may be influenced by genetic variants such as GSTT1 null genotype, NFE2L2 rs6721961 (G-allele), and possibly variations in GADD45A. The GSTT1 null genotype is associated with reduced detoxification capabilities, leading to increased susceptibility to ototoxicity. Similarly, the G-allele of NFE2L2 rs6721961 affects antioxidant defense mechanisms crucial for protecting against cisplatin-induced oxidative stress. Variations in GADD45A may influence cellular responses to stress and inflammation, further contributing to ototoxic risk. These findings suggest that genetic screening could help identify patients at higher risk of hearing loss and tinnitus before initiating cisplatin therapy, allowing for dose adjustments or alternative treatment strategies.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.59 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **XPC** (rs2228001) | 0.59 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated)<br>`PMID:41532599#p0` (systematic_review) | — |
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **TPMT** (TPMT*1) | 0.56 | moderate | curator_ambiguous | `ClinPGx:TPMT/TPMT*1:L3` (curated) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **NFE2L2** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL3** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **GADD45A** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **NF-B1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| _… 5 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (6 from 3 papers)</summary>

- `PMID:42633148/PMC13499120#p47` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Abbreviations**
  - ABR: Auditory brainstem response AKI: Acute kidney injury AMPK: AMP-activated protein kinase BAX: BCL2-associated X protein BCL-2: B-cell lymphoma 2 BECN1: Beclin 1 BFA: Brefeldin A BIRC5: Baculoviral IAP repeat containing 5 CCK-8…
- `PMID:42633148/PMC13499120#p18` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - To elucidate the mechanism by which Gadd45a knockout protects cells from cisplatin-induced toxicity, we collected protein samples from both the control and Gadd45a-/- groups for Western blotting analysis at various time points aft…
- `PMID:42633148/PMC13499120#p32` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Injection of si**
  - To evaluate the efficacy of siGadd45a knockdown in mitigating cisplatin ototoxicity, we first performed audiometry on mice to establish a baseline for subsequent experiments. Mice with qualified baseline audiometric profiles were …
- `PMID:42633148/PMC13499120#p14` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - Based on DNA topoisomerase II alpha (TOP2A), baculoviral IAP repeat-containing 5 (BIRC5), and GADD45A in platinum resistance and cell survival pathways [45], [46], [47], [48], we measured TOP2Α, BIRC5, and GADD45A protein expressi…
- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…
- `PMID:41532599#p0` — *The association between DNA repair genes polymorphisms and cisplatin-induced oto* — section **Abstract**
  - Ototoxicity is a dose-limiting toxicity of cisplatin. Several DNA repair gene polymorphisms have been investigated for their association with cisplatin-induced ototoxicity (CIO), but their predictive value remains controversial. T…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: GSTM1*

The non-null genotype of GSTM1 is strongly associated with an increased risk of cisplatin-induced ototoxicity in pediatric cancer patients, suggesting a critical role for glutathione S-transferase activity in the detoxification process. The biological mechanism likely involves impaired cellular defense against oxidative stress and reduced ability to mitigate cisplatin's toxic effects on auditory hair cells. For drug discovery and patient safety, pre-treatment genetic screening for GSTM1 status could inform personalized dosing strategies or alternative therapeutic options to minimize ototoxicity risk in susceptible patients.

### Phase 9L — widest net + ledger

*19 gene–drug pairs, 12 disputed*

Cisplatin-induced ototoxicity risk in pediatric cancer patients is associated with several genetic variants including GSTM1 (GSTM1 non-null), TPMT (TPMT*1), and COMT (rs4646316, rs9332377). The biological mechanism involves the modulation of cisplatin metabolism and detoxification pathways by these genes. For instance, GSTM1 is involved in glutathione conjugation, which can influence the clearance and toxicity of cisplatin. TPMT's role in methylation processes may also affect drug metabolism and susceptibility to ototoxicity. COMT variants impact dopamine catabolism but their exact mechanism in ototoxicity remains unclear. These findings suggest that genetic screening for these variants could help identify patients at higher risk of ototoxicity, enabling personalized dosing or the use of alternative therapies to mitigate adverse effects.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.64 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **ABCC3** (rs1051640) | 0.59 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated)<br>`PMID:40222694#p0` (systematic_review) | — |
| **SLC22A2** (rs316019) | 0.59 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated)<br>`PMID:40222694#p0` (systematic_review) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **TPMT** (TPMT*1) | 0.50 | moderate | curator_ambiguous, literature_internal | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:40222694#p0` (systematic_review) | `PMID:41637682#p0` (review) |
| **GSTM1** (GSTM1 non-null) | 0.50 | low | curator_ambiguous, literature_internal | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated)<br>`PMID:39386217/PMC11461197#p8` (animal) | `PMID:39386217/PMC11461197#p8` (animal) |
| **ACYP2** | 0.45 | low | curator_ambiguous | `PMID:36802061#p0` (meta_analysis) | — |
| **ERCC2** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **GSTP1** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **LRP2** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **GSTT1** | 0.38 | low | curator_ambiguous, literature_internal | `PMID:39386217/PMC11461197#p8` (animal)<br>`PMID:40222694#p0` (systematic_review) | `PMID:39386217/PMC11461197#p8` (animal) |
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (animal) | — |
| _… 5 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (11 from 5 papers)</summary>

- `PMID:39386217/PMC11461197#p8` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **The expression levels of both GSTM1 and GSTT1 were significantly reduced in patients with AKI**
  - The expression of both GSTM1 and GSTT1 were significantly reduced in AKI patients (A) Immunohistochemical staining results of GSTT1, GSTM1 and KIM-1 in renal puncture tissue of AKI patients and para-cancerous control tissue. (B) Q…
- `PMID:39386217/PMC11461197#p9` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **The expression levels of both GSTM1 and GSTT1 were significantly reduced in mice with cisplatin-induced AKI**
  - Mice received intraperitoneal injections of saline or cisplatin, and the expression levels of GSTT1 and GSTM1 were measured. Compared to the WT + saline group, blood urea nitrogen (BUN) and creatinine (CREA) levels were significan…
- `PMID:39386217/PMC11461197#p10` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **The expression levels of both GSTM1 and GSTT1 were significantly reduced in mice with cisplatin-induced AKI**
  - The expression of both GSTM1 and GSTT1 were significantly reduced in mice with cisplatin-induced AKI. (A) the BUN and CERA levels after 3 days of cisplatin and saline injection. n=6. (B) the expression of kim-1 was detected by imm…
- `PMID:39386217/PMC11461197#p16` — *GSTT1/GSTM1 deficiency aggravated cisplatin-induced acute kidney injury via ROS-* — section **Normal kidney function in GSTM1-KO, GSTT1-KO, and Gstm1/Gstt1-DKO mice**
  - The GSTM1/GSTT1 double-genotype deletion is frequently observed in the general population and is associated with an increased risk of various diseases, including cancer and kidney diseases (28–30). These proteins belong to the GST…
- `PMID:40222694#p0` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **Abstract**
  - Chemotherapy-induced toxicities remain challenging in pediatric oncology, affecting patient outcomes, hospital stays, and quality of life. Genetic variation can partly explain these toxicities, and pharmacogenomics could potential…
- `PMID:41637682#p0` — *TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.* — section **Abstract**
  - To assess the ongoing citation of the 2009 Nature Genetics article by Ross et al linking TPMT to cisplatin-induced ototoxicity and to evaluate the extent to which its disputed findings persist in the literature. A total of 378 Goo…

</details>

### Phase 11 — most precise + ledger

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

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: TPMT, ACYP2 (rs1872328), GSTM1*

The high risk of hearing loss in your daughter while on cisplatin for Neuroblastoma is likely influenced by genetic factors including TPMT, ACYP2 (rs1872328), and GSTM1. The biological mechanism involves altered drug metabolism and detoxification pathways that may exacerbate ototoxicity due to these variants. For patient safety, pre-treatment biomarker screening for these variants should be considered to identify high-risk patients who might benefit from dose adjustments or alternative agents with a lower risk of ototoxicity.

### Phase 9L — widest net + ledger

*19 gene–drug pairs, 12 disputed*

Your daughter's high risk for hearing loss due to her TPMT variant while being treated with cisplatin for Neuroblastoma is a significant concern. The TPMT variant affects drug metabolism, potentially leading to increased ototoxicity from cisplatin. Research indicates that patients with TPMT variants are at higher risk of developing cisplatin-induced hearing loss, especially when receiving high-intensity dosing regimens common in treating Neuroblastoma. Given the conflicting evidence and methodological limitations noted in some studies, it is crucial to closely monitor her hearing during treatment and consider dose adjustments or alternative treatments based on genetic testing results. This highlights the importance of integrating pharmacogenomics into clinical practice for optimizing patient safety.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.62 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **ABCC3** (rs1051640) | 0.59 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated)<br>`PMID:40222694#p0` (systematic_review) | — |
| **SLC22A2** (rs316019) | 0.59 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated)<br>`PMID:40222694#p0` (systematic_review) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **ACYP2** | 0.44 | low | curator_ambiguous | `PMID:37726872#p0` (systematic_review) | — |
| **ERCC2** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **GSTP1** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **LRP2** | 0.44 | low | curator_ambiguous | `PMID:40222694#p0` (systematic_review) | — |
| **TPMT** (TPMT*1) | 0.41 | low | curator_ambiguous, literature_internal | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:40222694#p0` (systematic_review) | `PMID:41637682#p0` (review)<br>`PMID:42504125#p0` (human_cohort) |
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (in_vitro) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (in_vitro) | — |
| _… 5 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (9 from 6 papers)</summary>

- `PMID:41637682#p0` — *TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.* — section **Abstract**
  - To assess the ongoing citation of the 2009 Nature Genetics article by Ross et al linking TPMT to cisplatin-induced ototoxicity and to evaluate the extent to which its disputed findings persist in the literature. A total of 378 Goo…
- `PMID:40222694#p0` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **Abstract**
  - Chemotherapy-induced toxicities remain challenging in pediatric oncology, affecting patient outcomes, hospital stays, and quality of life. Genetic variation can partly explain these toxicities, and pharmacogenomics could potential…
- `PMID:42504125#p0` — *Incidence and Severity of Carboplatin-Associated Hearing Loss in Children With C* — section **Abstract**
  - Platinum-based chemotherapy is known to cause severe and debilitating hearing loss, but unlike cisplatin, the true incidence of carboplatin-induced hearing loss remains unclear. We evaluated functional hearing outcomes in children…
- `PMID:37726872#p0` — *Systematic Critical Review of Genetic Factors Associated with Cisplatin-induced * — section **Abstract**
  - Cisplatin is commonly used to treat solid tumors; however, its use can be complicated by drug-induced hearing loss (ie, ototoxicity). The presence of certain genetic variants has been associated with the development/occurrence of …
- `PMID:36917731#p0` — *Role of Cisplatin Dose Intensity and TPMT Variation in the Development of Hearin* — section **Abstract**
  - Cisplatin, widely used in the treatment of solid tumors, causes permanent hearing loss in more than 60% of treated children. Previous studies have implicated several clinical factors in the development of ototoxicity, including cu…
- `PMID:42633148/PMC13499120#p47` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Abbreviations**
  - ABR: Auditory brainstem response AKI: Acute kidney injury AMPK: AMP-activated protein kinase BAX: BCL2-associated X protein BCL-2: B-cell lymphoma 2 BECN1: Beclin 1 BFA: Brefeldin A BIRC5: Baculoviral IAP repeat containing 5 CCK-8…

</details>

### Phase 11 — most precise + ledger

*18 gene–drug pairs, 10 disputed*

Your daughter's TPMT variant increases her risk for cisplatin-induced ototoxicity due to altered drug metabolism, potentially leading to higher levels of the toxic compound in her system. The genetic variants GSTT1 and NRF2 also contribute to increased susceptibility to hearing loss from cisplatin treatment, as they affect antioxidant defense mechanisms crucial for mitigating oxidative stress caused by the drug. Given these factors, it is advisable to closely monitor your daughter's auditory function during cisplatin therapy and consider alternative treatments or adjunctive therapies that might reduce ototoxicity risks while maintaining effective cancer management.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **COMT** (rs4646316) | 0.59 | moderate | curator_ambiguous | `ClinPGx:COMT/rs4646316:L3` (curated)<br>`ClinPGx:COMT/rs9332377:L3` (curated) | — |
| **ABCC3** (rs1051640) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs1051640:L3` (curated) | — |
| **GSTM1** (GSTM1 non-null) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM1/GSTM1 non-null:L3` (curated) | — |
| **SLC16A5** (rs4788863) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC16A5/rs4788863:L3` (curated) | — |
| **SLC22A2** (rs316019) | 0.56 | moderate | curator_ambiguous | `ClinPGx:SLC22A2/rs316019:L3` (curated) | — |
| **XPC** (rs2228001) | 0.56 | moderate | curator_ambiguous | `ClinPGx:XPC/rs2228001:L3` (curated) | — |
| **ACYP2** | 0.44 | low | curator_ambiguous | `PMID:37726872#p0` (systematic_review) | — |
| **GSTT1** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **NFE2L2** | 0.44 | low | curator_ambiguous | `PMID:38518393#p0` (human_cohort) | — |
| **TPMT** (TPMT*1) | 0.37 | low | curator_ambiguous, literature_internal | `ClinPGx:TPMT/TPMT*1:L3` (curated)<br>`PMID:37726872#p0` (systematic_review) | `PMID:41637682#p0` (review)<br>`PMID:42504125#p0` (human_cohort) |
| **MT-RNR1** | 0.27 | low | unsupported_claim | `PMID:42524757#p0` (review) | — |
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (in_vitro) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (in_vitro) | — |
| **CXCL3** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p47` (in_vitro) | — |
| _… 4 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (9 from 6 papers)</summary>

- `PMID:42633148/PMC13499120#p47` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Abbreviations**
  - ABR: Auditory brainstem response AKI: Acute kidney injury AMPK: AMP-activated protein kinase BAX: BCL2-associated X protein BCL-2: B-cell lymphoma 2 BECN1: Beclin 1 BFA: Brefeldin A BIRC5: Baculoviral IAP repeat containing 5 CCK-8…
- `PMID:42633148/PMC13499120#p18` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - To elucidate the mechanism by which Gadd45a knockout protects cells from cisplatin-induced toxicity, we collected protein samples from both the control and Gadd45a-/- groups for Western blotting analysis at various time points aft…
- `PMID:42633148/PMC13499120#p32` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Injection of si**
  - To evaluate the efficacy of siGadd45a knockdown in mitigating cisplatin ototoxicity, we first performed audiometry on mice to establish a baseline for subsequent experiments. Mice with qualified baseline audiometric profiles were …
- `PMID:42633148/PMC13499120#p14` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - Based on DNA topoisomerase II alpha (TOP2A), baculoviral IAP repeat-containing 5 (BIRC5), and GADD45A in platinum resistance and cell survival pathways [45], [46], [47], [48], we measured TOP2Α, BIRC5, and GADD45A protein expressi…
- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…
- `PMID:41637682#p0` — *TPMT-Cisplatin: Lessons in Citation Integrity and Scientific Oversight.* — section **Abstract**
  - To assess the ongoing citation of the 2009 Nature Genetics article by Ross et al linking TPMT to cisplatin-induced ototoxicity and to evaluate the extent to which its disputed findings persist in the literature. A total of 378 Goo…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: GSTT1*

The permanent inner ear damage observed after Platinol treatment may be influenced by the GSTT1 status, a genetic polymorphism affecting glutathione S-transferase theta 1 (GSTT1), which is involved in detoxifying and metabolizing drugs like cisplatin. Individuals with a null genotype for GSTT1 have reduced capacity to metabolize these drugs, potentially leading to higher toxicity and ototoxicity. This finding underscores the importance of pre-treatment genetic screening for GSTT1 status to predict drug metabolism efficiency and adjust dosing accordingly or consider alternative agents with lower ototoxic risk.

### Phase 9L — widest net + ledger

*10 gene–drug pairs, 9 disputed*

The permanent inner ear damage experienced by your child after Platinol (cisplatin) treatment may be influenced by her GSTT1 status. The medical literature and knowledge graph indicate that the absence of GSTT1 can increase susceptibility to ototoxicity from platinum-based drugs like cisplatin, as GSTT1 is involved in detoxifying these agents through glutathione S-transferase activity. This genetic variability underscores the importance of considering pharmacogenomic factors when prescribing Platinol, particularly for pediatric patients. For drug discovery and patient safety, biomarker screening for GSTT1 status could help identify at-risk individuals who may benefit from dose adjustments or alternative therapeutic options to mitigate ototoxicity risks.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC19A1** (rs12659) | 0.62 | moderate | — | `ClinPGx:SLC19A1/rs12659:L3` (curated) | — |
| **CYP2E1** (rs2070676) | 0.59 | moderate | curator_ambiguous | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.59 | moderate | curator_ambiguous | `ClinPGx:ERCC1/rs11615:L3` (curated)<br>`PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **GSTP1** (rs1695) | 0.59 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated)<br>`PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **ABCC3** (rs4148416) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs4148416:L3` (curated) | — |
| **AKT1** (rs1130214) | 0.56 | moderate | curator_ambiguous | `ClinPGx:AKT1/rs1130214:L3` (curated) | — |
| **GSTM3** (rs1799735) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM3/rs1799735:L3` (curated) | — |
| **GSTT1** | 0.30 | low | curator_ambiguous, literature_internal | `PMID:40342074/PMC12434574#p31` (human_cohort)<br>`PMID:40222694#p0` (systematic_review) | `PMID:40342074/PMC12434574#p31` (human_cohort) |
| **MLH1** | 0.28 | low | uncurated_literature_claim | `PMID:40342074/PMC12434574#p31` (human_cohort) | — |
| **MSH3** | 0.28 | low | uncurated_literature_claim | `PMID:40342074/PMC12434574#p31` (human_cohort) | — |

<details><summary>Paragraphs the system read and kept (5 from 2 papers)</summary>

- `PMID:40342074/PMC12434574#p31` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Discussion**
  - Genetic factors involved in CDDP metabolism influenced the severity of AKI in our study. In this context, we observed that HNSCC patients with GSTT1 present genotype had a decline of almost 5% in renal function, and the reduction …
- `PMID:40342074/PMC12434574#p13` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Genotyping**
  - Genotyping was conducted on DNA extracted from peripheral blood samples of patients. The following methods were employed: multiplex polymerase chain reaction (PCR) for GSTM1 and GSTT1 [32]; PCR followed by enzymatic digestion for …
- `PMID:40342074/PMC12434574#p23` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Kidney Injury After**
  - The results of multivariate analyses of associations of factors with potential roles (p < 0.10) or positively correlated with renal function decline are presented in Table 3. Patients who received high cumulative CDDP doses presen…
- `PMID:40342074/PMC12434574#p33` — *Genetic Variability in Cisplatin Metabolism in Kidney Injury in Patients With He* — section **Discussion**
  - We also observed that patients with GSTP1 c.313AG or GG genotypes grouped with ERCC1 c.354CT or TT, MLH1 c.93GA or AA, and MSH3 c.3133AG or GG experienced declines of 18%, 13%, and 12% in renal function when compared to patients w…
- `PMID:40222694#p0` — *Pharmacogenomics in pediatric oncology patients with solid tumors related to che* — section **Abstract**
  - Chemotherapy-induced toxicities remain challenging in pediatric oncology, affecting patient outcomes, hospital stays, and quality of life. Genetic variation can partly explain these toxicities, and pharmacogenomics could potential…

</details>

### Phase 11 — most precise + ledger

*16 gene–drug pairs, 7 disputed*

The permanent inner ear damage experienced by your child after Platinol (cisplatin) treatment may be influenced by her GSTT1 status, particularly if she has a null genotype for GSTT1. The study PMID:38518393 indicates that patients with the GSTT1 null genotype are more susceptible to cisplatin-induced ototoxicity. This genetic factor could explain why your child experienced permanent inner ear damage despite receiving standard chemotherapy protocols. For drug discovery and patient safety, it is crucial to screen for GSTT1 status in patients undergoing cisplatin treatment to identify those at higher risk of ototoxicity. Biomarker screening can help tailor dosing regimens or explore alternative agents with lower ototoxic potential.

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
| **CXCL1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p18` (animal) | — |
| **CXCL10** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p18` (animal) | — |
| **CXCL3** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p18` (animal) | — |
| **GADD45A** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p18` (animal) | — |
| **NF-B1** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p18` (animal) | — |
| **RELA** | 0.26 | low | unsupported_claim | `PMID:42633148/PMC13499120#p18` (animal) | — |
| _… 2 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (5 from 2 papers)</summary>

- `PMID:42633148/PMC13499120#p18` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - To elucidate the mechanism by which Gadd45a knockout protects cells from cisplatin-induced toxicity, we collected protein samples from both the control and Gadd45a-/- groups for Western blotting analysis at various time points aft…
- `PMID:42633148/PMC13499120#p14` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - Based on DNA topoisomerase II alpha (TOP2A), baculoviral IAP repeat-containing 5 (BIRC5), and GADD45A in platinum resistance and cell survival pathways [45], [46], [47], [48], we measured TOP2Α, BIRC5, and GADD45A protein expressi…
- `PMID:42633148/PMC13499120#p20` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - To investigate transcriptomic alterations associated with Gadd45a depletion, control and Gadd45a-/- OC1 cells were subjected to transcriptome sequencing. Hierarchical clustering analysis demonstrated a clear separation between the…
- `PMID:42633148/PMC13499120#p34` — *Gadd45a knockout alleviates cisplatin-induced hearing loss by inhibiting CXCL fa* — section **Results**
  - A Gadd45a knockout allele was generated by inserting LoxP sites flanking exons 1–3. Cre-mediated recombination excises this region and disrupts the Gadd45a coding sequence (Additional file 1: Fig. S6a). Gadd45a cKO mice underwent …
- `PMID:38518393#p0` — *Combined genetic polymorphisms of the GSTT1 and NRF2 genes increase susceptibili* — section **Abstract**
  - The genotype-phenotype relationship in cisplatin-induced ototoxicity remains unclear. By assessing early shifts in distortion product otoacoustic emission (DPOAE) levels after initial cisplatin administration, we aimed to discrimi…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: ERCC1, GSTP1, GSTM3*

Cisplatin-induced peripheral neuropathy is influenced by genetic polymorphisms such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735). These variants likely affect the drug's metabolism, DNA repair mechanisms, or cellular sensitivity to cisplatin, thereby modulating the risk of developing peripheral neuropathy. For drug discovery and patient safety, pre-treatment genetic screening for these polymorphisms can help predict susceptibility to adverse effects, allowing for dose adjustments or alternative therapeutic strategies to mitigate risks.

### Phase 9L — widest net + ledger

*18 gene–drug pairs, 6 disputed*

Cisplatin is known to cause peripheral neuropathy as a side effect. Genetic factors such as ERCC1 (rs11615), GSTP1 (rs1695), and GSTM3 (rs1799735) may influence the response to cisplatin treatment, but there is no conclusive evidence that these genetic variants cause a predisposition to peripheral neuropathy due to cisplatin. The biological mechanism likely involves variations in detoxification pathways or DNA repair processes influenced by these genes. For drug development and patient safety, it is important to consider biomarker screening for these genetic variants to identify patients at higher risk of developing peripheral neuropathy, potentially allowing for dose adjustments or the use of alternative agents.

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
| _… 4 more pairs_ | | | | | |

<details><summary>Paragraphs the system read and kept (6 from 4 papers)</summary>

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
- `PMID:42573969#p0` — *An NLRP3 inflammasome inhibitor evoked dose-dependent anti-allodynia in the hind* — section **Abstract**
  - Patients receiving chemotherapy for cancer treatment may develop chemotherapy-induced peripheral neuropathy (CIPN), a type of neuropathic (nerve) pain that is often difficult to treat. First-line analgesic/adjuvant agents recommen…

</details>

### Phase 11 — most precise + ledger

*7 gene–drug pairs, 6 disputed*

Cisplatin is known to cause peripheral neuropathy as a side effect, with genetic factors potentially influencing susceptibility. The evidence suggests that while ERCC1 (rs11615), GSTP1 (rs1695), and other genes like SLC19A1 may modulate the response to cisplatin, no definitive causal relationship has been established between these genetic variants and a predisposition specifically induced by cisplatin. The conflicting evidence for GSTP1 indicates that its association with peripheral neuropathy is more specific to oxaliplatin rather than cisplatin. This implies that while genetic screening might help identify patients at higher risk of developing peripheral neuropathy when treated with cisplatin, the relationship between these genes and the drug's side effects remains uncertain. Therefore, further research is needed to clarify the role of these genetic factors in predicting cisplatin-induced peripheral neuropathy.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC19A1** (rs12659) | 0.62 | moderate | — | `ClinPGx:SLC19A1/rs12659:L3` (curated) | — |
| **CYP2E1** (rs2070676) | 0.59 | moderate | curator_ambiguous | `ClinPGx:CYP2E1/rs6413432:L3` (curated)<br>`ClinPGx:CYP2E1/rs2070676:L3` (curated) | — |
| **GSTP1** (rs1695) | 0.59 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated)<br>`PMID:30854066#p0` (human_cohort) | — |
| **ABCC3** (rs4148416) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ABCC3/rs4148416:L3` (curated) | — |
| **AKT1** (rs1130214) | 0.56 | moderate | curator_ambiguous | `ClinPGx:AKT1/rs1130214:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.56 | moderate | curator_ambiguous | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |
| **GSTM3** (rs1799735) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTM3/rs1799735:L3` (curated) | — |

<details><summary>Paragraphs the system read and kept (2 from 2 papers)</summary>

- `PMID:42573969#p0` — *An NLRP3 inflammasome inhibitor evoked dose-dependent anti-allodynia in the hind* — section **Abstract**
  - Patients receiving chemotherapy for cancer treatment may develop chemotherapy-induced peripheral neuropathy (CIPN), a type of neuropathic (nerve) pain that is often difficult to treat. First-line analgesic/adjuvant agents recommen…
- `PMID:30854066#p0` — *GSTP1 as a potential predictive factor for adverse events associated with platin* — section **Abstract**
  - Glutathione S-transferase (GST) exhibits antidotal effects on numerous drugs, including platinum-based antineoplastic drugs. Furthermore, GST Pi 1 (GSTP1) polymorphism is associated with peripheral neuropathy. In the present study…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: SLC28A3 (rs7853758), GSTP1 (rs1695)*

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may be influenced by genetic factors, particularly variants within the SLC28A3 (rs7853758) gene. This variant is associated with a reduced risk of anthracycline-induced cardiotoxicity, suggesting that its absence could contribute to increased susceptibility to doxorubicin's adverse effects. Additionally, polymorphisms in GSTP1 (rs1695) have been linked to heightened sensitivity to doxorubicin-related cardiotoxicity. These findings underscore the importance of genetic screening for these variants before initiating treatment with doxorubicin to identify patients at higher risk and potentially adjust dosing or consider alternative therapeutic options.

### Phase 9L — widest net + ledger

*6 gene–drug pairs, 6 disputed*

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may have a genetic component. The EVIDENCE LEDGER suggests that SLC28A3 (rs7853758), GSTP1 (rs1695), and RARG (rs2229774) are potential biomarkers for doxorubicin-induced cardiotoxicity, although the evidence is conflicting. The biological mechanism likely involves genetic variants affecting drug metabolism or transport, leading to altered pharmacokinetics and increased cardiotoxic risk. For pediatric lymphoma patients, further investigation into these genes and others specific to this patient population could identify novel biomarkers for personalized dosing strategies or alternative therapeutic options to mitigate cardiotoxicity risks.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **SLC28A3** (rs7853758) | 0.54 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42246857#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.39 | low | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |
| **CPVL** | 0.28 | low | uncurated_literature_claim | `PMID:42657460#p0` (human_cohort) | — |
| **PIGR** | 0.28 | low | uncurated_literature_claim | `PMID:42657460#p0` (human_cohort) | — |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (2 from 2 papers)</summary>

- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…
- `PMID:42657460#p0` — *Plasma Proteins Associated With the Immune Response to Anthracycline Cardiotoxic* — section **Abstract**
  - Anthracyclines such as doxorubicin are well recognized to induce dose-dependent cardiotoxicity. However, traditional imaging and blood biomarkers of myocardial injury are inadequate for early risk stratification. We aimed to disco…

</details>

### Phase 11 — most precise + ledger

*3 gene–drug pairs, 3 disputed*

The severe shortness of breath and heart muscle damage observed after doxorubicin treatment for pediatric lymphoma may have a genetic component. The genes SLC28A3 (rs7853758) and GSTP1 (rs1695) are associated with doxorubicin-induced cardiotoxicity, though the evidence is ambiguous (PharmGKB levels 2B and 3 respectively). These associations suggest that genetic variations in these genes could modulate an individual's susceptibility to doxorubicin's cardiotoxic effects. For drug discovery and patient safety, it would be prudent to screen for these genetic variants before initiating doxorubicin therapy or consider dose adjustments based on the identified genotype. Additionally, exploring alternative agents with lower cardiotoxicity profiles may also benefit patients with specific genetic predispositions.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.71 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |

<details><summary>Paragraphs the system read and kept (1 from 1 papers)</summary>

- `PMID:42643688#p0` — *Borneol-based nanoparticles encapsulating Doxorubicin/Sodium tanshinone IIA sulf* — section **Abstract**
  - Clinical treatment of brain glioma remains challenging due to chemotherapeutic resistance, cardiotoxicity and the presence of blood-brain barrier (BBB). Advanced nanoplatforms that can cross the BBB efficiently and target brain gl…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: SLC28A3 (rs7853758), RARG (rs2229774), GSTP1 (rs1695)*

The genes/variants implicated in anthracycline-induced cardiotoxicity include SLC28A3 (rs7853758), RARG (rs2229774), and GSTP1 (rs1695). SLC28A3 (rs7853758) is a protective variant, reducing the risk of cardiotoxicity in childhood cancer survivors. The biological mechanism likely involves altered nucleoside transport or metabolism affecting cardiac tissue sensitivity to anthracyclines. For drug discovery and patient safety, pre-treatment biomarker screening for these variants can help identify high-risk patients who may benefit from dose adjustments or alternative agents with lower cardiotoxic potential.

### Phase 9L — widest net + ledger

*9 gene–drug pairs, 7 disputed*

The pharmacogenomic biomarkers predicting anthracycline-induced cardiotoxicity in childhood cancer survivors are not definitively established. The PharmGKB database lists SLC28A3 (rs7853758) and RARG (rs2229774) as potential but ambiguous markers, with conflicting evidence from clinical studies refuting their association. Other SNPs like GSTP1 rs1695, ABCB1 rs1045642, ABCC2 rs8187710, and CBR3 rs1056892 also show low confidence due to conflicting evidence. The biological mechanism underlying these associations is not well-defined, but may involve altered drug metabolism or transport affecting cardiotoxicity risk. For drug development, further research is needed to identify definitive genetic predictors in childhood cancer survivors. Clinically, current biomarker screening for anthracycline-induced cardiotoxicity should focus on clinical factors such as cumulative dose and age at diagnosis rather than these genetic markers.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **HAS3** | 0.58 | moderate | — | `PMID:42279262/PMC13255899#p61` (review) | — |
| **SLC28A3** (rs7853758) | 0.46 | low | curator_ambiguous, literature_internal | `ClinPGx:SLC28A3/rs7853758:L2B` (curated)<br>`PMID:42176227#p0` (review) | `PMID:42549829#p0` (human_cohort)<br>`PMID:42246857#p0` (human_cohort) |
| **GSTP1** (rs1695) | 0.43 | low | curated_vs_literature | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.41 | low | curator_ambiguous, literature_internal | `ClinPGx:RARG/rs2229774:L3` (curated)<br>`PMID:42176227#p0` (review) | `PMID:42246857#p0` (human_cohort) |
| **ABCB1** | 0.36 | low | curated_vs_literature | — | `PMID:42549829#p0` (human_cohort) |
| **ABCC2** | 0.36 | low | curated_vs_literature | — | `PMID:42549829#p0` (human_cohort) |
| **CBR3** | 0.36 | low | curated_vs_literature | — | `PMID:42549829#p0` (human_cohort) |
| **SLC22A3** | 0.27 | low | unsupported_claim | `PMID:42176227#p0` (review) | — |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (4 from 4 papers)</summary>

- `PMID:42549829#p0` — *Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Ch* — section **Abstract**
  - This study aimed to clarify the incidence of anthracycline-induced cardiotoxicity (ACT) and identify its clinical and candidate genetic risk factors in Chinese early-stage breast cancer patients, so as to provide evidence for clin…
- `PMID:42279262/PMC13255899#p61` — *Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical* — section **11. Strategies for Early Identification of Sex-Specific Cancer Treatment-Related Cardiovascular Toxicities**
  - Genetics: Sex-informed medicine encompasses genetics, hormones, and immune function, significantly impacting CV disease and cancer. Biological differences, such as X and Y chromosome effects and variations in sex hormones, contrib…
- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…
- `PMID:42176227#p0` — *Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharm* — section **Abstract**
  - Doxorubicin, a prototypical anthracycline, remains an important component of breast cancer therapy, although its use has declined with the availability of effective non-anthracycline regimens and is increasingly restricted to sele…

</details>

### Phase 11 — most precise + ledger

*8 gene–drug pairs, 7 disputed*

The pharmacogenomic biomarkers that predict anthracycline-induced cardiotoxicity in childhood cancer survivors are not definitively established, but there is evidence suggesting a potential role for certain genetic variations such as SLC28A3 (rs7853758) and GSTP1 (rs1695). However, the current evidence level is low to moderate due to conflicting data from clinical studies. The likely biological mechanism involves altered drug transport or metabolism affecting anthracycline cardiotoxicity risk. For drug development, further validation of these biomarkers in larger cohorts is necessary before implementing them for patient safety measures such as dose adjustment or alternative agent selection.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **HAS3** | 0.58 | moderate | — | `PMID:42279262/PMC13255899#p61` (review) | — |
| **SLC28A3** (rs7853758) | 0.44 | low | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42549829#p0` (human_cohort)<br>`PMID:42246857#p0` (human_cohort) |
| **GSTP1** (rs1695) | 0.39 | low | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.39 | low | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |
| **ABCB1** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **ABCC2** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **CBR3** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (3 from 3 papers)</summary>

- `PMID:42549829#p0` — *Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Ch* — section **Abstract**
  - This study aimed to clarify the incidence of anthracycline-induced cardiotoxicity (ACT) and identify its clinical and candidate genetic risk factors in Chinese early-stage breast cancer patients, so as to provide evidence for clin…
- `PMID:42279262/PMC13255899#p61` — *Sex Differences in Cancer and Cardiotoxicity: Mechanisms, Outcomes, and Clinical* — section **11. Strategies for Early Identification of Sex-Specific Cancer Treatment-Related Cardiovascular Toxicities**
  - Genetics: Sex-informed medicine encompasses genetics, hormones, and immune function, significantly impacting CV disease and cancer. Biological differences, such as X and Y chromosome effects and variations in sex hormones, contrib…
- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: CYP2D6*4, SLC28A3*

The adverse heart failure reaction in your son treated with doxorubicin is likely influenced by his CYP2D6*4 genetic variant, which may alter drug metabolism and increase cardiotoxicity risk. Although there's no direct pharmacogenomic link between CYP2D6 and doxorubicin, the prolonged exposure to higher levels of doxorubicin due to reduced clearance could exacerbate cardiac side effects. Additionally, screening for SLC28A3 variants like rs7853758 might provide further insights into cardiotoxicity risk. For drug discovery and patient safety, pre-treatment genetic testing should be considered to identify high-risk patients who may benefit from dose adjustments or alternative treatments.

### Phase 9L — widest net + ledger

*8 gene–drug pairs, 8 disputed*

The early heart failure observed in your son who carries the CYP2D6*4 genetic variant and was treated with doxorubicin for his neoplasm is likely influenced by both genetic and clinical factors. The CYP2D6*4 variant, which affects drug metabolism, may increase susceptibility to doxorubicin-induced cardiotoxicity due to altered drug processing. However, the evidence ledger indicates that there is no strong support for a direct link between CYP2D6*4 and doxorubicin-induced heart failure risk. Other clinical factors such as cumulative anthracycline dose and age are significant contributors to this adverse reaction. Therefore, it is crucial to closely monitor cardiac function during and after treatment with doxorubicin, considering both genetic predisposition and clinical variables.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.44 | low | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42549829#p0` (human_cohort)<br>`PMID:42246857#p0` (human_cohort) |
| **GSTP1** (rs1695) | 0.39 | low | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | `PMID:42549829#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.39 | low | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |
| **ABCB1** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **ABCC2** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **CBR3** | 0.23 | very_low | curator_ambiguous | — | `PMID:42549829#p0` (human_cohort) |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |
| **CYP2D6** | 0.05 | very_low | literature_internal, unsupported_claim | `PMID:42176227#p0` (review) | `PMID:42657460#p0` (human_cohort)<br>`PMID:42593900#p0` (in_vitro) |

<details><summary>Paragraphs the system read and kept (5 from 5 papers)</summary>

- `PMID:42549829#p0` — *Clinical and genetic risk factors for anthracycline‑induced cardiotoxicity in Ch* — section **Abstract**
  - This study aimed to clarify the incidence of anthracycline-induced cardiotoxicity (ACT) and identify its clinical and candidate genetic risk factors in Chinese early-stage breast cancer patients, so as to provide evidence for clin…
- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…
- `PMID:42176227#p0` — *Doxorubicin-Induced Cardiotoxicity in Breast Cancer: Mechanistic Pathways, Pharm* — section **Abstract**
  - Doxorubicin, a prototypical anthracycline, remains an important component of breast cancer therapy, although its use has declined with the availability of effective non-anthracycline regimens and is increasingly restricted to sele…
- `PMID:42657460#p0` — *Plasma Proteins Associated With the Immune Response to Anthracycline Cardiotoxic* — section **Abstract**
  - Anthracyclines such as doxorubicin are well recognized to induce dose-dependent cardiotoxicity. However, traditional imaging and blood biomarkers of myocardial injury are inadequate for early risk stratification. We aimed to disco…
- `PMID:42593900#p0` — *Discovery of ZJC-11 as a Novel Selective CDK7 Inhibitor for Treating Triple-Nega* — section **Abstract**
  - The development of cyclin-dependent kinase 7 (CDK7) inhibitors represents a promising therapeutic strategy for triple-negative breast cancer (TNBC). Herein, we designed and synthesized 21 novel CDK7-targeted small molecules and id…

</details>

### Phase 11 — most precise + ledger

*7 gene–drug pairs, 3 disputed*

The concern about early heart failure in your son who carries the CYP2D6*4 genetic variant and was treated with doxorubicin for his neoplasm is well-founded. The CYP2D6*4 variant, which affects drug metabolism, may increase susceptibility to doxorubicin-induced cardiotoxicity due to altered drug processing. Although there is no direct evidence linking CYP2D6*4 specifically to doxorubicin from PharmGKB, the medical knowledge graph indicates a moderate risk factor for heart failure (confidence: 0.80). The specific type of cancer does not significantly alter this general risk but may influence treatment duration and dosage. For drug discovery and patient safety, screening for CYP2D6*4 could help identify patients at higher risk for cardiotoxicity, potentially guiding dose adjustments or the use of alternative agents to mitigate adverse effects.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.71 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |
| **MYH3** | 0.26 | low | unsupported_claim | `PMID:42612758#p0` (in_vitro) | — |
| **IFI16** | 0.20 | very_low | unsupported_claim | — | `PMID:42612758#p0` (in_vitro) |
| **KCTD14** | 0.20 | very_low | unsupported_claim | — | `PMID:42612758#p0` (in_vitro) |
| **CYP2D6** | 0.13 | very_low | unsupported_claim | — | `PMID:42643688#p0` (animal)<br>`PMID:42594973#p0` (in_vitro) |

<details><summary>Paragraphs the system read and kept (3 from 3 papers)</summary>

- `PMID:42643688#p0` — *Borneol-based nanoparticles encapsulating Doxorubicin/Sodium tanshinone IIA sulf* — section **Abstract**
  - Clinical treatment of brain glioma remains challenging due to chemotherapeutic resistance, cardiotoxicity and the presence of blood-brain barrier (BBB). Advanced nanoplatforms that can cross the BBB efficiently and target brain gl…
- `PMID:42594973#p0` — *Vincristine enhances doxorubicin cardiotoxicity in human iPSC-derived cardiomyoc* — section **Abstract**
  - Doxorubicin is a well-known cardiotoxic chemotherapeutic agent. Whether its combination with vincristine exacerbates cardiotoxicity and the underlying mechanisms remains unclear. Human induced pluripotent stem cell derived cardiom…
- `PMID:42612758#p0` — *Doxorubicin-induced damage to AC16 cardiomyocytes and attenuation by human peric* — section **Abstract**
  - Heart failure (HF) remains a leading cause of death worldwide. Stem cells represent a promising strategy for myocardial regeneration due to their differentiation potential and paracrine effects. This study investigated the effect …

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: GSTM1, SLC28A3 (rs7853758)*

The adverse cardiac effects observed in your daughter following Adriamycin treatment are likely influenced by genetic factors such as the GSTM1 genotype and a synonymous coding variant rs7853758 within the SLC28A3 gene. These genetic variations may modulate an individual's susceptibility to doxorubicin-induced cardiotoxicity through mechanisms that affect drug metabolism, transport, or cellular response pathways. For future drug discovery efforts and patient safety, pre-treatment biomarker screening for these variants could help identify patients at higher risk of developing heart damage from Adriamycin, enabling dose adjustments or the use of alternative therapies to mitigate this risk.

### Phase 9L — widest net + ledger

*4 gene–drug pairs, 4 disputed*

Adriamycin-induced cardiac strain and heart muscle damage are well-established side effects with high confidence levels. The GSTM1 gene, which has a moderate confidence level (0.40), may play a role as a risk factor for these adverse reactions due to its involvement in oxidative stress responses during chemotherapy treatments. Studies suggest that lower expression of GSTM1 could indicate increased susceptibility to Adriamycin's cardiotoxic effects. For drug discovery and patient safety, screening for GSTM1 expression levels before initiating Adriamycin treatment might help identify patients at higher risk of cardiac complications, potentially guiding dose adjustments or the use of alternative agents.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **SLC28A3** (rs7853758) | 0.71 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | — |
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **RARG** (rs2229774) | 0.56 | moderate | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | — |
| **GSTM1** | 0.40 | low | curator_ambiguous, literature_internal | `PMID:32896271/PMC7478891#p18` (in_vitro)<br>`PMID:41823204#p0` (human_cohort) | `PMID:42528395#p0` (in_vitro) |

<details><summary>Paragraphs the system read and kept (4 from 3 papers)</summary>

- `PMID:32896271/PMC7478891#p18` — *Direct reprogramming of human smooth muscle and vascular endothelial cells revea* — section **Induced vascular cells show gene-expression and functional differences between young vs. old donors**
  - Figure 2—figure supplement 3.Representative images of GSTM1 expression by endothelial cells within human skin biopsies from young vs.old donors (N = 2 donors per condition, 10 tissue sections per condition; Student’s t-test with p…
- `PMID:32896271/PMC7478891#p30` — *Direct reprogramming of human smooth muscle and vascular endothelial cells revea* — section **Induced vascular cells show gene-expression and functional differences between young vs. old donors**
  - In parallel, DE analysis performed on iVECs highlighted the upregulation of GSTM1 and PALD1 in cells derived from old vs. young donors. GSTM1 is generally activated in presence of oxidative stress and inflammatory conditions (Lope…
- `PMID:41823204#p0` — *Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute* — section **Abstract**
  - This study investigated the association between genetic variants and the occurrence of oral mucositis (OM) in pediatric patients with acute lymphoblastic leukemia (ALL) and lymphoma undergoing chemotherapy (CT). A retrospective ob…
- `PMID:42528395#p0` — *Integrated Cantilever-MEA Platform for High-Sensitivity and Scalable Recording o* — section **Abstract**
  - Preclinical screening is critical for reducing drug attrition; however, current electromechanical platforms are often restricted by the trade-off between miniaturization and force sensitivity. Miniaturizing sensor dimensions to en…

</details>

### Phase 11 — most precise + ledger

*6 gene–drug pairs, 5 disputed*

Adriamycin-induced cardiac strain and heart muscle damage are well-documented side effects with high confidence levels. The GSTM1 genetic variant is suggested as a potential risk factor, though the evidence is mixed (confidence 0.34). Studies indicate that cadmium exposure increases GST activity in breast cancer cells, which may be relevant to Adriamycin-induced oxidative stress and cardiotoxicity. However, direct evidence linking GSTM1 specifically to cardiac damage from Adriamycin is limited. Further genetic testing of your daughter could clarify her risk profile, potentially guiding personalized treatment strategies or dose adjustments.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **GSTP1** (rs1695) | 0.56 | moderate | curator_ambiguous | `ClinPGx:GSTP1/rs1695:L3` (curated) | — |
| **SLC28A3** (rs7853758) | 0.54 | moderate | curator_ambiguous | `ClinPGx:SLC28A3/rs7853758:L2B` (curated) | `PMID:42246857#p0` (human_cohort) |
| **RARG** (rs2229774) | 0.39 | low | curator_ambiguous | `ClinPGx:RARG/rs2229774:L3` (curated) | `PMID:42246857#p0` (human_cohort) |
| **GSTM1** | 0.34 | low | curator_ambiguous, literature_internal | `PMID:42515685/PMC13416366#p46` (in_vitro)<br>`PMID:41823204#p0` (human_cohort) | `PMID:42515685/PMC13416366#p46` (in_vitro)<br>`PMID:42643688#p0` (animal) |
| **GST-PI** | 0.26 | low | unsupported_claim | `PMID:42515685/PMC13416366#p46` (in_vitro) | — |
| **UGT1A6** | 0.23 | very_low | curator_ambiguous | — | `PMID:42246857#p0` (human_cohort) |

<details><summary>Paragraphs the system read and kept (5 from 5 papers)</summary>

- `PMID:42639770#p0` — *Therapeutic effect of Fuzheng Yixin decoction on cardiac insufficiencythe solubl* — section **Abstract**
  - To investigate the effect of Fuzheng Yixin decoction (, FZYX) and explore its underlying mechanisms in doxorubicin-induced dilated cardiomyopathy (DCM) rat model. Sprague-Dawley rats were intraperitoneally injected with doxorubici…
- `PMID:42515685/PMC13416366#p46` — *Differential Effects of 17β-Estradiol, Its Metabolites, and Cadmium on Cytotoxic* — section **2.8.1. Effect of Single Compounds on GST Activity**
  - Exposure of MCF-7 and MCF-7/DOX cells to Cd, estradiol, and its metabolites resulted in a concentration-dependent increase in GST activity compared with the respective controls. Basal GST activity was higher in MCF-7/DOX cells tha…
- `PMID:42643688#p0` — *Borneol-based nanoparticles encapsulating Doxorubicin/Sodium tanshinone IIA sulf* — section **Abstract**
  - Clinical treatment of brain glioma remains challenging due to chemotherapeutic resistance, cardiotoxicity and the presence of blood-brain barrier (BBB). Advanced nanoplatforms that can cross the BBB efficiently and target brain gl…
- `PMID:41823204#p0` — *Genetic Variants Associated With Oral Mucositis in Pediatric Patients With Acute* — section **Abstract**
  - This study investigated the association between genetic variants and the occurrence of oral mucositis (OM) in pediatric patients with acute lymphoblastic leukemia (ALL) and lymphoma undergoing chemotherapy (CT). A retrospective ob…
- `PMID:42246857#p0` — *Doxorubicin-induced early-onset chronic progressive cardiotoxicity, pharmacogene* — section **Abstract**
  - Early-onset chronic progressive cardiotoxicity (ECPC) is a significant cause of morbidity and mortality among patients who receive doxorubicin-based chemotherapy for breast cancer. To establish incidence of ECPC in black Zimbabwea…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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

### Phase 4 — ClinPGx + its cited literature

*Genes named: ERCC1 (rs11615), CYBA (rs4673)*

Doxorubicin-induced mucositis is associated with genetic variants ERCC1 (rs11615) and CYBA (rs4673), which modulate the drug's response, potentially increasing susceptibility to this adverse effect. The biological mechanism likely involves impaired DNA repair or oxidative stress responses due to these genetic variations, leading to heightened toxicity from doxorubicin. For drug discovery and patient safety, pre-treatment screening for these variants could inform personalized dosing strategies or identify patients at higher risk who might benefit from mucositis prophylaxis or alternative therapies.

### Phase 9L — widest net + ledger

*5 gene–drug pairs, 0 disputed*

Doxorubicin can cause mucositis as a side effect, with genetic polymorphisms such as ERCC1 (rs11615) and CYBA (rs4673) increasing the risk of developing this adverse reaction. The biological mechanism likely involves DNA damage response pathways modulated by these genes, where individuals carrying specific variants may have impaired repair mechanisms leading to increased mucositis susceptibility when exposed to doxorubicin. For drug development, understanding these genetic predispositions is crucial for patient stratification and personalized dosing strategies. Clinically, screening patients for ERCC1 (rs11615) and CYBA (rs4673) variants could help predict mucositis risk, enabling dose adjustments or alternative treatment options to mitigate adverse effects.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **CYBA** (rs4673) | 0.62 | moderate | — | `ClinPGx:CYBA/rs4673:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.62 | moderate | — | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |
| **BAX** | 0.26 | low | unsupported_claim | `PMID:42653080#p0` (in_vitro) | — |
| **INKA2** | 0.26 | low | unsupported_claim | `PMID:42653080#p0` (in_vitro) | — |
| **ZMAT3** | 0.26 | low | unsupported_claim | `PMID:42653080#p0` (in_vitro) | — |

<details><summary>Paragraphs the system read and kept (2 from 2 papers)</summary>

- `PMID:42653080#p0` — *Colonoid-Based Transcriptomics Reveals Conserved and Model-Specific Mechanisms o* — section **Abstract**
  - Animal models are standard for safety evaluation, yet physiological differences limit human translation. Doxorubicin, a chemotherapeutic agent, can cause off-target gastrointestinal toxicity and treatment discontinuation. This stu…
- `PMID:42623591#p0` — *Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Inv* — section **Abstract**
  - Muscle-invasive bladder carcinoma (MIBC) poses major treatment challenges in low- and middle-income countries because of logistical and socioeconomic barriers limiting neoadjuvant chemotherapy (NAC) delivery. While dose-dense meth…

</details>

### Phase 11 — most precise + ledger

*2 gene–drug pairs, 0 disputed*

Doxorubicin is known to cause mucositis as a side effect. Genetic variants such as ERCC1 (rs11615) and CYBA (rs4673) are associated with an increased risk of doxorubicin-related adverse effects, including mucositis. The PharmGKB evidence level 3 for ERCC1 (rs11615) indicates that individuals carrying this genetic variant may have a predisposition to developing mucositis when treated with doxorubicin. This suggests that there is a genetic component influencing the risk of mucositis in patients receiving doxorubicin therapy. For drug discovery and patient safety, screening for these genetic variants could help identify high-risk patients who might benefit from dose adjustment or alternative agents.

| Gene | Conf | Label | Disputed | Supporting | Refuting |
|---|---|---|---|---|---|
| **CYBA** (rs4673) | 0.62 | moderate | — | `ClinPGx:CYBA/rs4673:L3` (curated) | — |
| **ERCC1** (rs11615) | 0.62 | moderate | — | `ClinPGx:ERCC1/rs11615:L3` (curated) | — |

<details><summary>Paragraphs the system read and kept (1 from 1 papers)</summary>

- `PMID:42623591#p0` — *Accelerated Methotrexate, Vinblastine, Doxorubicin, and Cisplatin for Muscle-Inv* — section **Abstract**
  - Muscle-invasive bladder carcinoma (MIBC) poses major treatment challenges in low- and middle-income countries because of logistical and socioeconomic barriers limiting neoadjuvant chemotherapy (NAC) delivery. While dose-dense meth…

</details>

### Phase 12 — as phase 11, with expanded open-access full text

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

### Phase 13 — contradiction resolution

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
