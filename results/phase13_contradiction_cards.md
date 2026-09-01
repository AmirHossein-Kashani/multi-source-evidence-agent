# Phase 13 — contradiction resolution cards

Each gene–drug pair is resolved to a status with the **reason** the sources disagree. Evidence is tiered (curated / clinical / mechanistic / narrative) and only comparable tiers may conflict, so an in-vitro null result no longer counts as contradicting a clinical association. Classification is computed in `contradiction_layer.py`; the model extracts the fields, the module decides.

| Status | Meaning | n |
|---|---|---|
| **CURATED-LITERATURE CONFLICT** | the curated database and the retrieved literature disagree | 0 |
| **CONFLICTING** | comparable credible evidence supports both directions | 22 |
| **CONTEXT-DEPENDENT** | the conflict disappears once population / dose / type is fixed | 3 |
| **CONSISTENT** | comparable credible evidence agrees | 0 |
| **INSUFFICIENT** | too little comparable clinical evidence to judge | 120 |
| | **total** | **145** |

**Why sources disagreed:** `curator_ambiguous` 11, `unexplained` 11, `endpoint` 1, `population` 1, `cancer_type` 1

---

## Q1. I am a child receiving cisplatin for cancer and developed hearing loss and tinnitus. What genetic variants make me susceptible to this ototoxicity?

*18 pairs — INSUFFICIENT 17, CONFLICTING 1*

### COMT (rs4646316) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:COMT/rs4646316:L3` (curated); `ClinPGx:COMT/rs9332377:L3` (curated)
- **Evidence tiers:** curated (2+/0−)

> The COMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on COMT alone.

<sub>17 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q2. What genes or variants have been linked to cisplatin ototoxicity risk in pediatric cancer patients?

*14 pairs — INSUFFICIENT 9, CONFLICTING 5*

### COMT (rs4646316) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.64 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:COMT/rs4646316:L3` (curated); `ClinPGx:COMT/rs9332377:L3` (curated); `PMID:40222694/#p0` (systematic_review)
- **Populations:** children, mixed
- **Cancer types:** solid tumors
- **Endpoints:** ototoxicity
- **Evidence tiers:** curated (2+/0−), clinical (2+/0−)

> The COMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on COMT alone.

### TPMT (TPMT*1) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.60 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:TPMT/TPMT*1:L3` (curated); `PMID:40222694/#p0` (systematic_review); `PMID:41637682#p0` (review)
- **Populations:** children
- **Cancer types:** solid tumors
- **Endpoints:** ototoxicity
- **Evidence tiers:** curated (1+/0−), clinical (1+/0−), narrative (1+/0−)

> The TPMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on TPMT alone.

### ABCC3 (rs1051640) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:ABCC3/rs1051640:L3` (curated); `PMID:40222694/#p0` (systematic_review)
- **Populations:** children
- **Cancer types:** solid tumors
- **Endpoints:** ototoxicity
- **Evidence tiers:** curated (1+/0−), clinical (1+/0−)

> The ABCC3-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ABCC3 alone.

### SLC22A2 (rs316019) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:SLC22A2/rs316019:L3` (curated); `PMID:40222694/#p0` (systematic_review)
- **Populations:** children
- **Cancer types:** solid tumors
- **Endpoints:** ototoxicity
- **Evidence tiers:** curated (1+/0−), clinical (1+/0−)

> The SLC22A2-cisplatin association remains disputed; evidence is insufficient to base clinical screening on SLC22A2 alone.

### ERCC2 — cisplatin

**Status: CONFLICTING**  ·  confidence 0.47 [low]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `PMID:40222694/#p0` (systematic_review); `PMID:36802061#p0` (meta_analysis)
- **Populations:** children, mixed
- **Cancer types:** solid tumors
- **Endpoints:** ototoxicity
- **Evidence tiers:** clinical (2+/0−)

> The ERCC2-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ERCC2 alone.

