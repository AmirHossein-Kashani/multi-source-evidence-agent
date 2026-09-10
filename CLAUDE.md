# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

AMG-RAG (EMNLP 2025 Findings paper, arXiv:2502.13010) builds a per-question medical knowledge graph with an LLM and reasons over it to answer medical QA. The original code targets multiple-choice benchmarks (MedQA/MedMCQA). The current work adapts it to the **open-ended GenMedGPT-5k dataset** (patient question → free-text doctor reply) and runs experiments on the Nibi cluster (Digital Research Alliance of Canada) with a remote Ollama LLM.

## Commands

```bash
source .venv/bin/activate                      # local venv (on cluster: module load StdEnv/2023 python/3.11.5 arrow/17.0.0 first)

python convert_genmedgpt.py                    # raw HF json -> dataset/GenMedGPT-5k/genmedgpt5k.jsonl (5452 items)
python convert_genmedgpt.py --limit 5          # small *_debug.jsonl for smoke tests

python test_llm.py                             # quick connectivity check against the LLM endpoint

python run_genmedgpt.py --n 50 --offset 0      # batch inference -> results/genmedgpt5k_results.jsonl
sbatch run_genmedgpt_alliance.bash             # same thing as a SLURM job (CPU-only)
sbatch --export=ALL,GENMED_N=500,GENMED_OFFSET=50 run_genmedgpt_alliance.bash   # override slice

python eval_genmedgpt.py                       # BERTScore (roberta-large, rescaled) -> results/genmedgpt5k_scores.csv
python eval_genmedgpt.py --judge               # + LLM-as-judge (weak llama3.1:8b approximation of the paper's GPT-4 ranking)
```

There are no tests or linters configured.

## LLM routing (env vars, read in `AMG_RAG_System.__init__`)

- `LLM_BASE_URL` — if set, ALL LLM calls go through `ChatOpenAI` to this OpenAI-compatible endpoint. In practice this is the user's own Ollama server exposed through an **ngrok free tunnel** (URL hardcoded in `run_genmedgpt_alliance.bash` and as the default in `eval_genmedgpt.py` — update both if the tunnel URL changes).
- `LLM_MODEL` (llama3.1:8b), `LLM_EXTRA_HEADERS` (ngrok needs `{"ngrok-skip-browser-warning": "true"}`).
- `AMG_USE_EXTERNAL=0` — offline mode: no PubMed, no Wikipedia, no Chroma/embeddings; the KG is built from the question text alone. The GenMedGPT experiments run this way, so results are a system-level ablation of the paper, not a reproduction.
- `.env` holds `OPENAI_API_KEY=ollama` (any non-empty string satisfies the client) and optional `pubmed_api`.

The ngrok tunnel dies when the host machine sleeps (`ERR_NGROK_3200`). The runner aborts after 3 consecutive failures for this reason — don't remove that guard.

## Architecture

`AMG-with-KG.py` is the whole system. The filename contains hyphens, so it **cannot be imported normally** — load it via `importlib.util.spec_from_file_location` (see `load_amg_module()` in `run_genmedgpt.py`).

Pipeline per question: entity extraction (LLM, relevance-scored) → bidirectional relation extraction between entity pairs (LLM) → optional external evidence (PubMed/Wikipedia) → entity summarization → chain-of-thought over graph paths → answer. All stages are LangChain `PromptTemplate | llm | StructuredOutputParser` chains built in `_setup_chains()`. The graph lives in `MedicalKnowledgeGraph` (networkx DiGraph + confidence-scored entities/relations).

Two entry points on `AMG_RAG_System`:
- `answer_question(question_data)` — original MCQ path (question + options → letter answer).
- `answer_open_question(question_data)` — open-ended path added for GenMedGPT-5k (question → free-text reply via `reason_open_with_graph`). The batch runner resets `system.kg` to a fresh graph before each question so entities don't bleed across items.

`Simple_AMG_RAG.py` and `create_VDB.py` are from the original paper repo and are not part of the GenMedGPT flow.

## GenMedGPT result-file contract

- `run_genmedgpt.py` appends JSONL and is resume-safe: on start it collects ids with a real answer and skips them; **failed items are never written**, so a re-run retries them.
- `"Unable to generate a reliable answer for this question."` is the salvage-fallback sentinel from `AMG_RAG_System._salvage_open_answer` meaning every LLM call failed. It is duplicated as `FALLBACK_ANSWER` in `run_genmedgpt.py` and `eval_genmedgpt.py` — keep all three in sync.
- `eval_genmedgpt.py` drops empty/fallback rows and dedups by id (last row wins) before scoring.
- `results/genmedgpt5k_results.bad.jsonl` is quarantined junk from a run where the tunnel died mid-batch; ignore it.

## PharmGKB / ADR experiment (second dataset, self-hosted Qwen)

A second open-ended experiment reuses the GenMedGPT pipeline on the **PharmGKB / ADR** pharmacogenomics dataset (Google-Drive `ADR_DataSet.zip`, unzipped to `dataset/ADR_DataSet/`). These tables are a knowledge base, not a Q&A set, so we synthesize QA pairs (**Framing 1 / text dataset**).

