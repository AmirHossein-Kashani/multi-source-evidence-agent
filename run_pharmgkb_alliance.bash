#!/bin/bash
# AMG-RAG on the PharmGKB/ADR dataset (open-ended, Framing 1) on the Nibi cluster.
#
# Self-hosted LLM: Qwen served by a LOCAL Ollama process on the allocated GPU -- NO ngrok,
# no remote host. Server + inference run in this one job. Run setup_ollama.bash on a login
# node FIRST to install the binary and cache the model (compute nodes have no internet).
#
# GPU: one H100 MIG 2g.20gb slice (~20 GB VRAM, the closest Nibi option to the 22 GB target).
#      To go bigger: use --gres=gpu:nvidia_h100_80gb_hbm3_3g.40gb:1 and LLM_MODEL=qwen2.5:32b.

#SBATCH --job-name=amg-pgx
#SBATCH --account=def-ester_gpu
#SBATCH --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1
#SBATCH --time=03:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-user=danielkordm@gmail.com
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_pgx_%j.out

# ---- Environment ----------------------------------------------------------
module load StdEnv/2023
module load python/3.11.5
module load arrow/17.0.0

cd "$SLURM_SUBMIT_DIR" || exit 1
source .venv/bin/activate

# Model caches live OUTSIDE the repo (keeps the editor/git fast); override AMG_MODELS_DIR to relocate.
export AMG_MODELS_DIR="${AMG_MODELS_DIR:-$(dirname "$SLURM_SUBMIT_DIR")/AMG-RAG-models}"
export HF_HOME="$AMG_MODELS_DIR/hf_cache"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# ---- Local Ollama server (OpenAI-compatible /v1, offline) ------------------
# MIG slices share a physical node, so bind a per-job loopback port to avoid clashing with
# another user's ollama on the same node.
export OLLAMA_PORT=$(( 11000 + (SLURM_JOB_ID % 4000) ))
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_KEEP_ALIVE=-1          # keep the model resident on the GPU for the whole run
export OLLAMA_NOPRUNE=1
export PATH="$SLURM_SUBMIT_DIR/bin:$PATH"
export LD_LIBRARY_PATH="$SLURM_SUBMIT_DIR/lib/ollama:${LD_LIBRARY_PATH:-}"

export LLM_MODEL="${LLM_MODEL:-qwen2.5:14b}"

command -v ollama >/dev/null || { echo "ERROR: ollama binary missing. Run setup_ollama.bash on a login node first."; exit 1; }

echo "Starting local ollama serve (GPU: ${CUDA_VISIBLE_DEVICES:-none}) ..."
ollama serve > "ollama_${SLURM_JOB_ID}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill $OLLAMA_PID 2>/dev/null || true' EXIT

for i in $(seq 1 90); do
  curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null && break
  sleep 2
done

ollama list | grep -q "${LLM_MODEL%%:*}" || { echo "ERROR: model '$LLM_MODEL' not cached. Run setup_ollama.bash on a login node first."; exit 1; }
ollama run "$LLM_MODEL" "ready" >/dev/null 2>&1 || true   # warm-load onto the GPU

# ---- Route AMG-RAG at the local server ------------------------------------
export LLM_BASE_URL="http://127.0.0.1:${OLLAMA_PORT}/v1"
export LLM_EXTRA_HEADERS=""          # no ngrok header needed anymore
export AMG_USE_EXTERNAL=0            # offline: KG built from the question text alone
export AMG_ANSWER_STYLE=pgx          # terse factual pharmacogenomics reply

# ---- Dataset slice --------------------------------------------------------
export GENMED_INPUT="$SLURM_SUBMIT_DIR/dataset/PharmGKB/pharmgkb.jsonl"
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/pharmgkb_results.jsonl"
export GENMED_N="${GENMED_N:-50}"       # sbatch --export=ALL,GENMED_N=500,GENMED_OFFSET=0 ...
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

date
echo "PharmGKB run: N=$GENMED_N OFFSET=$GENMED_OFFSET  LLM=$LLM_MODEL @ $LLM_BASE_URL (local)"

python run_genmedgpt.py

kill $OLLAMA_PID 2>/dev/null || true
date