<sub>9 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q3. My daughter carries a TPMT variant and is on cisplatin for her Neuroblastoma. Her audiologist says she's high risk for hearing loss — is there a genetic reason, and does her cancer type change the picture?

*11 pairs — INSUFFICIENT 9, CONFLICTING 1, CONTEXT-DEPENDENT 1*

### COMT (rs4646316) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:COMT/rs4646316:L3` (curated); `ClinPGx:COMT/rs9332377:L3` (curated)
- **Evidence tiers:** curated (2+/0−)

> The COMT-cisplatin association remains disputed; evidence is insufficient to base clinical screening on COMT alone.

### TPMT (TPMT*1) — cisplatin

**Status: CONTEXT-DEPENDENT**  ·  confidence 0.41 [low]

- **Why:** endpoint differs (e.g. threshold shift vs clinically significant loss) — supporting: cisplatin-induced ototoxicity, hearing loss, ototoxicity; refuting: clinically significant hearing loss
- **Supporting:** `ClinPGx:TPMT/TPMT*1:L3` (curated); `PMID:40222694/#p0` (systematic_review); `PMID:37726872#p0` (systematic_review)
- **Refuting:** `PMID:41637682#p0` (review); `PMID:42504125#p0` (human_cohort)
- **Populations:** children, mixed
- **Endpoints:** cisplatin-induced ototoxicity, clinically significant hearing loss, hearing loss
- **Evidence tiers:** curated (1+/0−), clinical (3+/1−), narrative (0+/1−)

> The apparent TPMT-cisplatin disagreement is explained by endpoint; the association may hold in one setting and not another.

<sub>9 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q4. After several cycles of Platinol, my child has permanent inner ear damage, and we're wondering if her GSTT1 status played a role, since her oncologist mentioned it during a different conversation about drug metabolism.

*10 pairs — INSUFFICIENT 6, CONFLICTING 4*

### CYP2E1 (rs2070676) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:CYP2E1/rs6413432:L3` (curated); `ClinPGx:CYP2E1/rs2070676:L3` (curated)
- **Evidence tiers:** curated (2+/0−)

> The CYP2E1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on CYP2E1 alone.

### ERCC1 (rs11615) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:ERCC1/rs11615:L3` (curated); `PMID:40342074/PMC12434574#p31` (human_cohort)
- **Populations:** adults
- **Cancer types:** head and neck squamous cell carcinoma
- **Endpoints:** renal function decline
- **Evidence tiers:** curated (1+/0−), clinical (1+/0−)

> The ERCC1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ERCC1 alone.

### GSTP1 (rs1695) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:GSTP1/rs1695:L3` (curated); `PMID:40342074/PMC12434574#p31` (human_cohort)
- **Populations:** adults
- **Cancer types:** head and neck squamous cell carcinoma
- **Endpoints:** renal function decline
- **Evidence tiers:** curated (1+/0−), clinical (1+/0−)

> The GSTP1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

### GSTT1 — cisplatin

