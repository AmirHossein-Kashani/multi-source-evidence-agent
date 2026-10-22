# Method update plan: evidence-driven graph search

Status: decided 2026-10-22. Implementation tracked in the sections below; phase 15 is the
first configuration that runs it (`run_adr_phase15_alliance.bash`).

## 1. Why

The phase-13 system seeds a per-question graph from ClinPGx and LLM relation extraction,
searches PubMed once from a flat list of graph edges, scores evidence with fixed rules, and
writes an answer. The audit (`claim_evidence_audit.md`) and the ledger analysis found:

- evidence is grouped by gene+drug, so an outcome mismatch (MLH1/MSH3: kidney injury counted
  as ototoxicity) is invisible;
- the drug of every literature claim is taken from the question, not the paper (SLCO1B1: a
  methotrexate paper counted as cisplatin evidence);
- drug-class rows ("Platinum compounds") escape literal matching;
- protein-biomarker findings are scored as inherited-variant evidence (CPVL/PIGR);
- the paper's study type is "strongest chunk wins", so a cohort study citing a meta-analysis
  in its discussion gets weight 1.0;
- literature-only pairs cannot score above "low" (base 0.25), are labelled *disputed*, and
  rank below the 12-entry cut, so none of the 9 candidate associations in phase 13 reached
  an answer;
- 83% of disagreement cards are `INSUFFICIENT` and the search never reacts to that;
- multi-hop paths exist only as prose for the reasoning prompt; search uses no path
  structure.

## 2. Decisions

| Question | Decision | Reason |
|---|---|---|
| Synonyms for the ADR outcome and drug classes | **MeSH** (entry terms for synonyms, tree parents for drug classes), fetched through E-utilities once and cached in `dataset/mesh_cache.json`; the hand-written tables in `pgx_kb.py` stay as the offline fallback | Standard vocabulary PubMed itself is indexed with; fixes the class-matching audit error from a maintained source instead of a growing hand list |
| Do LLM-hypothesised edges count as path steps? | **No.** Discovery paths are curated-only (ClinPGx rows + MeSH classes). Hypothesised edges enter the queue as single edges with a low prior, so they are still tested, but never compose into a path | Every proposed edge stays traceable to a database row; LLM edge confidences are uncalibrated numbers |
| Confidence cap for literature-only pairs | **Lift partially.** A pair with no curated row starts at base 0.25; if at least two *independent* sources of weight >= 0.85 (cohort, trial, GWAS, meta-analysis) support it, the base becomes 0.45, between curated Level 4 (0.40) and Level 3 (0.55). The maximum a literature-only pair can reach is ~0.64 (*moderate*); *high* stays curated-only | Discovery can show up in the score, but curated evidence keeps precedence, and the rule is one line in Section 3.4 |

## 3. Design: one edge queue, one loop

Every candidate (gene, drug, outcome) relation is an **edge with a status**
(`untested / confirmed / refuted / insufficient`) and a **provenance** tag. A loop spends a
search budget on the edges that most need testing.

| Edge source | Provenance | Prior |
|---|---|---|
| ClinPGx direct rows for the question's drug | `curated` | level base |
| LLM pairwise relation extraction | `hypothesised` | 0.30 |
| Metapath A: gene linked to the ADR outcome (MeSH synonyms), drug from the question | `path:A:outcome` | 0.50 |
| Metapath C: gene curated for the drug's MeSH class (e.g. Platinum compounds) | `path:C:class` | 0.55 |
| Metapath B: gene–gene neighbour of a curated gene, hub-penalised (Adamic–Adar) | `path:B:gene` | 0.35 |
| Claims extracted from papers in the previous round | `literature` | ledger score |
| Follow-up from a disagreement card | `followup:<status>:<axis>` | 0.60 |

**Allocator.** Rank queued edges by `uncertainty × prior`, where uncertainty is highest for a
ledger score near 0.5, few sources, or an `INSUFFICIENT` card. Issue queries for the top-k
(`AMG_QUERY_BUDGET`). This replaces the even split of `AMG_COMBO_MAX_QUERIES`.

**Rounds.** After each round: digest new papers, rebuild the ledger and the cards, write
literature claims back into the graph as edges carrying their ledger score and refs. Stop
after `AMG_SEARCH_ROUNDS` rounds (default 2) or when a round adds no edge of cohort weight or
better.

**Follow-up queries (idea 3).** `INSUFFICIENT` → `gene AND drug AND outcome` restricted to
`meta-analysis[pt] OR systematic review[pt] OR cohort`; `CONTEXT-DEPENDENT` on an axis →
the same query plus the refuting side's axis value; `CONFLICTING` with no axis → the query
plus `replication`.

**Answer.** Ledger + cards as before, plus a separate **"Candidate associations not in
ClinPGx"** block that sits outside the 12-entry cut, each with its proposing path and refs.

