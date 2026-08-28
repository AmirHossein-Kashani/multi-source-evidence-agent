# Phase 11 — method note

A standalone description of the phase-11 configuration of AMG-RAG: what it does, how each
stage works, what it outputs, how it was evaluated, and where it fails.

---

## 1. What the method is for

Given a pharmacogenomic question — *"which genetic variants make a child susceptible to
cisplatin-induced ototoxicity?"* — the method produces **a weighted, cited list of candidate
gene–drug associations**, not a prose opinion.

Three properties define it:

1. **Recall is the objective.** Every candidate gene found is reported, including weak ones.
   Nothing is dropped for being uncurated or poorly supported; it is reported *as* poorly
   supported.
2. **Disagreement is preserved, not averaged.** When the curated knowledge base and the
   literature conflict, or two papers conflict, the pair is flagged and both sides are kept.
3. **Confidence is computed by rule, never by the language model.** The model extracts and
   classifies; a formula over the resulting structure produces the number, so any score is
   traceable to the claims that produced it.

**Configuration**

```bash
AMG_KB_SOURCE=pharmgkb+pubmed_free    # curated tables + model-authored literature search
AMG_PUBMED_FULLTEXT=1                 # read open-access full text, not just abstracts
AMG_PAPER_DIGEST=1                    # per-paper paragraph reading
AMG_EVIDENCE_LEDGER=1                 # per-gene confidence + contradiction detection
AMG_ANSWER_STYLE=adr
```

Model: `qwen2.5:14b`, served locally by Ollama on one H100 MIG 2g.20gb slice, with
`OLLAMA_CONTEXT_LENGTH=16384`.

---

## 2. Knowledge sources

**Curated — ClinPGx / PharmGKB bulk download** (`pgx_kb.py`), loaded offline:

| Table | Rows | What it gives |
|---|---|---|
| `clinicalVariants.tsv` | 5,190 | gene, variant, drug, phenotype, **evidence level 1A–4** |
| `relationships.tsv` | 127,988 pairs | gene × drug **association status** and the PMIDs cited for it |

The association column is the method's ground signal for disagreement: **74,646 `associated`,
33,100 `not associated`, 20,032 `ambiguous`** — the last meaning the curators themselves found
conflicting reports.

**Literature — PubMed / PMC** via NCBI E-utilities, rate-limited to ~3 requests/second, cached
per PMID and per query.

---

## 3. Pipeline

```
question
  │
  ├─ 1. entity + KG construction    entities, relations, curated ClinPGx edges
  │
  ├─ 2. query authoring (LLM)       the model writes PubMed queries; any number of concepts
  │
  ├─ 3. retrieval                   ClinPGx rows + PubMed records (abstract or full text)
  │
  ├─ 4. per-paper reading (LLM)     paragraphs that answer the question, with citable ids
  │
  ├─ 5. evidence ledger (rule)      claims → confidence + contradiction flags per gene–drug pair
  │
  └─ 6. answer                      prose conditioned on the ledger
```

### Stage 1 — knowledge graph

Entities are extracted from the question by the model and scored for relevance. In parallel,
ClinPGx rows matching the question are seeded into the graph as confidence-weighted edges
(`drug → gene → variant`), where edge confidence comes from the PharmGKB evidence level.
Relations between extracted entities are inferred pairwise by the model. The graph supplies two
things downstream: entity names to enrich, and **edges** showing which concepts are related.

### Stage 2 — query authoring

A dedicated chain writes the PubMed queries. It receives the question, the knowledge-graph
edges (`entity -[relation]-> entity`) and the evidence retrieved so far, and returns queries
with the concepts each covers.

The model decides **both** how many concepts to combine and the exact wording. Quoted phrases,
`OR` groups and PubMed field tags pass through verbatim; the code only strips control characters,
caps length at 300, and closes the space before a field tag. Observed behaviour over 392 queries
on ten questions:

| Concepts per query | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| queries | 31 | 246 | 103 | 11 | 1 |

Examples the model produced: `"cisplatin ototoxicity"[tiab]`, `ACYP2`,
`(GSTM1 OR TPMT) AND cisplatin AND hearing loss`.

A query returning nothing is **relaxed** rather than discarded: field tags are dropped first,
then the last `AND` term. This takes empty queries to zero (39 of 392 were recovered this way).
Results from different queries are interleaved round-robin so each contributes.

### Stage 3 — retrieval

ClinPGx is searched first; its rows carry gene, variant, evidence level and the PMIDs the
curators cite. PubMed records are fetched as XML and parsed into PMID, title, abstract, journal
and year, so every item carries a citable identifier.

