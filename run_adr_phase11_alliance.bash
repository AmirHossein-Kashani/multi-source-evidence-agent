#!/bin/bash
# Phase 11 -- EVIDENCE LEDGER: per-gene confidence + contradictions between sources.
#
# Builds on phase 10 (free-arity model-authored queries + per-paper paragraph digests) and adds
# the research payload: every claim is aggregated per gene-drug pair, disagreement between the
# curated ClinPGx tables and the retrieved literature is flagged explicitly, and a confidence is
# computed BY RULE in evidence_ledger.py (never emitted by the model, so it can be calibrated).
# Recall is the objective: low-confidence genes are reported as low-confidence, not dropped.
#
# Runs on either input:
#   sbatch --export=ALL,ADR_INPUT=.../adr_clinical.jsonl,ADR_TAG=adrclin        run_adr_phase11_alliance.bash
#   sbatch --time=05:00:00 --export=ALL,ADR_INPUT=.../pgx_confidence_bench.jsonl,ADR_TAG=bench,\
#          AMG_DIGEST_MAX_PAPERS=3,AMG_DIGEST_MAX_BATCHES=3 run_adr_phase11_alliance.bash
#
# --- inherited from phase 10 ---
# FREE search: the model controls both the arity and the phrasing.
#
# Phases 8/9 forced every query to combine >=2 graph-related terms, and the CODE assembled the
# query string by joining them with AND. Phase 10 removes both constraints:
#   * the model may search ONE concept alone, or combine two, three or more -- its choice
#   * the model writes the PubMed query string itself; quoted phrases, AND/OR and field tags
#     such as [tiab] are passed through verbatim
# Phase 10 also replaces "paste raw article text into the prompt" with a READ-then-DECIDE
# stage: every retrieved paper is read paragraph by paragraph, the model keeps the paragraphs
# that bear on the question (each citable as PMID:x/PMCy#pN), and the final answer is made from
# the curated ClinPGx evidence PLUS those digests -- not from raw text and not from the
# knowledge-graph context alone (which is all the answer chain saw in phases 3-9).
#
#   PHASE 10  AMG_KB_SOURCE=pharmgkb+pubmed_free  AMG_PUBMED_FULLTEXT=1
#
# ClinPGx grounding stays ON. Previous phases are NOT re-run.

#SBATCH --job-name=amg-adr11
#SBATCH --account=def-ester_gpu
#SBATCH --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1
#SBATCH --time=02:30:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-user=danielkordm@gmail.com
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_adr11_%j.out

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
  echo "INTERNET CHECK: NCBI NOT reachable -- phase 10 is a literature phase; aborting."
  exit 1
fi
echo "INTERNET CHECK: NCBI reachable."

export OLLAMA_PORT=$(( 11000 + (SLURM_JOB_ID % 4000) ))
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_KEEP_ALIVE=-1
# The 4096-token default truncated prompts in the first attempt (37 truncation events in the
# server log). Reading paper paragraphs needs far more room.
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
export AMG_KB_SOURCE=pharmgkb+pubmed_free
export AMG_COMBO_MAX_QUERIES="${AMG_COMBO_MAX_QUERIES:-4}"
export AMG_OPEN_PER_PHRASE="${AMG_OPEN_PER_PHRASE:-2}"
# Paper-digest stage: read each retrieved paper paragraph by paragraph, keep the parts that
# answer the question, and decide from ClinPGx + those digests.
# Open-access full-text routes: PMC -> Europe PMC -> Unpaywall(repository copy) -> PMC PDF.
# Unpaywall needs only a contact email; it is not a subscription credential.
export UNPAYWALL_EMAIL="${UNPAYWALL_EMAIL:-amkkashani@gmail.com}"
export AMG_PAPER_DIGEST=1
export AMG_EVIDENCE_LEDGER=1
export AMG_DIGEST_MAX_PAPERS="${AMG_DIGEST_MAX_PAPERS:-6}"
export AMG_DIGEST_BATCH_CHARS="${AMG_DIGEST_BATCH_CHARS:-2400}"
export AMG_DIGEST_MAX_BATCHES="${AMG_DIGEST_MAX_BATCHES:-6}"

ADR_INPUT="${ADR_INPUT:-$SLURM_SUBMIT_DIR/dataset/PharmGKB/adr_clinical.jsonl}"
ADR_TAG="${ADR_TAG:-adrclin}"
export GENMED_INPUT="$ADR_INPUT"
export GENMED_N="${GENMED_N:-$(wc -l < "$ADR_INPUT")}"
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

date
echo "=========================================================="
echo "PHASE 11  --  model-authored queries + per-paper reading"
echo "              + evidence ledger: per-gene confidence and source contradictions"
echo "=========================================================="
export AMG_PUBMED_FULLTEXT=1
export AMG_FULLTEXT_MAX_CHARS="${AMG_FULLTEXT_MAX_CHARS:-3000}"
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase11_ledger.jsonl"
python -u run_genmedgpt.py

kill $OLLAMA_PID 2>/dev/null || true
date
