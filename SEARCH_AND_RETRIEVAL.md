# How search works in AMG-RAG (ClinPGx + PubMed + full text)

Everything the system retrieves — ClinPGx table rows, PubMed abstracts, PMC full text,
Wikipedia summaries — passes through **one function**:

```
AMG_RAG_System._evidence_search_detailed(query, max_results, stage)   # AMG-with-KG.py
```

That single seam is what makes phases 3/4/5 switchable by environment variable alone. This
document explains how a query becomes evidence: how words are found, how the tables are
matched and ranked, how PubMed is queried, how full text is pulled, and which knobs to turn
to make retrieval better.

---

## 1. The pipeline at a glance

```
question text
     │
     ├─► (A) find the words ──┬─► LLM entity extraction  (entity_extractor chain)
     │                        └─► ClinPGx lexicon match  (pgx_kb.extract_entities)
     │
     ├─► (B) ClinPGx lookup   → ranked curated rows + the PMIDs ClinPGx cites
     │                          (pgx_kb.search_detailed)
     │
     ├─► (C) PubMed check     → fetch those exact PMIDs, then top up with a live search
     │        [phase 4]         (PubMedSearcher.fetch_by_pmids / search_detailed)
     │
     ├─► (D) full text        → PMID → PMCID → JATS XML body → (fallback) OA PDF
     │        [phase 5]         (PubMedSearcher.fetch_fulltext)
     │
     └─► (E) log everything   → evidence_log + collect_references()
```

Phase selection is purely configuration:

| Phase | `AMG_KB_SOURCE` | `AMG_PUBMED_FULLTEXT` | Runs stages |
|---|---|---|---|
| 3 | `pharmgkb` | `0` | A, B, E |
| 4 | `pharmgkb+pubmed` | `0` | A, B, C, E |
| 5 | `pharmgkb+pubmed` | `1` | A, B, C, D, E |

---

## 2. (A) Finding the words

Two **independent** extractors run, and they deliberately disagree — that redundancy is what
keeps recall up when either one fails.

### 2.1 LLM entity extraction

The `entity_extractor` chain asks the model for medical entities plus a 1–10 relevance score
and a description. Model output is messy in practice, so `build_knowledge_graph` normalizes
three different shapes into parallel lists:

- three parallel arrays (`entities` / `scores` / `descriptions`) — the documented format
- a single array of dicts (`{name, score, description}`) — what llama3.1/qwen often return
- bare strings

If extraction fails entirely it falls back to salient words from the question (`len(w) > 4`),
so the graph is never empty. The first **8** entities become KG nodes.

### 2.2 ClinPGx lexicon matching — `pgx_kb.extract_entities()`

This does **not** use the LLM. It matches the question text against vocabularies built from
the ClinPGx tables at load time:

| Vocabulary | Size | Built from |
|---|---|---|
| drugs | 669 | `chemicals` column of `clinicalVariants.tsv` |
| phenotypes | 376 | `phenotypes` column |
| genes | 1,087 | `gene` column |

The matching rules:

**Normalization** — `_norm()` lowercases and collapses whitespace, applied to both the text
and every vocabulary term, so casing and spacing never cause a miss.

**Word-boundary matching** — the critical detail. Terms are matched with a custom boundary
that ignores `\b`'s treatment of punctuation:

```python
re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text)
```

`re.escape` means drug names containing regex metacharacters can never corrupt the pattern.
The lookarounds prevent substring false positives — searching for the gene `ABCB5` will not
fire inside `ABCB51`, and the drug `dapsone` will not fire inside `dapsonelike`.

**Length floors** — drugs and phenotypes need ≥ 4 characters, genes ≥ 3. Without this, short
gene symbols and abbreviations match constantly in ordinary prose.

**Synonym expansion** — three hand-built maps bridge patient language to table vocabulary:

- `PHENO_SYNONYMS`: `hearing loss`, `deafness`, `tinnitus` → `ototoxicity`;
  `heart failure`, `cardiomyopathy` → `cardiotoxicity`; `liver injury` → `hepatotoxicity`