## 4. Step 0 fixes (prerequisites)

1. Ledger groups by gene + drug + **outcome** (outcome normalised through MeSH synonyms;
   curated rows use their phenotype column, literature claims their `endpoint`).
2. Digest extracts `drugs_studied`; a claim whose drug matches neither the question drug nor
   its class is kept in the log but excluded from that drug's ledger (`drug_match=mismatch`).
3. `pgx_kb` drug expansion includes MeSH class parents; class-level curated rows are reported
   with `match=class`.
4. Digest extracts `evidence_kind` (`germline_variant / somatic / expression /
   protein_biomarker / unknown`); non-germline claims are weighted ×0.5 and flagged.
5. Study type = majority over read chunks, overridden by PubMed's own publication-type tags
   when they name a design (Meta-Analysis, Systematic Review, Randomized Controlled Trial,
   Case Reports, Review); papers tagged *Retracted Publication* are dropped.
6. `uncurated_literature_claim` no longer sets `disputed` (phase 13: 87 → 78 disputed pairs).

## 5. Build order

| Step | What | Where | Verified by |
|---|---|---|---|
| 0 | Fixes 1–6 | `evidence_ledger.py`, `pgx_kb.py`, `mesh_terms.py` (new), digest schema in `AMG-with-KG.py` | unit checks on the ledger and KB |
| 1 | Edge queue with status and provenance | `edge_queue.py` (new) | unit checks |
| 2 | Allocator (uncertainty × prior, budget) | `edge_queue.py` | unit checks |
| 3 | Metapath proposer A, C, B over the global ClinPGx graph | `graph_paths.py` (new) | yields on the cisplatin question: A=5, C=46, B hub-penalised |
| 4 | Follow-up queries from cards | `contradiction_layer.py` | unit checks |
| 5 | Rounds + write-back | `reason_open_with_graph` | phase-15 run |

All new behaviour is behind environment variables so phase 13 reproduces unchanged:
`AMG_PATH_DISCOVERY=1`, `AMG_SEARCH_ROUNDS=2` (code default 0 = off), `AMG_QUERY_BUDGET=6`,
`AMG_FOLLOWUP_SEARCH=1`. `run_adr_phase15_alliance.bash` sets them.

### Implementation status (2026-10-22)

Steps 0–5 are implemented and pass the offline tests in `tests/` (the loop is exercised with
fake PubMed and digest responses; the ledger, class matching, MeSH lookups and path yields
run against the real tables). Not yet run on the GPU with the model: phase 15 on the 10
development questions is the next job.

Details fixed while implementing, beyond the design above:

- **Budget reserve.** Curated-but-`INSUFFICIENT` edges have priority ~0.7, untested path
  proposals <= 0.55, so with a small budget discovery would never be searched. A third of
  each round's budget is reserved for untested edges (`EdgeQueue.select`).
- **Second attempts differ.** An edge's first query is `gene AND drug AND outcome`; its
  second drops the outcome and asks for association language
  (`polymorphism OR genotype OR variant OR allele`). A query string is never issued twice
  in one question.
- **Curated row outcome.** A ClinPGx row lists several phenotypes (cancer type, toxicity); it
  is filed under the one in the question's outcome family when present, else its first.
- **Write-back on seeded edges.** When a literature-backed group already has a curated edge
  in the graph, the literature refs are attached to that edge instead of adding a duplicate.
- **MeSH classes are not always the class you want.** The MeSH tree puts doxorubicin under
  daunorubicin, not "anthracyclines"; the static `DRUG_CLASS_MEMBERS` table stays as a
  complement. For cisplatin MeSH gives "platinum compounds", which is the ClinPGx node.
- **Pattern C never proposes curated negatives.** MLH1/MSH3–"Platinum compounds" rows are
  "not associated"; they reach the ledger through class matching as curated negatives
  (`match=class`), which is the audit fix, and are not discovery candidates.

## 6. Evaluation

| Test | Measures | Ground truth |
|---|---|---|
| E1 masked recovery (`make_masked_recovery.py`) | recovery of hidden curated edges, by metapath and by round | ClinPGx |
| E2 fixed-retrieval ablation | plain RAG → +ledger → +cards → +loop on the same cached evidence | human rating, 10 dev questions |
| E3 per-metapath precision | share of proposed candidates reaching cohort-or-better support | ledger + audit |
| E4 resolution | `INSUFFICIENT` → resolved (83% baseline); `CONSISTENT` count (0); dispute precision (0.47) | cards |
| E5 candidate reporting | candidates that reach the answer (0 of 9 baseline), audited | manual |

The 10 questions stay a development set. The 72-pair benchmark is the held-out set, with its
label-leakage caveat stated.

## 7. Parked

Idea 4 (snapshot-drift detector), idea 6 (citation-graph hop), idea 7 (refutation-seeking
queries: cheap once the queue exists; add as a query type).