Where an open-access copy exists, full text is retrieved: `elink` maps PMID → PMCID, then the
PMC JATS XML `<body>` is parsed **into a list of paragraphs**, each tagged with the title of its
enclosing `<sec>`. An open-access PDF (via `pypdf`) is the fallback. Full text is not truncated
at this point — the whole paragraph list is kept.

### Stage 4 — per-paper reading

Each candidate paper is read rather than pasted into a prompt. Its paragraphs are grouped into
batches of ≤ 2,400 characters, and the batches are **ranked before reading**, because a long
article cannot be sent to the model whole. The ranking rewards findings and penalises
background:

| Signal | Weight |
|---|---|
| variant identifiers (`rs\d{3,}`) | ×3 |
| effect statistics (`95% CI`, `odds ratio`, `p = 0.0x`, `hazard ratio`) | ×3 |
| gene symbols | ×2 |
| association language (`associated`, `genotype`, `carriers`, `allele`, `susceptibility`) | ×1.5 |
| question terms | ×1 |
| section is Results / Discussion / Conclusion | **+8** |
| section is Abstract | +4 |
| section is Introduction / Background | **−6** |
| section is Methods / Materials | −4 |
| background phrasing (*"remains incompletely understood"*, *"is widely used"*) | −5 |

The top 6 batches are read. For each, the model returns:

- the **paragraph numbers** that bear on the question
- a 2–3 sentence statement of what they establish
- the **study type** (meta-analysis, systematic review, GWAS, human cohort, clinical trial,
  case report, animal, in vitro, review)
- the genes the text **supports** and the genes it **refutes**

Every kept paragraph is addressable as `PMID:42633148/PMC13499120#p34`.

Coverage is capped and the cap is logged, never silent: a 35-batch article reports
`reading the 6 most finding-dense of 35 batches`.

### Stage 5 — the evidence ledger

Claims are collected from two places and aggregated per **(gene, drug)** pair:

- **curated claims** — one per ClinPGx row, `study_type="curated"`, stance taken from the
  association column (`not associated` becomes a refuting claim)
- **literature claims** — one per gene per digested paper, stance from the digest's
  supports/refutes lists, carrying the paragraph reference

**Confidence**

```
base    = LEVEL_CONF[evidence level]        1A .98  1B .90  2A .80  2B .70  3 .55  4 .40
        = 0.25   if the pair is absent from the curated tables
        = 0.15   if the curators record it as NOT associated
        = 0.55   if associated but with no clinical-variant level

support = Σ study-type weight over DISTINCT sources
          curated/meta-analysis 1.0 · systematic review .95 · GWAS .9 · human cohort .85
          · clinical trial .85 · case report .45 · review .4 · animal .3 · in vitro .2

confidence = clamp( base · (1 + 0.18·log1p(support)) − 0.30·log1p(refute) , 0, 1 )
             × 0.9 when the curators mark the pair ambiguous

labels: high ≥ 0.75 · moderate ≥ 0.50 · low ≥ 0.25 · very_low below
```

Two properties are deliberate. Sources are de-duplicated by identity, so five paragraphs of one
paper count once, not five times. And support is log-damped, so the tenth confirming study adds
less than the second.

**Contradiction flags**

| Flag | Fires when |
|---|---|
| `curator_ambiguous` | the curators recorded conflicting evidence for the pair |
| `curated_vs_literature` | the tables say *not associated* but papers support it, or the reverse |
| `literature_internal` | retrieved papers support and refute the same pair |
| `uncurated_literature_claim` | absent from the tables but backed by a human study — a candidate novel association |
| `unsupported_claim` | absent from the tables with nothing stronger than a review or an animal study behind it |

A pair is `disputed` when any flag other than `unsupported_claim` fires.

### Stage 6 — the answer

The ledger is rendered into the answer prompt, which is instructed to report **every** gene with
its confidence label, to state explicitly what disagrees with what where a pair is disputed, and
never to assert a link the ledger marks unsupported.

---

## 4. Output

Per question, alongside the prose answer:

```jsonc
"gene_ledger": [{
  "gene": "TPMT", "drug": "cisplatin",
  "variants": ["TPMT*1"], "phenotypes": ["Ototoxicity"],
  "confidence": 0.501, "label": "moderate", "disputed": true,
  "contradictions": [
    {"type": "curator_ambiguous", "detail": "ClinPGx curators record conflicting evidence…"},
    {"type": "literature_internal", "detail": "retrieved papers disagree with each other",
     "refs": ["PMID:40222694#p0", "PMID:41637682#p0"]}],
  "supporting": [
    {"ref": "ClinPGx:TPMT/TPMT*1:L3", "study_type": "curated", "text": "…level 3 linking it to…"},
    {"ref": "PMID:40222694#p0", "study_type": "systematic_review", "text": "…identifies several genes…"}],
  "refuting": [
    {"ref": "PMID:41637682#p0", "study_type": "review",
     "text": "…a 2009 Nature Genetics article which incorrectly linked TPMT to cisplatin ototoxicity…"}],
  "components": {"base": 0.55, "support_weight": 1.95, "support_sources": 2,
                 "refute_weight": 0.4, "refute_sources": 1,
                 "clinpgx_level": "3", "clinpgx_association": "ambiguous"}
}]
```