```bash
python convert_pharmgkb.py                 # var_drug_ann.tsv -> dataset/PharmGKB/pharmgkb.jsonl (12,173 items)
python convert_pharmgkb.py --source both   # + var_pheno_ann.tsv
python convert_pharmgkb.py --limit 5       # pharmgkb_debug.jsonl smoke test

bash  setup_ollama.bash                     # LOGIN node: install rootless Ollama + pull qwen2.5:14b into ../AMG-RAG-models/ollama
sbatch run_pharmgkb_alliance.bash           # GPU job: serve Qwen locally + run batch -> results/pharmgkb_results.jsonl
```

- Converter templates a question from gene/variant/drug and uses the curated `Sentence` column as the gold reference (no answer leakage — the effect/direction lives only in the reference). Output schema matches `run_genmedgpt.py` (`{id, question, reference, ...}`), so the same runner and `eval_genmedgpt.py` (BERTScore) are reused.
- `AMG_ANSWER_STYLE=pgx` (env, read in `__init__`) switches `reason_open_with_graph` to `open_pgx_answer_chain` — a terse factual pharmacogenomics reply instead of the empathetic GenMedGPT doctor reply. Default `doctor` preserves the GenMedGPT behaviour.

### Retrieval phases, provenance, and full text (phases 3-5)

The ADR/ClinPGx experiment is organized as retrieval "phases", selected via env vars read in `AMG_RAG_System.__init__` and routed through `_evidence_search_detailed` (the single retrieval seam):

- **Phase 3** (`AMG_KB_SOURCE=pharmgkb`, aka setup3): offline ClinPGx tables only (`pgx_kb.py`). Runs as condition C of `run_adr_alliance.bash`.
- **Phase 4** (`AMG_KB_SOURCE=pharmgkb+pubmed`): ClinPGx first, then a **PubMed check** — the exact PMIDs `relationships.tsv` cites for the retrieved gene-drug pairs are fetched from PubMed (`via: clinpgx_citation`), topped up with a live esearch on the query. Forces PubMed on regardless of `AMG_USE_EXTERNAL`; needs internet (NCBI E-utilities).
- **Phase 5** (add `AMG_PUBMED_FULLTEXT=1`): PubMed abstracts used at the *reasoning* stage are upgraded to **PMC full text** (elink PMID→PMCID → JATS XML `<body>`; open-access PDF via `pypdf` as fallback — pypdf is optional, the PDF path silently skips if it's missing). `AMG_FULLTEXT_MAX_CHARS` (default 3000) caps how much of each article enters the prompt — mind the serving model's context window (Ollama default num_ctx is small).
- `sbatch run_adr_phase45_alliance.bash` runs phases 4 then 5 on the ADR discovery set (aborts cleanly if NCBI is unreachable from the compute node).

**Provenance**: every retrieval (ClinPGx row, PubMed abstract, PMC full text, Wikipedia summary) is logged to `AMG_RAG_System.evidence_log` with a stage tag (`question_context`, `entity:<name>`, `reasoning`) and a stable ref (`PMID:xxx`, `PMID:xxx/PMCxxx`, `ClinPGx:GENE/variant:Llevel`, `Wikipedia:title`). Both entry points attach `references` (deduped citations via `collect_references()`) and `evidence_log` to the result, and `run_genmedgpt.py` persists both fields in the results JSONL. The log resets per question in `answer_question`/`answer_open_question`. `PubMedSearcher` caches per-PMID (abstract + full text) and rate-limits NCBI calls to ~3/s.

### Self-hosted LLM (replaces the ngrok tunnel)

The PharmGKB job runs its own **Ollama server locally on the allocated GPU** — no ngrok, no remote host. `LLM_BASE_URL=http://127.0.0.1:11434/v1` points the existing `ChatOpenAI` path at it, so no change to `AMG-with-KG.py`'s routing.

- **Selected model: `qwen2.5:14b`** (Qwen2.5-14B-Instruct, Ollama Q4_K_M ≈ 9 GB). Override `LLM_MODEL=qwen2.5:14b-instruct-q8_0` (≈16 GB) to use more of the slice, or `qwen2.5:32b` on a bigger GPU.
- **GPU: one H100 MIG `2g.20gb` slice (~20 GB VRAM)** — Nibi's closest option to the 22 GB target. `--gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1`, account `def-ester_gpu`. For 32B use the `3g.40gb` (40 GB) slice.
- Compute nodes have **no internet**, so `setup_ollama.bash` must run on a login node first to install `./bin/ollama` (+ `./lib/ollama`) and pre-pull the model into `$AMG_MODELS_DIR/ollama/models`. The GPU job then serves it fully offline.
- vLLM was rejected: the Alliance wheel is cp38-tagged and its install pulls modules (opencv) that fail to build in the py3.11 venv.

## Cluster notes

- SLURM account `def-ester_cpu` for CPU-only GenMedGPT jobs (LLM remote); `def-ester_gpu` for the PharmGKB GPU job (LLM local). Job logs land in `amg_genmed_<jobid>.out` / `amg_pgx_<jobid>.out`.
- **Model caches live outside the repo** in `$AMG_MODELS_DIR` (default: sibling dir `../AMG-RAG-models`, i.e. `/scratch/kashi77/AMG-RAG-models`): `ollama/` (Ollama store) and `hf_cache/` (`HF_HOME`). They were moved out so VS Code / git never walk multi-GB model blobs. Every job script and `setup_ollama.bash` derive both paths from `AMG_MODELS_DIR`.
- `HF_HOME` points at `$AMG_MODELS_DIR/hf_cache/` — BERTScore's roberta-large and any embedding models cache there.
- Do all downloads (`convert_genmedgpt.py`, `setup_ollama.bash`) from the login node.
