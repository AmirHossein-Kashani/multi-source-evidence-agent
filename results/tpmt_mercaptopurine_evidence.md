# Evidence report: TPMT genotype and mercaptopurine response

**Question:** Will my TPMT genotype change how I respond to mercaptopurine?

Retrieval-only trace (no LLM answer): what each phase retrieves and how it is referenced.

## Phase 3 — ClinPGx local tables (`AMG_KB_SOURCE=pharmgkb`)

| Ref | Gene | Variant | Level | Drug | Evidence string | Cited PMIDs |
|---|---|---|---|---|---|---|
| `ClinPGx:NUDT15/rs116855232:L1A` | NUDT15 | rs116855232 | 1A | mercaptopurine | NUDT15 (rs116855232): PharmGKB evidence level 1A linking it to mercaptopurine-related Dosage. ClinPGx relationship: ambiguous. | 25108385, 25624441, 26033531, 26076924, 26405151, 26503813 |
| `ClinPGx:TPMT/TPMT*1:L1A` | TPMT | TPMT*1 | 1A | mercaptopurine | TPMT (TPMT*1): PharmGKB evidence level 1A linking it to mercaptopurine-related Metabolism/PK. ClinPGx relationship: ambiguous. | 10354134, 10376773, 10580024, 10734022, 11337943, 11372592 |
| `ClinPGx:TPMT/TPMT*1:L1A` | TPMT | TPMT*1 | 1A | mercaptopurine | TPMT (TPMT*1): PharmGKB evidence level 1A linking it to mercaptopurine-related Dose reduction. ClinPGx relationship: ambiguous. | 10354134, 10376773, 10580024, 10734022, 11337943, 11372592 |

## Phase 4 — PubMed check of the ClinPGx citations (`AMG_KB_SOURCE=pharmgkb+pubmed`)

The PMIDs cited by `relationships.tsv` for the retrieved gene–drug pairs are fetched from PubMed (`via: clinpgx_citation`); a live esearch tops up to the result cap.

### PMID:25108385  (clinpgx_citation)

**A common missense variant in NUDT15 confers susceptibility to thiopurine-induced leukopenia.**  
*Nature genetics* (2014)

Thiopurine therapy, commonly used in autoimmune conditions, can be complicated by life-threatening leukopenia. This leukopenia is associated with genetic variation in TPMT (encoding thiopurine S-methyltransferase). Despite a lower frequency of TPMT mutations in Asians, the incidence of thiopurine-induced leukopenia is higher in Asians than in individuals of European descent. Here we performed an Immunochip-based 2-stage association study in 978 Korean subjects with Crohn's disease treated with thiopurines. We identified a nonsynonymous SNP in NUDT15 (encoding p.Arg139Cys) that was strongly associated with thiopurine-induced early leukopenia (odds ratio (OR) = 35.6; P(combined) = 4.88 × 10(-94)). In Koreans, this variant demonstrated sensitivity and specificity of 89.4% and 93.2%, respectively, for thiopurine-induced early leukopenia (in comparison to 12.1% and 97.6% for TPMT variants). Although rare, this SNP was also strongly associated with thiopurine-induced leukopenia in subjects with inflammatory bowel disease of European descent (OR = 9.50; P = 4.64 × 10(-4)). Thus, NUDT15 is a pharmacogenetic determinant for thiopurine-induced leukopenia in diverse populations.

### PMID:25624441  (clinpgx_citation)

**Inherited NUDT15 variant is a genetic determinant of mercaptopurine intolerance in children with acute lymphoblastic leukemia.**  
*Journal of clinical oncology : official journal of the American Society of Clinical Oncology* (2015)

Mercaptopurine (MP) is the mainstay of curative therapy for acute lymphoblastic leukemia (ALL). We performed a genome-wide association study (GWAS) to identify comprehensively the genetic basis of MP intolerance in children with ALL. The discovery GWAS and replication cohorts included 657 and 371 children from two prospective clinical trials. MP dose intensity was a marker for drug tolerance and toxicities and was defined as prescribed dose divided by the planned protocol dose during maintenance therapy; its association with genotype was evaluated using a linear mixed-effects model. MP dose intensity varied by race and ethnicity and was negatively correlated with East Asian genetic ancestry (P < .001). The GWAS revealed two genome-wide significant loci associated with dose intensity: rs1142345 in TPMT (Tyr240Cys, present in *3A and *3C variants; P = 8.6 × 10(-9)) and rs116855232 in NUDT15 (P = 8.8 × 10(-9)), with independent replication. Patients with TT genotype at rs116855232 were exquisitely sensitive to MP, with an average dose intensity of 8.3%, compared with those with TC and CC genotypes, who tolerated 63% and 83.5% of the planned dose, respectively. The NUDT15 variant was most common in East Asians and Hispanics, rare in Europeans, and not observed in Africans, contributing to ancestry-related differences in MP tolerance. Of children homozygous for either TPMT or NUDT15 variants or heterozygous for both, 100% required ≥ 50% MP dose reduction, compared with only 7.7% of others. We describe a germline variant in NUDT15 strongly associated with MP intolerance in childhood ALL, which may have implications for treatment individualization in this disease.