- `DRUG_SYNONYMS`: brand → generic (`Platinol` → `cisplatin`, `Adriamycin` → `doxorubicin`)
- `DRUG_CLASS_MEMBERS`: class → members (`anthracycline` → doxorubicin, daunorubicin,
  epirubicin, idarubicin)

**Star alleles** — `CYP2D6*4` is not a table token, so a second pass runs
`re.findall(r"([a-z0-9]+)\*[0-9a-z]+", text)` and keeps the stem if it is a known gene.
`gene_of_allele()` does the same normalization for lookups (`CYP2D6*4` → `cyp2d6`).

**Worked example.** For *"After several cycles of Platinol, my child has permanent inner ear
damage and GSTT1 was mentioned"*:

```
{'drugs': ['cisplatin'], 'phenotypes': [], 'genes': ['gstt1']}
```

The brand name resolved through `DRUG_SYNONYMS` and the gene matched directly — but
`phenotypes` is **empty**, because "inner ear damage" is not in `PHENO_SYNONYMS`. The lookup
then falls back to drug-only, which still works but returns less targeted rows. This is the
single highest-value place to improve recall (see §7.1).

---

## 3. (B) ClinPGx lookup and ranking — `pgx_kb.search_detailed()`

Lookup is tiered, most specific first:

1. **(drug, phenotype)** via the `by_drug_pheno` index — the precise hit
2. **drug only** via `by_drug` — the fallback when no phenotype was recognized
3. **phenotype only** / **gene only** — when no drug appears in the question

Results are ranked by PharmGKB evidence level, strongest first:

```
LEVEL_RANK = {1a:0, 1b:1, 2a:2, 2b:3, 3:4, 4:5}     # sort order
LEVEL_CONF = {1a:0.98, 1b:0.9, 2a:0.8, 2b:0.7, 3:0.55, 4:0.4}   # KG edge confidence
```

`LEVEL_CONF` never drops below **0.4** on purpose: graph path exploration uses a 0.3
confidence threshold, so even level-3/4 evidence stays traversable instead of being silently
pruned.

Each returned record carries its own provenance:

```json
{"source": "ClinPGx",
 "ref": "ClinPGx:ACYP2/rs1872328:L3",
 "text": "ACYP2 (rs1872328): PharmGKB evidence level 3 linking it to cisplatin-related ...",
 "gene": "ACYP2", "variant": "rs1872328", "level": "3", "drug": "cisplatin",
 "pmids": ["25665007", "26928270", "28445188"]}
```

That `pmids` list is the bridge to phase 4. It comes from `pmids_for_pair()`, which reads the
`PMIDs` column of `relationships.tsv` for the gene–drug pair (127,988 pairs indexed, stored
both directions, with definite associations preferred over `ambiguous`).

**Set-membership gating.** `is_associated()` returns `associated` / `not associated` /
`ambiguous` / `None`. `_pgx_premise_note()` uses it to catch false premises: when a question
asserts a gene–drug link the tables have no row for, a corrective NOTE is prepended to the
evidence. This is what makes the system answer *"there is no established PharmGKB association
between CYP2D6 and doxorubicin"* instead of inventing a mechanism.

---

## 4. (C) The PubMed check — phase 4

The ordering here is the whole idea: **cited PMIDs first, blind search only as filler.**

1. Collect `pmids` from every ClinPGx record just retrieved.
2. `fetch_by_pmids(cited[:max_results])` — fetch those exact papers, tagged
   `via: clinpgx_citation`. This *verifies the curated claim against its own source
   literature* rather than searching the topic afresh.
3. If fewer than `max_results` were found, top up with `search_detailed(query)` — a live
   esearch — skipping PMIDs already present.

In the 10-question ADR run this produced **360 citation-backed retrievals vs 56 search-based**
ones: the large majority of evidence is traceable to ClinPGx's own references.

### Fetching and parsing

The original code fetched `rettype=abstract` plain text and split on blank lines, dropping any
line containing "author"/"doi"/"pmid" — which threw the PMID away, so nothing could be cited.
The rewrite fetches **XML** and parses fields properly:

