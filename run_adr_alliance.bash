#!/bin/bash
# ADR drug-discovery "opinion" run: feed drug->adverse-reaction prompts to AMG-RAG and
# capture its assessment + reasoning + evidence context. Runs the SAME prompts TWICE:
#   (A) current DB only  -> AMG_USE_EXTERNAL=0  -> results/adr_offline.jsonl
#   (B) paper's setup    -> AMG_USE_EXTERNAL=1  (PubMed + Wikipedia) -> results/adr_pubmed.jsonl
# Self-hosted Qwen on the GPU (local Ollama). Condition B needs internet on the compute node;
# the job checks that first and skips B if unreachable (so we never fake a PubMed run).

#SBATCH --job-name=amg-adr
#SBATCH --account=def-ester_gpu
#SBATCH --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1
#SBATCH --time=03:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-user=danielkordm@gmail.com
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_adr_%j.out

module load StdEnv/2023
module load python/3.11.5
module load arrow/17.0.0

cd "$SLURM_SUBMIT_DIR" || exit 1
source .venv/bin/activate

# Model caches live OUTSIDE the repo (keeps the editor/git fast); override AMG_MODELS_DIR to relocate.
export AMG_MODELS_DIR="${AMG_MODELS_DIR:-$(dirname "$SLURM_SUBMIT_DIR")/AMG-RAG-models}"
export HF_HOME="$AMG_MODELS_DIR/hf_cache"
export HF_HUB_OFFLINE=1                 # embedding model is already cached; don't hit the HF hub
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# ---- Local Ollama server (per-job port) -----------------------------------
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

# ---- Common AMG-RAG routing ------------------------------------------------
export LLM_BASE_URL="http://127.0.0.1:${OLLAMA_PORT}/v1"
export LLM_EXTRA_HEADERS=""
export AMG_ANSWER_STYLE=adr
# Parametrizable: sbatch --export=ALL,ADR_INPUT=...,ADR_TAG=... run_adr_alliance.bash
ADR_INPUT="${ADR_INPUT:-$SLURM_SUBMIT_DIR/dataset/PharmGKB/adr_discovery.jsonl}"
ADR_TAG="${ADR_TAG:-adr}"
export GENMED_INPUT="$ADR_INPUT"
export GENMED_N="${GENMED_N:-$(wc -l < "$ADR_INPUT")}"
export GENMED_OFFSET=0

date
# =========================== CONDITION A: offline ===========================
echo "=========================================================="
echo "CONDITION A  --  current DB only (AMG_USE_EXTERNAL=0)"
echo "=========================================================="
export AMG_USE_EXTERNAL=0
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_offline.jsonl"
python run_genmedgpt.py

# =================== CONDITION B: paper setup (PubMed) ======================
echo "=========================================================="
echo "CONDITION B  --  paper setup, PubMed+Wikipedia (AMG_USE_EXTERNAL=1)"
echo "=========================================================="
if curl -sf --max-time 20 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi" >/dev/null; then
  echo "INTERNET CHECK: NCBI reachable from compute node -> running PubMed condition."
  export AMG_USE_EXTERNAL=1
  export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_pubmed.jsonl"
  python run_genmedgpt.py
else
  echo "INTERNET CHECK: NCBI NOT reachable from this compute node -> SKIPPING PubMed condition."
  echo "(Re-run condition B on a node with internet; offline results are still in results/adr_offline.jsonl.)"
fi

# =================== CONDITION C: local ClinPGx grounding ====================
echo "=========================================================="
echo "CONDITION C  --  local ClinPGx tables (AMG_KB_SOURCE=pharmgkb, no network)"
echo "=========================================================="
export AMG_USE_EXTERNAL=0
export AMG_KB_SOURCE=pharmgkb
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_pharmgkb.jsonl"
python run_genmedgpt.py
unset AMG_KB_SOURCE

kill $OLLAMA_PID 2>/dev/null || true
date
