#!/bin/bash
# Phase 15 -- EDGE QUEUE + TYPED-PATH DISCOVERY + SEARCH ROUNDS (docs/PLAN.md).
#
# Phase 13 searched once from a flat list of graph edges and never reacted to what the
# ledger or the cards found. Phase 15 keeps phase 13's retrieval, digestion, ledger and
# contradiction layer, and adds:
#   * every candidate gene-drug(-outcome) relation is an EDGE with a status
#     (untested / confirmed / refuted / disputed / insufficient) and a provenance
#   * typed short paths over the global ClinPGx graph propose edges the tables lack
#     (A: gene linked to the ADR outcome; B: gene-gene neighbour of a curated gene,
#      hub-penalised; C: gene curated for the drug's MeSH class, e.g. platinum compounds)
#   * AMG_SEARCH_ROUNDS targeted rounds: each spends AMG_QUERY_BUDGET queries where
#     uncertainty x prior is highest (a third reserved for untested edges), digests the new
#     papers, rebuilds ledger + cards, writes literature edges back into the graph, and stops
#     early when a round reads no cohort-or-better paper
#   * disagreement cards generate the next round's queries (INSUFFICIENT -> meta-analysis /
#     review / cohort filter; CONTEXT-DEPENDENT -> the separating axis value; ...)
#   * step-0 fixes from the audit: evidence grouped by gene + drug + OUTCOME, the drug taken
#     from the paper (off-drug papers excluded), MeSH drug classes in curated matching,
#     expression / protein-biomarker evidence weighted half, PubMed publication types
#     cross-check the study type, retracted papers dropped, candidates not labelled disputed
#
# Runs on either input:
#   sbatch run_adr_phase15_alliance.bash
#   sbatch --export=ALL,ADR_INPUT=.../masked_questions.jsonl,ADR_TAG=maskrec,\
#          AMG_KB_CLINVAR=...,AMG_KB_REL=... run_adr_phase15_alliance.bash     (E1 masked recovery)
#
# Time: phase 13 fit in 2:30; the extra rounds read up to AMG_DIGEST_MAX_PAPERS new papers
# each, so allow ~1.6x.

#SBATCH --job-name=amg-adr15
#SBATCH --account=def-ester_gpu
#SBATCH --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_adr15_%j.out

module load StdEnv/2023
module load python/3.11.5
module load arrow/17.0.0

cd "$SLURM_SUBMIT_DIR" || exit 1
source .venv/bin/activate

# Model caches live OUTSIDE the repo (keeps the editor/git fast); override AMG_MODELS_DIR to relocate.
export AMG_MODELS_DIR="${AMG_MODELS_DIR:-$(dirname "$SLURM_SUBMIT_DIR")/AMG-RAG-models}"
export HF_HOME="$AMG_MODELS_DIR/hf_cache"
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

if ! curl -sf --max-time 20 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi" >/dev/null; then
  echo "INTERNET CHECK: NCBI NOT reachable -- phase 15 is a literature phase; aborting."
  exit 1
fi
echo "INTERNET CHECK: NCBI reachable."

export OLLAMA_PORT=$(( 11000 + (SLURM_JOB_ID % 4000) ))
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_KEEP_ALIVE=-1
# Paper paragraphs need far more room than the 4096-token default.
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-16384}"
export OLLAMA_NOPRUNE=1
export PATH="$SLURM_SUBMIT_DIR/bin:$PATH"
export LD_LIBRARY_PATH="$SLURM_SUBMIT_DIR/lib/ollama:${LD_LIBRARY_PATH:-}"
export LLM_MODEL="${LLM_MODEL:-qwen2.5:14b}"

command -v ollama >/dev/null || { echo "ERROR: ollama binary missing; run setup_ollama.bash first."; exit 1; }
echo "Starting local ollama serve (GPU: ${CUDA_VISIBLE_DEVICES:-none}) ..."
ollama serve > "ollama_${SLURM_JOB_ID}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill $OLLAMA_PID 2>/dev/null || true' EXIT
for i in $(seq 1 90); do curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null && break; sleep 2; done
ollama run "$LLM_MODEL" "ready" >/dev/null 2>&1 || true

export LLM_BASE_URL="http://127.0.0.1:${OLLAMA_PORT}/v1"
export LLM_EXTRA_HEADERS=""
export AMG_ANSWER_STYLE=adr
export AMG_USE_EXTERNAL=0
# --- phase 13 stack ---
export AMG_KB_SOURCE=pharmgkb+pubmed_combo
export AMG_COMBO_MAX_QUERIES="${AMG_COMBO_MAX_QUERIES:-4}"
export AMG_OPEN_PER_PHRASE="${AMG_OPEN_PER_PHRASE:-2}"
export UNPAYWALL_EMAIL="${UNPAYWALL_EMAIL:?set UNPAYWALL_EMAIL to a contact address (export it or pass via --export)}"
export AMG_PAPER_DIGEST=1
export AMG_EVIDENCE_LEDGER=1
export AMG_CONTRADICTION_LAYER=1
export AMG_PUBMED_FULLTEXT=1
export AMG_FULLTEXT_MAX_CHARS="${AMG_FULLTEXT_MAX_CHARS:-3000}"
export AMG_DIGEST_MAX_PAPERS="${AMG_DIGEST_MAX_PAPERS:-6}"
export AMG_DIGEST_BATCH_CHARS="${AMG_DIGEST_BATCH_CHARS:-2400}"
export AMG_DIGEST_MAX_BATCHES="${AMG_DIGEST_MAX_BATCHES:-6}"
# --- phase 15 ---
export AMG_PATH_DISCOVERY="${AMG_PATH_DISCOVERY:-1}"
export AMG_PATH_MAX_CANDIDATES="${AMG_PATH_MAX_CANDIDATES:-10}"
export AMG_SEARCH_ROUNDS="${AMG_SEARCH_ROUNDS:-2}"
export AMG_QUERY_BUDGET="${AMG_QUERY_BUDGET:-6}"
export AMG_FOLLOWUP_SEARCH="${AMG_FOLLOWUP_SEARCH:-1}"
export AMG_MESH_ONLINE="${AMG_MESH_ONLINE:-1}"     # dataset/mesh_cache.json is read first

ADR_INPUT="${ADR_INPUT:-$SLURM_SUBMIT_DIR/dataset/PharmGKB/adr_clinical.jsonl}"
ADR_TAG="${ADR_TAG:-adrclin}"
export GENMED_INPUT="$ADR_INPUT"
export GENMED_N="${GENMED_N:-$(wc -l < "$ADR_INPUT")}"
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

date
echo "=========================================================="
echo "PHASE 15  --  edge queue + typed-path discovery + ${AMG_SEARCH_ROUNDS} search round(s)"
echo "              budget ${AMG_QUERY_BUDGET}/round, follow-ups=${AMG_FOLLOWUP_SEARCH}, paths=${AMG_PATH_DISCOVERY}"
echo "=========================================================="
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase15_loop.jsonl"
python -u run_genmedgpt.py

kill $OLLAMA_PID 2>/dev/null || true
date
