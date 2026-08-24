# How Phase 9 works

Phase 9 is the combined-topic literature phase: **entities that are related in the knowledge
graph are searched together as one conjunctive PubMed query, and the resulting papers are read
in full** where an open-access copy exists.

```bash
AMG_KB_SOURCE=pharmgkb+pubmed_combo    # phase 8 (abstracts) + this line = phase 9
AMG_PUBMED_FULLTEXT=1
```

Nothing else differs from phases 3–8: same code, same entry point (`run_genmedgpt.py` →
`AMG_RAG_System.answer_open_question`), same model. Only environment variables change.

---

## 1. Why it exists

| Phase | Search shape | Failure it hit |
|---|---|---|
| 4/5 | only the PMIDs ClinPGx already cites | cannot see anything ClinPGx never curated |
| 6/7 | one topic per query, LLM-chosen | a bare entity (`tinnitus`) returns PubMed's *newest* match — a dural AV fistula case report. **20–23% on-topic** |
| **9** | **related terms combined into one query** | **54% on-topic**, and 6 papers read in full |

A single term is ambiguous; a conjunction is not. `tinnitus` matches any audiology paper, but
`tinnitus AND cisplatin AND hearing loss` can essentially only match a paper about the link
the graph says exists.

---

## 2. The pipeline for one question

```
question
   │
   ├─(1) ClinPGx lookup ────────► curated gene/variant rows (evidence levels, cited PMIDs)
   │                                 │
   ├─(2) build the KG ──────────► entities + relations (edges)
   │                                 │
   ├─(3) combo-query chain ◄────────┘  LLM sees the EDGES + evidence,
   │            │                      groups related terms, picks the arity
   │            ▼
   ├─(4) conjunctive PubMed search   "cisplatin AND GSTM1 AND ototoxicity"
   │            │                     ── empty? drop the last term and retry (back-off)
   │            ▼
   ├─(5) full-text upgrade          PMID → PMCID → JATS XML body (→ OA PDF fallback)
   │            │
   └─(6) reason and answer ◄────────┘  + log every query to `search_shape`
```

---

## 3. Step by step

### (1) ClinPGx grounding — unchanged from phase 3

`pgx_kb.search_detailed()` matches the question against the ClinPGx vocabularies and returns
curated rows with evidence levels, plus the PMIDs `relationships.tsv` cites. Phase 9 keeps
this: the literature search *supplements* the curated tables, it does not replace them.

### (2) The knowledge graph supplies the relations

`_seed_pgx_edges()` inserts curated edges (drug → gene → variant, weighted by evidence level)
and the LLM relation-extraction pass adds its own. `_graph_relation_context()` then flattens
the top edges above 0.3 confidence into text the query builder can read:

```
cisplatin -[response_modulated_by[3]]-> GSTM1
Ototoxicity -[risk_modulated_by[3]]-> TPMT
GSTM1 -[has_variant]-> GSTM1 non-null
```

**This is the input that makes phase 9 different from phase 7.** Phase 7's chain sees entity
*names*; phase 9's chain sees which entities are *connected to each other*.

### (3) The combo-query chain decides what to combine, and how many

`combo_query_chain` receives the question, those edges, and the evidence so far, and returns
groups of 2–4 terms joined by ` + `. The prompt asks it to combine terms that co-occur in the
relations — a drug with the gene that modulates it, a gene with the adverse effect it
predisposes to — and to vary the group size. **The model chooses the arity; the code does not
impose one.**

Caps (env-tunable): `AMG_COMBO_MAX_QUERIES=4` groups per stage, `AMG_COMBO_MAX_TERMS=4` terms
per group, `AMG_OPEN_PER_PHRASE=2` papers per query.

Two safeguards:

- **Entity stages skip the chain.** When the query *is* a single entity name, the code pairs it
  deterministically with the question's own drug/adverse-effect anchors
  (`_question_anchors()`), so `tinnitus` becomes `tinnitus AND cisplatin AND hearing loss`.
  This is what removed the phase 6/7 noise, and it costs no extra LLM call.
- **Fallback.** If the chain fails or returns junk, groups are built by pairing each retrieved
  ClinPGx gene with the question's drug. In the 10-question run the chain never failed.

### (4) Conjunctive search with back-off

`_combo_pubmed_search()` joins the terms with ` AND ` and searches. A conjunction is precise
but can over-constrain, so **an empty result drops the last term and retries**, down to a floor
of 2 terms. Hits from different groups are then interleaved **round-robin**, so every group
contributes instead of the first one consuming the budget.

Real example from the run (Q1, `GSTM1 (GSTM1 non-null)` entity stage):

```
GSTM1 GSTM1 non-null AND cisplatin AND hearing loss   → 0 hits
GSTM1 GSTM1 non-null AND cisplatin                    → 0 hits   (floor reached, give up)
```

versus one that worked first try:

```
ACYP2 rs1872328 AND cisplatin AND hearing loss        → 2 hits
```

### (5) Full-text upgrade — the part that makes it phase 9 rather than phase 8

At the **reasoning stage only**, the top 2 PubMed items are upgraded by `fetch_fulltext()`:

1. `elink` PMID → PMCID (no PMCID ⇒ no open-access copy ⇒ keep the abstract)
2. `efetch db=pmc` → JATS XML, concatenate every `<p>` under `<body>`
3. if the XML has no `<body>` (not open access), fall back to the OA PDF via `pypdf`

`AMG_FULLTEXT_MAX_CHARS` (default 3,000) caps what enters the prompt. Entity stages are
deliberately excluded — their descriptions are truncated to 500 characters anyway, so full
text there would be wasted calls.

The provenance is chained, not overwritten:

```
ref : PMID:39386217        →  PMID:39386217/PMC11461197
via : combo2:cisplatin + GSTM1  →  combo2:cisplatin + GSTM1+pmc_xml
```

so you can still see the query that found it *and* how it was read.

### (6) Everything is logged

Each issued query appends one record to `search_shape` in the results JSONL:

```json
{"stage": "reasoning", "requested_arity": 3, "used_arity": 3,
 "terms": ["COMT", "rs4646316", "hearing loss"], "backoffs": 0, "hits": 2}
```

Every retrieved item also appends to `evidence_log`, and `references` holds the deduplicated
citation list.

---

## 4. A complete real trace (Q1)

16 queries were issued for *"I am a child receiving cisplatin … what genetic variants make me
susceptible to this ototoxicity?"*:

| Stage | Query | Terms | Back-off | Hits |
|---|---|---|---|---|
| question | `cisplatin AND ACYP2` | 2 | 0 | 2 |
| question | `cisplatin AND GSTM1 AND ototoxicity` | 3 | 0 | 2 |
| question | `TPMT AND ototoxicity` | 2 | 0 | 2 |
| question | `hearing_loss AND tinnitus AND pharmacogenomics` | 3 | 0 | 2 |
| entity | `cisplatin AND hearing loss` | 2 | 0 | 2 |
| entity | `cancer AND cisplatin AND hearing loss` | 3 | 0 | 2 |
| entity | `tinnitus AND cisplatin AND hearing loss` | 3 | 0 | 2 |
| entity | `ACYP2 rs1872328 AND cisplatin AND hearing loss` | 3 | 0 | 2 |
| entity | `GSTM1 GSTM1 non-null AND cisplatin` | 2 | 1 | 0 |
| entity | `TPMT TPMT*1 AND cisplatin` | 2 | 1 | 0 |
| reasoning | `cisplatin AND ACYP2` | 2 | 0 | 2 |
| reasoning | `GSTM1 AND ototoxicity` | 2 | 0 | 2 |
| reasoning | `TPMT AND cisplatin` | 2 | 0 | 2 |
| reasoning | `COMT AND rs4646316 AND hearing loss` | 3 | 0 | 2 |

Note `cancer` and `tinnitus` — the exact terms that produced junk in phase 7 — are here
anchored to `cisplatin AND hearing loss` and stay on topic.

The two failures are informative: the entity names arrive as `GSTM1 (GSTM1 non-null)`, which
cleans to the duplicated string `GSTM1 GSTM1 non-null` and matches nothing in PubMed. That is a
real rough edge worth fixing (strip the parenthetical before searching).

---

## 5. What it measured, across all 10 questions

| | Phase 9 |
|---|---|
| Queries issued | 159 (15.9 per question) |
| 2-term / 3-term / 4-term | 80 (50%) / 79 (50%) / 0 (0%) |
| Mean arity requested → searched | 2.50 → 2.38 |
| Back-offs | 18 of 159; 10 (6%) still empty |
| Hit rate | 90% for 2-term, **100%** for 3-term |
| On-topic precision | **54%** (vs 20–23% in phases 6/7) |
| Papers read in full | 6 |
| Genes grounded in retrieved evidence | 100% |
| ClinPGx-valid genes | 95% |

The LLM never requested a 4-term query despite being allowed up to 4 — it self-limited to
conjunctions it expected to return results, which the low back-off rate confirms.

---

## 6. Running it

```bash
sbatch run_adr_phase89_alliance.bash          # phases 8 then 9
python make_adr_phase89_report.py --tag adrclin   # search-shape report
python make_adr_all_phases_report.py              # all phases in one file
```

Inspect the search shape of any question directly:

```bash
python -c "
import json
r = [json.loads(l) for l in open('results/adrclin_phase9_combo_fulltext.jsonl')][0]
for c in r['search_shape']:
    print(c['used_arity'], 'terms |', ' AND '.join(c['terms']), '->', c['hits'], 'hits')
"
```

---

## 7. Known limits

- **Entity names with parentheticals** (`GSTM1 (GSTM1 non-null)`) become duplicated tokens that
  match nothing. Two of 16 queries in the Q1 trace were wasted this way.
- **Conjunctions bias toward what the graph already believes.** Phase 9 is good at finding
  evidence *about known links* and correspondingly weaker at surprising you — phase 7's looser
  search is the one that stumbles onto unrelated-but-relevant work.
- **Full text is still scarce** (6 of ~20 attempts): most pharmacogenomics literature is not
  open access.
- **On-topic % is a keyword proxy**, so 54% is a lower bound.
