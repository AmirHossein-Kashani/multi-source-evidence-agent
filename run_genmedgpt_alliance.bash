#!/bin/bash
# AMG-RAG on GenMedGPT-5k (open-ended) on the Nibi cluster.
#
# The LLM runs REMOTELY on a custom Ollama server via an ngrok tunnel, so this job is
# CPU-only. Local work is just sentence-transformers embeddings + PubMed/Wikipedia HTTP.
# Evaluation (BERTScore) is run as a SEPARATE short job, not here.

#SBATCH --job-name=amg-genmed
#SBATCH --account=def-ester_cpu
#SBATCH --time=03:00:00           # generous for a 50-item batch (~30 remote LLM calls/item)
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mail-user=danielkordm@gmail.com
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_genmed_%j.out

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

# ---- Custom LLM endpoint (Ollama, OpenAI-compatible) ----------------------
export LLM_BASE_URL="https://widen-oops-sandfish.ngrok-free.dev/v1"
export LLM_MODEL="llama3.1:8b"
export LLM_EXTRA_HEADERS='{"ngrok-skip-browser-warning": "true"}'

# Offline: use ONLY the provided data -- no PubMed, no Wikipedia, no vector store.
export AMG_USE_EXTERNAL=0

# ---- Dataset slice --------------------------------------------------------
export GENMED_N="${GENMED_N:-50}"        # override at submit time: sbatch --export=ALL,GENMED_N=50,GENMED_OFFSET=0 ...
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

date
echo "GenMedGPT-5k run: N=$GENMED_N OFFSET=$GENMED_OFFSET  LLM=$LLM_MODEL @ $LLM_BASE_URL"

python run_genmedgpt.py

deactivate
date