Also persisted: `paper_digests` (what was read, which paragraphs were kept, from which section),
`references` and `evidence_log` (full retrieval provenance), and `search_shape` (every query
issued, its arity and hit count).

---

## 5. Results

**Ten ADR clinical questions** (45–47 minutes on one GPU slice):

- **96 gene–drug pairs**, mean 9.6 per question
- **61** carry a contradiction flag
- confidence labels: moderate 43, low 36, very_low 17
- 29 papers read, 41 paragraphs cited, 4 read as full text
- retrieval precision: **65%** of retrieved papers mention both the drug and the adverse effect

**Confidence calibration**, on 72 gene–drug pairs labelled from the curated association column
(`associated` → positive, `not associated` → negative, `ambiguous` → disputed):

| Label | n | mean confidence | assigned labels |
|---|---|---|---|
| positive | 15 | **0.424** | low 8, moderate 5, very_low 2 |
| disputed | 21 | 0.351 | low 13, moderate 4, very_low 4 |
| negative | 16 | **0.073** | very_low 16 |

- separation (positive − negative): **+0.351**
- Spearman(confidence, label order): **0.721**
- **every one of the 16 negatives** was placed in `very_low` — the method reliably declines to
  endorse pairs the curators record as not associated

**Contradiction detection**: recall **0.95** (20 of 21 disputed pairs), precision **0.47**,
F1 **0.62**.

---

## 6. Limitations

- **The prose does not cite.** Only 1 of 10 answers contains a reference, although the ledger
  carries paragraph-level identifiers. **The ledger is the deliverable; the prose is not.** On
  one question the answer promoted a gene that its own ledger entry scored 0.26 `low`
  `unsupported_claim`.
- **Confidence is compressed.** Positives average 0.424 and nothing reaches `high`. The
  ambiguity damping and log-damped support term are likely too conservative.
- **Contradiction precision is 0.47** — the method over-flags. Much of that is genuine
  literature-versus-curation disagreement rather than error, but it cannot yet be used
  unfiltered.
- **Target-pair recall is 65–84%** on the labelled set: a third of positive pairs were never
  surfaced, so the calibration figures describe the pairs that were found.
- **Reading is partial.** Six batches per paper is roughly 29% of a long article — now the most
  finding-dense 29%, but partial.
- **Section-based ranking degrades** on papers whose section titles are full sentences rather
  than "Results"; the finding-signal terms carry those cases.
- **A glossary can look like a finding.** Gene-symbol density scores an *Abbreviations* section
  highly; one digest cited such a paragraph.
- **Gene symbols are not canonicalised**, so hyphenated variants can appear as separate ledger
  entries.
- **The calibration labels come from the same curated source the method retrieves from**, so
  the measurement is partly self-consistent. It remains informative for the negative and
  disputed classes, where the method must disagree with what its own retrieval returns.
- **Validated on 10 questions and 72 labelled pairs** — descriptive, not statistically powered.

---

## 7. Running it

```bash
sbatch run_adr_phase11_alliance.bash          # ten ADR questions

python make_pgx_benchmark.py --per-class 50   # build the labelled pair set
sbatch --time=05:00:00 --export=ALL,ADR_INPUT=.../pgx_confidence_bench.jsonl,ADR_TAG=bench,\
       AMG_DIGEST_MAX_PAPERS=3,AMG_DIGEST_MAX_BATCHES=3 run_adr_phase11_alliance.bash

python eval_ledger.py                         # recall, calibration, contradiction P/R
```

**Tuning knobs**

| Variable | Default | Effect |
|---|---|---|
| `AMG_COMBO_MAX_QUERIES` | 4 | queries authored per stage |
| `AMG_OPEN_PER_PHRASE` | 2 | papers taken per query |
| `AMG_DIGEST_MAX_PAPERS` | 6 | papers read per question |
| `AMG_DIGEST_BATCH_CHARS` | 2400 | paragraph batch size sent to the model |
| `AMG_DIGEST_MAX_BATCHES` | 6 | batches read per paper — raise for fuller coverage |
| `AMG_FULLTEXT_MAX_CHARS` | 3000 | cap on non-digest full-text use |

**Key files**: `AMG-with-KG.py` (pipeline), `pgx_kb.py` (curated tables),
`evidence_ledger.py` (confidence and contradictions), `run_genmedgpt.py` (batch runner,
resume-safe), `make_pgx_benchmark.py`, `eval_ledger.py`.
