#!/bin/bash
# External published baselines, one GPU job per stage (results/benchmarks.md, section 4).
#
#   sbatch --export=ALL,EXT_STAGE=medrag   --time=06:00:00 run_extbase_alliance.bash
#       MedRAG and i-MedRAG (Xiong et al., 2024) with MedCPT over Textbooks + StatPearls, on
#       the PGxQA items and the masked-recovery questions. First use builds the MedCPT
#       index (~425k chunks) on the GPU and caches it under ext_baselines/medrag_corpus.
#   sbatch --export=ALL,EXT_STAGE=paperqa,OLLAMA_NUM_PARALLEL=4 --gres=gpu:h100:1 --mem=64G --time=04:00:00 run_extbase_alliance.bash
#       PaperQA2 (FutureHouse) agent over the shared PubMed abstract corpus. Its evidence
#       summaries run concurrently (hence the parallel slots); a full GPU because the MIG
#       queue was not moving (8 h pending with no start estimate). The runner resumes, so
#       the stage can also be run as a chain of 1-hour jobs, which backfill sooner:
#       sbatch ... --time=01:00:00 --dependency=afterany:<previous job> run_extbase_alliance.bash
#       Add PAPERQA_AGENT=fake for PaperQA2's fixed pipeline (search -> gather -> answer) in
#       place of its LLM tool-selecting agent; results go to results/*_paperqa_fake.jsonl.
#   sbatch --export=ALL,EXT_STAGE=lightrag --time=08:00:00 run_extbase_alliance.bash
#       LightRAG (document-built graph, no curated KG) over the same corpus: index, then query.
#
# All stages serve qwen2.5:14b (and nomic-embed-text for embeddings) through the local Ollama
# server, as the phase scripts do; each baseline's own venv lives in /scratch/kashi77/ext_baselines.

#SBATCH --job-name=amg-extbase
#SBATCH --account=def-ester_gpu
#SBATCH --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1
#SBATCH --time=06:00:00
#SBATCH --mem=48G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_extbase_%j.out

set -u
STAGE="${EXT_STAGE:?set EXT_STAGE to medrag | imedrag | paperqa | lightrag}"
EXT=/scratch/kashi77/ext_baselines
module load StdEnv/2023
module load python/3.11.5
module load arrow/17.0.0
cd "$SLURM_SUBMIT_DIR" || exit 1

export AMG_MODELS_DIR="${AMG_MODELS_DIR:-$(dirname "$SLURM_SUBMIT_DIR")/AMG-RAG-models}"
export HF_HOME="$AMG_MODELS_DIR/hf_cache"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

export OLLAMA_PORT=$(( 11000 + (SLURM_JOB_ID % 4000) ))
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_KEEP_ALIVE=-1
# MedRAG packs up to 15k tokens of snippets into one prompt; 24k leaves room for the answer
# (KV cache for qwen2.5:14b at 24k is ~5 GB, fine on the 20 GB slice).
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-24576}"
export TIKTOKEN_CACHE_DIR="$AMG_MODELS_DIR/tiktoken_cache"      # pre-cached cl100k_base (no internet needed)
export OLLAMA_NOPRUNE=1
# LightRAG indexes with LIGHTRAG_ASYNC concurrent extraction calls at an 8k context (see the
# runner). Extraction is ~40 s/abstract on a 2g.20gb slice, so this stage runs on a full H100:
#   sbatch --export=ALL,EXT_STAGE=lightrag,LIGHTRAG_ASYNC=8 --gres=gpu:h100:1 --mem=64G --time=10:00:00 run_extbase_alliance.bash
# LLM_TIMEOUT: LightRAG's per-call timeout (default 240 s) is too short for a busy server.
[ "$STAGE" = "lightrag" ] && export OLLAMA_NUM_PARALLEL="${LIGHTRAG_ASYNC:-4}" OLLAMA_CONTEXT_LENGTH=8192 LLM_TIMEOUT="${LLM_TIMEOUT:-900}"
export PATH="$SLURM_SUBMIT_DIR/bin:$PATH"
export LD_LIBRARY_PATH="$SLURM_SUBMIT_DIR/lib/ollama:${LD_LIBRARY_PATH:-}"
export LLM_MODEL="${LLM_MODEL:-qwen2.5:14b}"
command -v ollama >/dev/null || { echo "ERROR: ollama binary missing"; exit 1; }
ollama serve > "ollama_${SLURM_JOB_ID}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill $OLLAMA_PID 2>/dev/null || true' EXIT
for i in $(seq 1 90); do curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null && break; sleep 2; done
ollama run "$LLM_MODEL" "ready" >/dev/null 2>&1 || true

# OpenAI-compatible endpoint (MedRAG uses the openai client; LiteLLM/LightRAG use Ollama natively)
export OPENAI_BASE_URL="http://$OLLAMA_HOST/v1" OPENAI_API_BASE="http://$OLLAMA_HOST/v1" OPENAI_API_KEY=ollama
export OLLAMA_API_BASE="http://$OLLAMA_HOST"
PGXQA=dataset/PGxQA/pgxqa_eval.jsonl
MASKED=dataset/ADR_DataSet_masked/masked_questions.jsonl
CORPUS=$EXT/corpus_pubmed

date
case "$STAGE" in
  medrag|imedrag)
    # medrag: builds the MedCPT index on first use (~500k chunks), then one call per question.
    # imedrag: 3 follow-up rounds per question; submit it with --dependency=afterok:<medrag job>
    # so it finds the cached index.
    source .venv/bin/activate          # the project venv already has torch/transformers/sentence-transformers/openai; python-liquid was added
    cp extbase/medrag_faiss_shim.py $EXT/MedRAG/src/faiss.py     # exact flat index in numpy (no faiss wheel here)
    python -u extbase/run_medrag_baseline.py --mode $STAGE --input $PGXQA  --out results/pgxqa_${STAGE}.jsonl
    python -u extbase/run_medrag_baseline.py --mode $STAGE --input $MASKED --out results/maskrec_${STAGE}.jsonl
    ;;
  paperqa)
    source $EXT/venv-paperqa/bin/activate
    SUF=${PAPERQA_AGENT:+_$PAPERQA_AGENT}        # PAPERQA_AGENT=fake -> results/*_paperqa_fake.jsonl
    python -u extbase/run_paperqa_baseline.py --corpus $CORPUS --input $PGXQA  --out results/pgxqa_paperqa${SUF}.jsonl
    python -u extbase/run_paperqa_baseline.py --corpus $CORPUS --input $MASKED --out results/maskrec_paperqa${SUF}.jsonl
    ;;
  lightrag)
    source $EXT/venv-lightrag/bin/activate
    python -u extbase/run_lightrag_baseline.py --corpus $CORPUS --workdir $EXT/lightrag_work --index
    python -u extbase/run_lightrag_baseline.py --corpus $CORPUS --workdir $EXT/lightrag_work --input $PGXQA  --out results/pgxqa_lightrag.jsonl
    python -u extbase/run_lightrag_baseline.py --corpus $CORPUS --workdir $EXT/lightrag_work --input $MASKED --out results/maskrec_lightrag.jsonl
    ;;
  *) echo "unknown EXT_STAGE=$STAGE"; exit 1 ;;
esac
kill $OLLAMA_PID 2>/dev/null || true
date
