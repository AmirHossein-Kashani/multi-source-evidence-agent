#!/bin/bash
# AMG-RAG on the Nibi (Digital Research Alliance) cluster.
#
# The LLM itself runs REMOTELY on a custom Ollama server reached over an ngrok
# tunnel (OpenAI-compatible /v1 endpoint), so this job needs NO GPU. The only
# local work is sentence-transformers embeddings + Chroma + PubMed/Wikipedia
# HTTP calls, which are light CPU tasks. Hence a CPU allocation.
#
# The SBATCH directives must appear before any executable line in this script.

#SBATCH --job-name=amg-rag
#SBATCH --account=def-ester_cpu   # CPU allocation on Nibi (use def-ester_gpu only if requesting a GPU)
#SBATCH --time=00:30:00           # start short to test; raise for larger dataset runs. Format D-H:M:S
#SBATCH --mem=16G                 # total CPU memory
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4         # threads for torch / embeddings
#SBATCH --mail-user=danielkordm@gmail.com
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_%j.out

# ---- Environment ----------------------------------------------------------
module load StdEnv/2023
module load python/3.11.5
module load arrow/17.0.0

cd "$SLURM_SUBMIT_DIR" || exit 1
source .venv/bin/activate

# Keep HF model cache inside the project (persists between runs, avoids $HOME quota)
export HF_HOME="$SLURM_SUBMIT_DIR/.hf_cache"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# ---- Custom LLM endpoint (Ollama, OpenAI-compatible) ----------------------
# Route every LangChain LLM call to the remote Ollama server.
export LLM_BASE_URL="https://widen-oops-sandfish.ngrok-free.dev/v1"
export LLM_MODEL="llama3.1:8b"
export LLM_EXTRA_HEADERS='{"ngrok-skip-browser-warning": "true"}'

date
echo "Using LLM endpoint: $LLM_BASE_URL  model=$LLM_MODEL"

python AMG-with-KG.py

deactivate

# print completion time
date
