#!/bin/bash
# Three-way retrieval comparison on ONE question set, in ONE job.
#
# Phases 3/4/5 differ ONLY by environment variables -- identical code, identical entry
# point (run_genmedgpt.py -> AMG_RAG_System.answer_open_question), identical model,
# identical input. That is the whole point of this script: the only independent variable
# is the retrieval configuration.
#
#   PHASE 3  AMG_KB_SOURCE=pharmgkb          offline ClinPGx tables only
#   PHASE 4  AMG_KB_SOURCE=pharmgkb+pubmed   + PubMed check of the PMIDs ClinPGx cites
#   PHASE 5  AMG_PUBMED_FULLTEXT=1           + PMC full text for reasoning-stage abstracts
#
# run_genmedgpt.py is resume-safe (already-answered ids are skipped), so re-running this
# after a partial run only fills the gaps. Phases 4/5 need internet; phase 3 does not, so
# the job still produces phase 3 if NCBI is unreachable.

#SBATCH --job-name=amg-adr345
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
#SBATCH --output=amg_adr345_%j.out

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

# ---- Local Ollama server (per-job port) ------------------------------------
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

# ---- Constants held fixed across all three phases --------------------------
export LLM_BASE_URL="http://127.0.0.1:${OLLAMA_PORT}/v1"
export LLM_EXTRA_HEADERS=""
export AMG_ANSWER_STYLE=adr
ADR_INPUT="${ADR_INPUT:-$SLURM_SUBMIT_DIR/dataset/PharmGKB/adr_clinical.jsonl}"
ADR_TAG="${ADR_TAG:-adrclin}"
export GENMED_INPUT="$ADR_INPUT"
export GENMED_N="${GENMED_N:-$(wc -l < "$ADR_INPUT")}"
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

echo "Input: $ADR_INPUT ($GENMED_N items) | model: $LLM_MODEL"
date

# ============================ PHASE 3 ========================================
echo "=========================================================="
echo "PHASE 3  --  ClinPGx tables only (offline)"
echo "=========================================================="
export AMG_KB_SOURCE=pharmgkb
export AMG_USE_EXTERNAL=0
export AMG_PUBMED_FULLTEXT=0
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase3_clinpgx.jsonl"
python run_genmedgpt.py

# Phases 4 and 5 need NCBI. Phase 3 above is already safely on disk.
if ! curl -sf --max-time 20 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi" >/dev/null; then
  echo "INTERNET CHECK: NCBI NOT reachable -> phases 4/5 SKIPPED (phase 3 results kept)."
  kill $OLLAMA_PID 2>/dev/null || true
  date
  exit 0
fi
echo "INTERNET CHECK: NCBI reachable."

# ============================ PHASE 4 ========================================
echo "=========================================================="
echo "PHASE 4  --  ClinPGx + PubMed citation check"
echo "=========================================================="
export AMG_KB_SOURCE=pharmgkb+pubmed
export AMG_PUBMED_FULLTEXT=0
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase4_clinpgx_pubmed.jsonl"
python run_genmedgpt.py

# ============================ PHASE 5 ========================================
echo "=========================================================="
echo "PHASE 5  --  + PMC full text"
echo "=========================================================="
export AMG_PUBMED_FULLTEXT=1
export AMG_FULLTEXT_MAX_CHARS="${AMG_FULLTEXT_MAX_CHARS:-3000}"
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase5_fulltext.jsonl"
python run_genmedgpt.py

kill $OLLAMA_PID 2>/dev/null || true
date
echo "Compare with:  python make_adr_phase45_report.py --tag $ADR_TAG"
