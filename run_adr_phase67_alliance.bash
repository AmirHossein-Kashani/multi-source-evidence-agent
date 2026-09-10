#!/bin/bash
# Phases 6 & 7 -- OPEN literature search, not limited to ClinPGx citations.
#
# Phases 4/5 could only read the papers ClinPGx already cites for a gene-drug pair.
# Phases 6/7 lift that restriction: an LLM that has seen the question AND the evidence /
# knowledge-graph content retrieved so far chooses the search topics, each topic is searched
# separately on PubMed, and anything relevant may come back -- including recent work that
# post-dates the ClinPGx curation.
#
#   PHASE 6  AMG_KB_SOURCE=pharmgkb+pubmed_open                        abstracts only
#   PHASE 7  AMG_KB_SOURCE=pharmgkb+pubmed_open AMG_PUBMED_FULLTEXT=1  + PMC full text
#
# ClinPGx grounding stays ON in both, so these are strictly "phase 3 + free literature".
# Previous phases are NOT re-run: separate output files, and the runner skips finished ids.

#SBATCH --job-name=amg-adr67
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
#SBATCH --output=amg_adr67_%j.out

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
  echo "INTERNET CHECK: NCBI NOT reachable -- phases 6/7 are literature phases; aborting."
  exit 1
fi
echo "INTERNET CHECK: NCBI reachable."

export OLLAMA_PORT=$(( 11000 + (SLURM_JOB_ID % 4000) ))
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_KEEP_ALIVE=-1
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
export AMG_KB_SOURCE=pharmgkb+pubmed_open
export AMG_MAX_SEARCH_PHRASES="${AMG_MAX_SEARCH_PHRASES:-3}"
export AMG_OPEN_PER_PHRASE="${AMG_OPEN_PER_PHRASE:-2}"

ADR_INPUT="${ADR_INPUT:-$SLURM_SUBMIT_DIR/dataset/PharmGKB/adr_clinical.jsonl}"
ADR_TAG="${ADR_TAG:-adrclin}"
export GENMED_INPUT="$ADR_INPUT"
export GENMED_N="${GENMED_N:-$(wc -l < "$ADR_INPUT")}"
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

date
echo "=========================================================="
echo "PHASE 6  --  open LLM-directed PubMed search (abstracts)"
echo "=========================================================="
export AMG_PUBMED_FULLTEXT=0
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase6_open_abstracts.jsonl"
python run_genmedgpt.py

echo "=========================================================="
echo "PHASE 7  --  open search + PMC full text"
echo "=========================================================="
export AMG_PUBMED_FULLTEXT=1
export AMG_FULLTEXT_MAX_CHARS="${AMG_FULLTEXT_MAX_CHARS:-3000}"
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase7_open_fulltext.jsonl"
python run_genmedgpt.py

kill $OLLAMA_PID 2>/dev/null || true
date