| Field | XPath |
|---|---|
| PMID | `.//MedlineCitation/PMID` |
| title | `.//Article/ArticleTitle` |
| abstract | `.//Abstract/AbstractText` (all sections joined) |
| journal | `.//Journal/Title` |
| year | `.//JournalIssue/PubDate/Year` |

`_xml_text()` flattens inline markup via `itertext()`, so italics/sub-tags inside a title do
not shred it into fragments. The prompt-ready string is capped at 2,000 characters and
prefixed `[PMID 25665007] (Nature genetics, 2015) …` so the model sees the citation inline.

### Being a good NCBI citizen

- **Rate limit:** `_MIN_INTERVAL = 0.34 s` between calls (~3/s, NCBI's unauthenticated
  ceiling; set `pubmed_api` in `.env` to go faster).
- **Cache:** `_article_cache` per PMID, `_fulltext_cache` per PMID. The same paper cited by
  several genes is fetched once. `fetch_by_pmids` returns **copies**, so a phase-5 full-text
  upgrade can't corrupt the cached abstract.
- **Failure isolation:** every network call is wrapped; a failure logs and returns empty
  rather than killing the question.

---

## 5. (D) Full text — phase 5

Abstracts are all `efetch` gives you. To go deeper:

1. **`elink`** `dbfrom=pubmed&db=pmc` → the `pubmed_pmc` LinkSetDb → `PMCxxxxxxx`.
   No PMC id means no open-access copy exists; stop here and keep the abstract.
2. **JATS XML** — `efetch db=pmc`, take `.//body`, concatenate every `<p>`. A non-OA article
   returns metadata *without* a `<body>`, which is detected and treated as "no full text".
3. **OA PDF fallback** — query the OA service for a `format="pdf"` link, rewrite the returned
   `ftp://` URL to `https://`, and extract text with `pypdf`. **pypdf is optional**: if it is
   not installed this path returns empty and the abstract is used. (Install with
   `pip install --no-index pypdf`.)

Only the **top 2** PubMed items per question are upgraded, and only at the `reasoning` stage —
entity descriptions get truncated to 500 characters anyway, so full text there would be wasted
calls. `AMG_FULLTEXT_MAX_CHARS` (default 3,000) caps what enters the prompt; mind the serving
model's context window.

When an upgrade succeeds the record is re-tagged so the trail is preserved through both steps:

```
ref  : PMID:25108385  →  PMID:25108385/PMC4999337
via  : clinpgx_citation  →  clinpgx_citation+pmc_xml
```

---

## 6. (E) Where retrieval is called, and what gets logged

Three call sites, each with its own budget and stage tag:

| Stage tag | Called from | Query | `max_results` |
|---|---|---|---|
| `question_context` | `build_knowledge_graph` | question + options | 3 |
| `entity:<name>` | per extracted entity (≤ 8) | the entity name alone | 2 |
| `reasoning` | `reason_with_graph` / `reason_open_with_graph` | question + top 3 KG entities | 2 |

Full-text upgrades happen **only** at `reasoning`.

Every item is appended to `self.evidence_log`:

```json
{"stage": "reasoning", "query": "…", "source": "PubMed",
 "ref": "PMID:25665007", "snippet": "…", "title": "…",
 "journal": "Nature genetics", "year": "2015", "via": "clinpgx_citation"}
```

`collect_references()` deduplicates by `ref` and records every stage each reference was used
in. Both fields land in the results JSONL (`references`, `evidence_log`), and the log is reset
per question. Reference id formats:

| Form | Meaning |
|---|---|
| `ClinPGx:GENE/variant:Llevel` | curated table row + evidence level |
| `PMID:xxxxxxx` | PubMed abstract |
| `PMID:xxxxxxx/PMCxxxxxxx` | abstract upgraded to full text |
| `Wikipedia:Title` | Wikipedia summary (paper baseline only) |

---

## 7. How to make search better

Concrete levers, highest value first.

### 7.1 Widen the phenotype lexicon (biggest recall win)