### PMID:26033531  (clinpgx_citation)

**Susceptibility to 6-MP toxicity conferred by a NUDT15 variant in Japanese children with acute lymphoblastic leukaemia.**  
*British journal of haematology* (2015)

Genotyping of TPMT prior to 6-mercaptopurine (6-MP) administration in acute lymphoblastic leukaemia (ALL) patients has been integrated into clinical practice in some populations of European ancestry. However, the comparable rates of 6-MP myelotoxicity, but rarity of TPMT variants, in Asians suggest that major determinants have yet to be discovered in this population. We genotyped 92 Japanese paediatric ALL patients for NUDT15 rs116855232, a 6-MP toxicity-related locus discovered in Asians. Logistic regression and survival analysis were used to evaluate its association with leucopenia, hepatotoxicity, 6-MP dose reduction, therapy interruption and event-free survival. The allele frequency of rs116855232 was 0·16, and leucopenia was more common in carriers of the T allele (odds ratio, 7·20; 95% confidence interval, 2·49-20·80; P = 2·7 × 10(-4) ). As leucopenia results in 6-MP dose reduction, we observed average doses during maintenance therapy of 40·7, 29·3 and 8·8 mg/m(2) for patients with CC, CT and TT genotypes, respectively (P < 0·001). Hepatotoxicity was observed only in CC genotype patients. Event-free survival did not significantly differ by NUDT15 genotype. rs116855232 is an important determinant of 6-MP myelotoxicity in Japanese children with ALL and may represent the most robust toxicity-related locus in Asians to date. Considerations for clinical application may be warranted.

## Phase 5 — full-text upgrade (`AMG_PUBMED_FULLTEXT=1`)

### PMID:25108385/PMC4999337 — full text via `pmc_xml`

**A common missense variant in NUDT15 confers susceptibility to thiopurine-induced leukopenia.**

Article body retrieved: **20,406 characters** from PMC4999337; first 3,000 enter the prompt. Excerpt:

> Azathioprine (AZA) and its close analog 6-mercaptopurine (6-MP) are thiopurines widely used in the treatment of patients with cancers, organ transplantation, and autoimmune or inflammatory diseases, including inflammatory bowel diseases (IBD)1,2. However, thiopurine-associated leukopenia is a substantial hazard that occurs in up to 5% of individuals with IBD of European descent3–5. The association between thiopurine-induced leukopenia and TPMT mutations is well established, and TPMT testing before thiopurine exposure is recommended by the US Food and Drug Administration (FDA). However, only about a quarter of individuals with IBD who have thiopurine-associated leukopenia carry a TPMT mutation, suggesting the existence of additional factors and also questioning the usefulness of pretesting for TPMT status in this situation6–8. Interestingly, although the frequency of TPMT mutations is lower in Asians than in individuals of European descent (~3% versus ~10%)9–13, the frequency at which thiopurine-induced leukopenia occurs in Asians is considerably higher11,12,14. Thiopurine-associated leukopenia (defined by a white blood cell (WBC) count of <3,000 cells/mm3) was observed in 31.2% and

- PMID:25624441: no open-access full text in PMC (abstract only).
- PMID:26033531: no open-access full text in PMC (abstract only).

## Consolidated references (as persisted in `references`)

| Ref | Source | Title |
|---|---|---|
| `ClinPGx:NUDT15/rs116855232:L1A` | ClinPGx | — |
| `ClinPGx:TPMT/TPMT*1:L1A` | ClinPGx | — |
| `PMID:25108385/PMC4999337` | PubMed | A common missense variant in NUDT15 confers susceptibility to thiopurine-induced leukopenia. |
| `PMID:25624441` | PubMed | Inherited NUDT15 variant is a genetic determinant of mercaptopurine intolerance in children with acute lymphoblastic leukemia. |
| `PMID:26033531` | PubMed | Susceptibility to 6-MP toxicity conferred by a NUDT15 variant in Japanese children with acute lymphoblastic leukaemia. |

---
*Generated by AMG-RAG retrieval seams (`_evidence_search_detailed`), 2026-08-14. In a real run these fields appear per item as `references` / `evidence_log` in the results JSONL.*
