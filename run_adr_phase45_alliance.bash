#!/bin/bash
# ADR phases 4 & 5 on top of the ClinPGx grounding (phase 3 = AMG_KB_SOURCE=pharmgkb):
#   PHASE 4  ClinPGx + PubMed check  -> AMG_KB_SOURCE=pharmgkb+pubmed
#            After each ClinPGx retrieval, fetch the exact PMIDs relationships.tsv cites
#            for the gene-drug pairs (topped up with a live PubMed search). All retrieved
#            evidence is referenced (PMID / ClinPGx level) in the results JSONL
#            (`references` + `evidence_log` fields).
#   PHASE 5  + full text             -> AMG_PUBMED_FULLTEXT=1
#            PubMed abstracts used at the reasoning stage are upgraded to PMC full text
#            (JATS XML; open-access PDF via pypdf as fallback) when available.
# Both phases need internet on the compute node (NCBI E-utilities); the job checks
# reachability first and aborts cleanly if offline, so we never fake a PubMed run.
# Self-hosted Qwen on the GPU (local Ollama), same setup as run_adr_alliance.bash.

#SBATCH --job-name=amg-adr45
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
#SBATCH --output=amg_adr45_%j.out

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

# ---- Internet check (both phases require NCBI) ------------------------------
if ! curl -sf --max-time 20 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi" >/dev/null; then
  echo "INTERNET CHECK: NCBI NOT reachable from this compute node."
  echo "Phases 4/5 need E-utilities access; re-submit on an internet-enabled node."
  exit 1
fi
echo "INTERNET CHECK: NCBI reachable."

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
export AMG_USE_EXTERNAL=0            # PubMed is forced on by pharmgkb+pubmed itself
# Parametrizable: sbatch --export=ALL,ADR_INPUT=...,ADR_TAG=... run_adr_phase45_alliance.bash
ADR_INPUT="${ADR_INPUT:-$SLURM_SUBMIT_DIR/dataset/PharmGKB/adr_discovery.jsonl}"
ADR_TAG="${ADR_TAG:-adr}"
export GENMED_INPUT="$ADR_INPUT"
export GENMED_N="${GENMED_N:-$(wc -l < "$ADR_INPUT")}"
export GENMED_OFFSET="${GENMED_OFFSET:-0}"

date
# ================= PHASE 4: ClinPGx + PubMed check (abstracts) ===============
echo "=========================================================="
echo "PHASE 4  --  ClinPGx + PubMed citation check (AMG_KB_SOURCE=pharmgkb+pubmed)"
echo "=========================================================="
export AMG_KB_SOURCE=pharmgkb+pubmed
export AMG_PUBMED_FULLTEXT=0
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase4_clinpgx_pubmed.jsonl"
python run_genmedgpt.py

# ================= PHASE 5: + PMC full text ==================================
echo "=========================================================="
echo "PHASE 5  --  + full text (AMG_PUBMED_FULLTEXT=1, PMC XML / OA PDF)"
echo "=========================================================="
export AMG_PUBMED_FULLTEXT=1
export AMG_FULLTEXT_MAX_CHARS="${AMG_FULLTEXT_MAX_CHARS:-3000}"
export GENMED_OUTPUT="$SLURM_SUBMIT_DIR/results/${ADR_TAG}_phase5_fulltext.jsonl"
python run_genmedgpt.py

kill $OLLAMA_PID 2>/dev/null || true
date
