# The three best configurations — approach, strengths, weaknesses

Out of twelve configurations, three are worth keeping. They are not ranked on one axis, because
they optimise different things: **phase 4** is the safe citable baseline, **phase 9L** maximises
recall and contradiction discovery, **phase 11** maximises precision and is the only high-evidence
phase that resists a false premise.

| | Phase 4 | Phase 9L | Phase 11 |
|---|---|---|---|
| One-line summary | verify the curated claim against its own citations | cast the widest net, then weigh it | search precisely, then weigh it |
| Retrieval | ClinPGx-cited PMIDs | graph-related terms, `AND`-joined | model-authored queries, free arity |
| Papers read in full | no | yes (7) | yes (4) |
| Per-gene confidence | no | yes | yes |
| Genes per question | 2–3 | **11.6** | 9.6 |
| On-topic precision | 22% | 52% | **65%** |
| Catches the false premise | **✅** | ❌ | **✅** |
| Runtime (10 questions) | ~37 min | 45 min | 47 min |

---

## Phase 4 — ClinPGx + its own cited literature

### Approach

ClinPGx returns curated gene–variant–drug rows with PharmGKB evidence levels. Rather than
searching PubMed for the *topic*, phase 4 fetches **the exact PMIDs `relationships.tsv` cites
for those pairs** (`pmids_for_pair()`), tagged `via: clinpgx_citation`. A live search only tops
up when the citations run short. Each paper is parsed from XML into PMID/title/abstract/journal/
year, so every statement can carry a citation.

The important property: this **verifies a curated claim against the literature that produced
it**, rather than asking PubMed an open question. 360 of 416 PubMed retrievals in the phase-4/5
runs came from citations rather than search.

### Strengths

- **Highest reliability of any phase**: 95% ClinPGx-valid, 100% grounded.
- **The only simple phase that catches the Q8 false premise** — it answers *"there is no direct
  pharmacogenomic link between CYP2D6 and doxorubicin"* rather than inventing a mechanism.
- **Recovered ACYP2** on Q1/Q3 with its *Nature Genetics* GWAS — the validated cisplatin
  ototoxicity locus that phase 3 missed.
- Cheapest of the three, and the least machinery.

### Weaknesses

- **Cannot see anything ClinPGx has not curated.** By construction it never surfaces a novel
  candidate — for a discovery goal this is disqualifying.
- **Low precision on its top-up searches (22% on-topic)**: the residual live search passes the
  raw question to `esearch`, which ANDs every token and returns little or nothing useful.
- **No confidence, no contradiction handling.** It reports curated facts as flat assertions,
  even for pairs ClinPGx itself marks ambiguous.
- Names only 2–3 genes.

**Use it when** you need a defensible, conservative answer and novelty is not the goal.

---

## Phase 9L — phase-9 retrieval + the ledger

### Approach

The model sees the **knowledge-graph edges** and groups related entities into a single
conjunctive query — `cisplatin AND ACYP2 AND hearing loss` — assembled by code with a fixed
arity of 2–4. An over-constrained query backs off by dropping its last term; entity-stage
queries are anchored to the question's own drug and adverse effect.

Retrieved papers are then read paragraph by paragraph (the digest stage), and every claim —
curated or literature — is aggregated into the **evidence ledger**, which computes confidence by
rule and flags contradictions.

### Strengths

- **The widest net of any configuration**: 116 gene–drug pairs, 145 PubMed references, 35
  papers digested, 7 read in full — roughly **3× phase 11's literature volume**.
- **Finds the most contradictions: 72**, including the only `curated_vs_literature` flags
  (5) and the most `literature_internal` disagreements (10) — the cases where the papers
  actually contradict the tables or each other.
- **Only configuration to raise `uncurated_literature_claim`** (4 times): genes not in ClinPGx
  but supported by human studies, i.e. candidate novel associations.
- Conjunctions are reliable: 160 queries, only 11 empty, 18 recovered by back-off.

### Weaknesses