`PHENO_SYNONYMS` in `pgx_kb.py` is hand-built and small. "Inner ear damage", "ringing in the
ears", "trouble hearing" all fail to reach `ototoxicity`, downgrading the lookup from
(drug, phenotype) to drug-only. Add lay-language variants, or map through a medical
vocabulary (MeSH/UMLS synonyms) instead of a literal dict.

### 7.2 Build the esearch query from entities, not raw question text

**This is a real defect, inherited from the original paper code.** The live search passes the
whole question as `term`, and NCBI ANDs every token. A long patient-style question therefore
returns *nothing*:

```
esearch("My child on cisplatin developed hearing loss. What genetic variants …")  →  []
esearch("cisplatin ototoxicity genetic variants")                                 →  3 PMIDs
```

When it does return results they are often off-topic (the ADR run pulled a 2026 dermatology
paper into a cisplatin question). Fix: compose the term from extracted gene/drug/phenotype
entities, e.g. `("cisplatin"[tiab] AND "ototoxicity"[tiab])`, and consider `sort=relevance`.
I have **not** applied this yet — it changes retrieval output, so it should land together with
a re-run of all three phases to keep the comparison consistent.

### 7.3 Scope entity-level searches

Each of the ≤ 8 entities is searched independently, so a cisplatin question also pulls
capecitabine/DPYD rows. Options: restrict entity searches to entities the ClinPGx lexicon
actually recognizes, or filter returned rows to the drug named in the question.

### 7.4 Raise the evidence budget

`max_results` of 2–3 per stage is conservative. More evidence costs prompt tokens, so raise it
together with the model's `num_ctx`.

### 7.5 Cover more full text

Only 2 of ≤ 20 upgrade attempts succeeded in the ADR run — most ClinPGx-cited papers are older
and not open-access. Installing `pypdf` enables the OA PDF path; beyond that, Europe PMC or a
publisher API would be needed. Rank candidates by OA availability before spending calls.

### 7.6 Rank instead of truncate

Ranking is by PharmGKB evidence level only, then the list is cut. Semantic similarity between
the row text and the question (the embedding stack is already imported) would order results
better than level alone.

---

## 8. What changed versus the original code

| Area | Before | Now |
|---|---|---|
| PubMed parsing | plain-text split; lines containing "pmid"/"doi" discarded | XML parse of PMID, title, abstract, journal, year |
| Citations | impossible — PMIDs were stripped | every item carries a stable `ref` |
| Rate limiting | none | 0.34 s between NCBI calls |
| Caching | none | per-PMID abstract and full-text caches |
| Full text | none | PMC JATS XML + OA PDF fallback |
| ClinPGx retrieval | `search()` → `List[str]` | `search_detailed()` → records with gene/variant/level/**cited PMIDs** |
| ClinPGx ↔ literature | disconnected | `pmids_for_pair()` links table rows to their sources |
| Provenance | none | `evidence_log` + `references` persisted per question |
| Entity `sources` | guessed (`["PubMed","Wikipedia"]` regardless of what returned) | the sources that actually contributed |
| Retrieval seams | scattered calls | one `_evidence_search_detailed` |

The legacy `search(query, max_results) -> List[str]` contract still exists on both searchers,
so nothing downstream had to change.

---

## 9. Reproducing and inspecting

```bash
# all three phases, one job, env vars as the only difference
sbatch run_adr_phases345_alliance.bash

# single phase, by configuration alone
export AMG_KB_SOURCE=pharmgkb          # phase 3
export AMG_KB_SOURCE=pharmgkb+pubmed   # phase 4
export AMG_PUBMED_FULLTEXT=1           # phase 5
python run_genmedgpt.py

# render the 3-way comparison
python make_adr_phase45_report.py --tag adrclin
```

Inspect what any question actually retrieved:

```bash
python -c "
import json
r = [json.loads(l) for l in open('results/adrclin_phase5_fulltext.jsonl')][0]
for e in r['evidence_log']:
    print(e['stage'], '|', e['source'], '|', e['ref'], '|', e.get('via',''))
"
```