**Status: CONFLICTING**  ·  confidence 0.19 [very_low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `PMID:40342074/PMC12434574#p31` (human_cohort); `PMID:40222694/#p0` (systematic_review)
- **Refuting:** `PMID:40342074/PMC12434574#p31` (human_cohort); `PMID:40222694/#p0` (systematic_review)
- **Populations:** adults, children
- **Cancer types:** head and neck squamous cell carcinoma, solid tumors
- **Endpoints:** ototoxicity, renal function decline
- **Evidence tiers:** clinical (2+/2−)

> The GSTT1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on GSTT1 alone.

<sub>6 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q5. Can cisplatin cause a genetic predisposition to peripheral neuropathy?

*19 pairs — INSUFFICIENT 16, CONFLICTING 3*

### CYP2E1 (rs2070676) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.59 [moderate]

- **Why:** the curators themselves record conflicting reports
- **Supporting:** `ClinPGx:CYP2E1/rs6413432:L3` (curated); `ClinPGx:CYP2E1/rs2070676:L3` (curated)
- **Evidence tiers:** curated (2+/0−)

> The CYP2E1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on CYP2E1 alone.

### ERCC1 (rs11615) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.42 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:ERCC1/rs11615:L3` (curated); `PMID:42123691/PMC13164360#p18` (human_cohort)
- **Refuting:** `PMID:42123691/PMC13164360#p18` (human_cohort)
- **Populations:** adults
- **Cancer types:** gastric and gastroesophageal junction adenocarcinoma
- **Endpoints:** pathological tumor regression grading (trg)
- **Evidence tiers:** curated (1+/0−), clinical (1+/1−)

> The ERCC1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on ERCC1 alone.

### GSTP1 (rs1695) — cisplatin

**Status: CONFLICTING**  ·  confidence 0.39 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:GSTP1/rs1695:L3` (curated)
- **Refuting:** `PMID:42123691/PMC13164360#p18` (human_cohort)
- **Populations:** adults
- **Cancer types:** gastric and gastroesophageal junction adenocarcinoma
- **Endpoints:** pathological tumor regression grading (trg)
- **Evidence tiers:** curated (1+/0−), clinical (0+/1−)

> The GSTP1-cisplatin association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

<sub>16 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q6. After receiving doxorubicin for pediatric lymphoma, my child developed severe shortness of breath and heart muscle damage. Is there a genetic cause for this?

*12 pairs — INSUFFICIENT 10, CONFLICTING 2*

### SLC28A3 (rs7853758) — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.54 [moderate]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:SLC28A3/rs7853758:L2B` (curated)
- **Refuting:** `PMID:42246857#p0` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** early-onset chronic progressive cardiotoxicity (ecpc)
- **Evidence tiers:** curated (1+/0−), clinical (0+/1−)

> The SLC28A3-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on SLC28A3 alone.

### RARG (rs2229774) — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.39 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:RARG/rs2229774:L3` (curated)
- **Refuting:** `PMID:42246857#p0` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** early-onset chronic progressive cardiotoxicity (ecpc)
- **Evidence tiers:** curated (1+/0−), clinical (0+/1−)

> The RARG-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on RARG alone.

<sub>10 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q7. Which pharmacogenomic biomarkers predict anthracycline-induced cardiotoxicity in childhood cancer survivors?

*25 pairs — INSUFFICIENT 23, CONFLICTING 1, CONTEXT-DEPENDENT 1*

### GSTP1 (rs1695) — anthracycline

**Status: CONFLICTING**  ·  confidence 0.39 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:GSTP1/rs1695:L3` (curated)
- **Refuting:** `PMID:42549829#p0` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** antracycline-induced cardiotoxicity
- **Evidence tiers:** curated (1+/0−), clinical (0+/1−)

> The GSTP1-anthracycline association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

### SLC28A3 (rs7853758) — anthracycline

**Status: CONTEXT-DEPENDENT**  ·  confidence 0.65 [moderate]

- **Why:** population differs (e.g. children vs adults) — supporting: children; refuting: adults
- **Supporting:** `ClinPGx:SLC28A3/rs7853758:L2B` (curated); `PMID:40413218/PMC12103300#p15` (systematic_review)
- **Refuting:** `PMID:42549829#p0` (human_cohort)
- **Populations:** adults, children
- **Cancer types:** breast cancer, mixed
- **Endpoints:** antracycline-induced cardiotoxicity, cardiotoxicity
- **Evidence tiers:** curated (1+/0−), clinical (1+/1−)

> The apparent SLC28A3-anthracycline disagreement is explained by population; the association may hold in one setting and not another.

<sub>23 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q8. My son carries CYP2D6*4 and was on doxorubicin for his Neoplasm — his cardiologist is concerned about early heart failure. Is this genetic, and does his specific cancer diagnosis matter here?

*13 pairs — INSUFFICIENT 10, CONFLICTING 3*

### SLC28A3 (rs7853758) — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.46 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:SLC28A3/rs7853758:L2B` (curated); `PMID:42176227#p0` (review)
- **Refuting:** `PMID:42549829#p0` (human_cohort); `PMID:42246857#p0` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** anthracycline-induced cardiotoxicity (act), early-onset chronic progressive cardiotoxicity (ecpc)
- **Evidence tiers:** curated (1+/0−), narrative (1+/0−), clinical (0+/2−)

> The SLC28A3-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on SLC28A3 alone.

### RARG (rs2229774) — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.41 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:RARG/rs2229774:L3` (curated); `PMID:42176227#p0` (review)
- **Refuting:** `PMID:42246857#p0` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** early-onset chronic progressive cardiotoxicity (ecpc)
- **Evidence tiers:** curated (1+/0−), narrative (1+/0−), clinical (0+/1−)

> The RARG-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on RARG alone.

### GSTP1 (rs1695) — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.39 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:GSTP1/rs1695:L3` (curated)
- **Refuting:** `PMID:42549829#p0` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** anthracycline-induced cardiotoxicity (act)
- **Evidence tiers:** curated (1+/0−), clinical (0+/1−)

> The GSTP1-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on GSTP1 alone.

<sub>10 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q9. My daughter took Adriamycin and now has cardiac strain and heart muscle damage — could her GSTM1 result from an earlier test be connected?

*11 pairs — INSUFFICIENT 10, CONTEXT-DEPENDENT 1*

### GSTM1 — doxorubicin

**Status: CONTEXT-DEPENDENT**  ·  confidence 0.18 [very_low]

- **Why:** cancer type differs — supporting: acute lymphoblastic leukemia and lymphoma; refuting: hematologic malignancies and solid tumors
- **Supporting:** `PMID:32896271/PMC7478891#p18` (in_vitro); `PMID:41823204#p0` (human_cohort)
- **Refuting:** `PMID:32896271/PMC7478891#p18` (in_vitro); `PMID:42670540/#p6` (review); `PMID:42670080#p0` (human_cohort)
- **Populations:** children
- **Cancer types:** acute lymphoblastic leukemia and lymphoma, hematologic malignancies and solid tumors
- **Endpoints:** cardiotoxicity, including acute cardiomyopathy and cardiac f, oral mucositis
- **Evidence tiers:** mechanistic (1+/2−), clinical (1+/1−), narrative (0+/1−)

> The apparent GSTM1-doxorubicin disagreement is explained by cancer_type; the association may hold in one setting and not another.

<sub>10 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

## Q10. Could doxorubicin cause a genetic predisposition to mucositis?

*12 pairs — INSUFFICIENT 10, CONFLICTING 2*

### CYBA (rs4673) — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.47 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `ClinPGx:CYBA/rs4673:L3` (curated); `PMID:40362292/PMC12072181#p18` (human_cohort)
- **Refuting:** `PMID:40362292/PMC12072181#p18` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** subclinical cardiotoxicity
- **Evidence tiers:** curated (1+/0−), clinical (1+/1−)

> The CYBA-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on CYBA alone.

### CBR3 — doxorubicin

**Status: CONFLICTING**  ·  confidence 0.27 [low]

- **Why:** comparable studies disagree with no contextual difference detected
- **Supporting:** `PMID:40362292/PMC12072181#p18` (human_cohort)
- **Refuting:** `PMID:40362292/PMC12072181#p18` (human_cohort)
- **Populations:** adults
- **Cancer types:** breast cancer
- **Endpoints:** subclinical cardiotoxicity
- **Evidence tiers:** clinical (1+/1−)

> The CBR3-doxorubicin association remains disputed; evidence is insufficient to base clinical screening on CBR3 alone.

<sub>10 further pairs resolved INSUFFICIENT (fewer than two comparable clinical sources).</sub>

---