- **Lower precision than phase 11** (52% vs 65% on-topic).
- **Misses the Q8 false premise** — with 145 references in play, the corrective ClinPGx note is
  crowded out of the answer.
- **Gene-symbol noise**: emitted `ABCB-1`, `ABCC-1`, `ABCG-2`, `GST-PI` — hyphenated duplicates
  that become separate ledger entries. Fixable by canonicalising against `pgx_kb`'s
  1,087-symbol vocabulary.
- **Arity is capped** at 2–4 by the prompt; it never issues a single-concept survey query.
- Highest `unsupported_claim` count (38) — the wide net pulls in genes with nothing solid behind
  them. They are labelled as such, but they inflate the ledger.

**Use it when** the goal is discovery and contradiction-hunting, and you will read the ledger
rather than the prose.

---

## Phase 11 — free-form retrieval + the ledger

### Approach

Identical analysis to phase 9L; the difference is retrieval. The model authors the PubMed query
itself — deciding whether to search one concept or five, and writing the string with quoted
phrases, `OR` groups and field tags passed through verbatim. Empty queries are relaxed by
dropping field tags, then terms.

It used that freedom: arity ranged **1 to 5** (31 single-term, 11 four-term, 1 five-term) where
phases 8/9/9L never left 2–3.

### Strengths

- **Best retrieval precision of any phase: 65% on-topic.**
- **Catches the Q8 false premise** — the only ledger phase that does, likely because it carries
  a third of phase 9L's reference volume, leaving the corrective note visible.
- **Calibrated confidence, measured**: on 72 labelled pairs, positive−negative separation
  **+0.351**, Spearman **0.721**, and *all 16* negatives placed in `very_low` — it reliably
  declines to endorse pairs ClinPGx marks "not associated", the hard direction.
- **Contradiction recall 0.95** (20 of 21 disputed pairs).
- Zero empty queries; the model self-limits its arity sensibly.

### Weaknesses

- **Retrieves far less than 9L**: 48 PubMed refs vs 145, 96 pairs vs 116. Its query plan is
  cached per stage-class, so fewer distinct queries are issued.
- **Contradiction precision is only 0.47** — it over-flags, though much of that is genuine
  disagreement rather than error.
- **Confidence is compressed low**: positives average 0.424 and nothing reaches `high`. The
  ambiguity damping plus log-damped support term is probably too conservative.
- **Target-pair recall 65–84%** on the benchmark: a third of positive pairs were never surfaced.

**Use it when** you want the most trustworthy weighted answer per question, and precision
matters more than exhaustiveness.

---

## Shared weaknesses (both ledger phases)

1. **Answers do not cite.** 0–1 of 10 answers contain a `PMID:` reference, although the ledger
   carries paragraph-level refs like `PMID:42633148/PMC13499120#p34`. The prompt asks; the
   14B model largely ignores it. **The ledger is the product — the prose is not.**
2. **The ledger's curated lookup bypasses `_evidence_search_detailed`**, so those ClinPGx rows
   never enter `evidence_log` or `references`. Auditing a ledger gene through the normal
   provenance path fails even though the ledger cites it.
3. **Digest coverage is capped** at 6 batches per paper (~29% of a long article) — now spent on
   the most finding-dense sections, but still partial.
4. **Confidence has been validated only on 72 pairs**, and against labels drawn from a source
   the system also retrieves from.

---

## Recommendation

**Run 9L and 11 together, not one or the other.** They disagree productively: per question they
share most genes (Q3: 16 of ~19; Q7: 8 of 9) but each finds several the other misses — 9L
surfaced ALDH2/SIRT3/IDH2 on Q1, phase 11 surfaced NFE2L2 and MT-RNR1. The union is the
candidate set; agreement between two independent retrieval strategies is itself a confidence
signal worth adding to the ledger.

Keep **phase 4** as the conservative control in any comparison — it is the honest "curated
evidence only" baseline, and the only cheap configuration that resists a false premise.
