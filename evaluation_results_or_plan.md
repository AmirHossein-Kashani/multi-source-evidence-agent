# Evaluation: completed analyses and proposed experiments (Phase 14)

Part A contains analyses completed from cached outputs only — these numbers may be cited in the revised draft. Part B contains proposed experiments with runnable scripts; **no results from Part B appear in the manuscript**.

---

## Part A — completed analyses (cached data only)

### A1. Evidence-score validation, fully reported

Source: `results/ledger_evaluation.md` (phase 11 configuration; benchmark built by `make_pgx_benchmark.py` from the ClinPGx snapshot of 2026-07-05).

- Labels: curator-derived, machine-assembled (Association column of `relationships.tsv`); 23 positive / 24 negative / 25 disputed. Not human annotations made for this project.
- Surfacing recall (did the system's ledger contain the target pair at all): positive 15/23 (65%), negative 16/24 (67%), disputed 21/25 (84%).
- Over surfaced pairs only: mean evidence score positive 0.424, disputed 0.351, negative 0.073; separation (pos − neg) **+0.351** (15 vs 16 pairs); Spearman(score, label order) **0.721** over 52 pairs.
- Contradiction flag: **precision 0.47, recall 0.95, F1 0.62** (TP 20, FN 1, FP 23, TN 8). The flag over-fires; false positives come mainly from `curated_vs_literature` (21 raised) and `literature_internal` (18 raised) triggering on weak or dependent evidence.
- Known dependence: labels and scorer constants both derive from the same Association field; the system also retrieves from the same KB. Treat as in-development validation, not held-out performance.

### A2. Evidence-lineage and double-counting quantification

Script: `eval_lineage.py` (this phase). Run over `results/adrclin_phase13_resolution.jsonl` (145 ledger pairs):

| Quantity | Value | Meaning |
|---|---|---|
| Pairs with a curated claim inside the support list | 53 / 145 | The curated row raises both the base term and the support term. Bounded effect: support multiplier with a single weight-1.0 source is 1 + 0.18·ln 2 ≈ 1.125, so ≤ ~12.5% score inflation relative to base. |
| Literature supporting sources | 96 | After document-level dedup (`source_id()`), across all pairs. |
| …that are PMIDs ClinPGx itself cites for the same pair | **2** (2 pairs affected) | Document-level KB–literature double-counting is rare in this run. |

Unresolved: same-cohort dependence across different publications is not detectable from cached data.

### A3. False-premise probe: manual re-adjudication of all 12 phases

Probe: Q8 asserts a CYP2D6*4–doxorubicin cardiotoxicity link with no supporting row in the KB snapshot. Automatic scoring in `eval_adr_phases.py` uses regex `DENIAL_PATTERNS`; the table below is from reading the cached answers. Two judgments per answer: does it *explicitly deny* the direct link, and does it nevertheless *endorse* the premise (assert the mechanism or recommend CYP2D6-based action)?

| Phase | Regex verdict | Explicit denial present | Still endorses premise | Manual category |
|---|---|---|---|---|
| 3 | missed | no | yes (screening recommended) | asserts |
| 4 | caught | yes ("no direct pharmacogenomic link") | yes (mechanism + exposure story) | mixed |
| 5 | caught | yes (same text as 4) | yes | mixed |
| 6 | missed | no | yes | asserts |
| 7 | missed | no | yes | asserts |
| 8 | missed | no | yes | asserts |
| 9 | missed | no | yes | asserts |
| 9L | **missed (regex error)** | yes ("no strong support for a direct link") | partly (susceptibility wording) | mixed |
| 10 | missed | no | yes (invented ROS mechanism detail) | asserts |
| 11 | caught | yes ("no direct evidence … from PharmGKB") | yes ("concern … well-founded"; screening recommended) | mixed |
| 12 | caught | yes ("no established pharmacogenomic link") | yes ("likely influenced by his genetic predisposition") | mixed |
| 13 | **missed (regex error)** | yes ("evidence does not support an established association") | **no** — redirects action to clinical risk factors | **denies and redirects** |

Findings:
1. The regex mislabels 2 of 12 phases (9L, 13) because their denial phrasing ("no strong support", "does not support an established association") matches no pattern; it also credits 4 phases (4/5/11/12) that deny the link in one sentence and endorse it in the next.
2. Under manual reading, **phase 13 gives the strongest answer** of all twelve: explicit denial plus no CYP2D6-based recommendation. The previous drafts reported phase 13 as failing the probe; that was a measurement artifact.
3. Every phase's answer still opens by restating the premise sympathetically; none is a perfect refusal.
4. This is one probe question. It is a diagnostic case, not a safety measurement; no causal claim about evidence volume can be made from it.

### A4. What the phase table can and cannot support

Phases share code and differ by environment variables, but the variables change retrieval, so retrieved evidence differs across phases by design. The only near-controlled contrast is **phase 9 vs 9L** (same retrieval configuration; digest+ledger off/on): named genes per question rise from 2–3 (prose) to a ledger of 116 scored pairs with 53 paragraphs kept, at essentially unchanged retrieval volume (22.5 → 23.4 refs/q). Phase 12 vs 13 confounds the contradiction layer with a retrieval-mode change (`pubmed_free` → `pubmed_combo`) and must not be read as an ablation of the layer alone.

---

## Part B — proposed experiments (scripts ready; results deliberately absent)

### B1. Controlled comparison: plain RAG vs ledger vs ledger+resolution *(highest priority)*

Question (RQ1/RQ2): with retrieved evidence held fixed, does the structured ledger improve claim support and uncertainty reporting over ordinary RAG, and does contextual comparison improve disagreement classification?

Design: replay **cached evidence** (the persisted `evidence_log` + digests from phase 13 runs) into three answer conditions with the same model and question: (i) evidence pasted as plain context, no ledger (ordinary RAG); (ii) ledger text included, no cards; (iii) ledger + contradiction cards. Only the answer-generation call differs; retrieval cost is zero because evidence is replayed. ~30 LLM calls total (10 questions × 3 conditions) — small enough for a short GPU job or even a login-node-adjacent Ollama session elsewhere.

Metrics (denominators = genes named in answers): unsupported-assertion rate (named genes absent from the replayed evidence), citation compliance (references that resolve to the evidence log), dispute-reporting compliance (disputed ledger pairs mentioned as disputed), and the false-premise probe under the improved manual rubric of A3. Report counts, not percentages, at this n.

Status: requires ~30 inference calls (one modest job). Runner sketch: load cached JSONL, rebuild the three prompt variants from stored fields, call the local model. Not run in this phase because it needs a GPU allocation; all inputs are already on disk.

### B2. Masked-association recovery (controlled recovery task)

Question (RQ3): can the system recover associations through literature when they are removed from its curated graph?

Design: `make_masked_recovery.py` (this phase) selects N well-curated gene–drug pairs (clinicalVariants level ≤ 2B, e.g. SLC28A3–anthracyclines, TPMT–mercaptopurine), writes masked copies of `clinicalVariants.tsv` and `relationships.tsv` with those rows removed, and emits the question list. Run the phase-13 configuration with `AMG_KB_CLINVAR`/`AMG_KB_REL` pointing at the masked tables (already supported by `AMG-with-KG.py`; no code change needed). Success = the masked pair appears in the ledger flagged `uncurated_literature_claim` with a resolving citation; compare against ordinary RAG on the same questions. This measures **association recovery**, explicitly not biological novelty. Requires internet-enabled retrieval and one GPU job; not run in this phase.

### B3. Digest extraction-fidelity audit

Motivated by the SLCO1B1 attribution error (A-audit row 8). Sample ~30 digested paper records across phases; check by reading: does the paper concern the claimed drug, does it support the claimed gene list, is the endpoint recorded correctly, is the study type right. Manual, ~2–3 hours, no compute. Yields the error rate that Section "extraction limits" of the draft currently states qualitatively.

### B4. Contradiction-flag precision repair *(code change proposal)*

The 0.47 precision in A1 suggests two cheap fixes: require at least one non-dependent literature source before raising `curated_vs_literature`, and require both sides of `literature_internal` to be clinical-tier (mirroring the phase-13 comparability rule inside the *ledger* flags, which currently pre-date it). Re-validate on the same 72-pair benchmark (pure post-processing over cached claims — no inference). Provided as a proposal; not implemented, to keep the audited numbers attached to the code that produced them.
