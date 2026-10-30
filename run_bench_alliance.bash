#!/bin/bash
# Benchmarks and baselines (docs/PLAN.md section 6, extended): one GPU job per stage.
#
#   sbatch --export=ALL,BENCH_STAGE=pgxcorpus  --time=02:00:00 run_bench_alliance.bash
#       digest-chain extraction on PGxCorpus (874 sentences) + dictionary baseline + scores
#   sbatch --export=ALL,BENCH_STAGE=masked     --time=04:30:00 run_bench_alliance.bash
#       masked-association recovery (E1): LLM-only, phase 13 and phase 15 on the masked
#       tables written by make_masked_recovery.py
#   sbatch --export=ALL,BENCH_STAGE=pgxqa15    --time=06:00:00 run_bench_alliance.bash
#       PGxQA subsets with the phase-15 configuration (lighter budget: 1 round, 4 queries,
#       4 new papers per round)
#   sbatch --export=ALL,BENCH_STAGE=pgxqa_base --time=04:00:00 run_bench_alliance.bash
#       PGxQA subsets with baseline A (no retrieval) and baseline B (original AMG-RAG:
#       PubMed + Wikipedia through the graph)
#   sbatch --export=ALL,BENCH_STAGE=pgxqa_ablate --gres=gpu:h100:1 --time=01:00:00 run_bench_alliance.bash
#       the ablation ladder below phase 15 on the same items: the ClinPGx tables alone
#       (phase-3 setup), the tables plus the base PubMed retrieval with raw article text
#       (no digest, ledger or cards), and phase 13 (digest + ledger + cards, no discovery
#       loop) at the phase-15 run's total budget (8 queries, 8 papers). ~5 h on a MIG slice;
#       run as a chain of 1-hour full-GPU jobs (--dependency=afterany:<previous>), every
#       condition resumes.
#
# Every stage serves qwen2.5:14b locally on the MIG slice exactly as the phase scripts do.
# run_genmedgpt.py is resume-safe, so a stage that hits the time limit can be resubmitted.

#SBATCH --job-name=amg-bench
#SBATCH --account=def-ester_gpu
#SBATCH --gres=gpu:nvidia_h100_80gb_hbm3_2g.20gb:1
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_bench_%j.out

set -u
STAGE="${BENCH_STAGE:?set BENCH_STAGE to pgxcorpus | masked | pgxqa15 | pgxqa_base | pgxqa_ablate}"

module load StdEnv/2023
module load python/3.11.5
module load arrow/17.0.0
cd "$SLURM_SUBMIT_DIR" || exit 1
source .venv/bin/activate

export AMG_MODELS_DIR="${AMG_MODELS_DIR:-$(dirname "$SLURM_SUBMIT_DIR")/AMG-RAG-models}"
export HF_HOME="$AMG_MODELS_DIR/hf_cache"
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

if [ "$STAGE" != "pgxcorpus" ]; then
  if ! curl -sf --max-time 20 "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi" >/dev/null; then
    echo "INTERNET CHECK: NCBI NOT reachable -- stage $STAGE needs PubMed; aborting."; exit 1
  fi
  echo "INTERNET CHECK: NCBI reachable."
fi

export OLLAMA_PORT=$(( 11000 + (SLURM_JOB_ID % 4000) ))
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export OLLAMA_HOST="127.0.0.1:${OLLAMA_PORT}"
export OLLAMA_KEEP_ALIVE=-1
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-16384}"
export OLLAMA_NOPRUNE=1
export PATH="$SLURM_SUBMIT_DIR/bin:$PATH"
export LD_LIBRARY_PATH="$SLURM_SUBMIT_DIR/lib/ollama:${LD_LIBRARY_PATH:-}"
export LLM_MODEL="${LLM_MODEL:-qwen2.5:14b}"
command -v ollama >/dev/null || { echo "ERROR: ollama binary missing; run setup_ollama.bash first."; exit 1; }
ollama serve > "ollama_${SLURM_JOB_ID}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill $OLLAMA_PID 2>/dev/null || true' EXIT
for i in $(seq 1 90); do curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null && break; sleep 2; done
ollama run "$LLM_MODEL" "ready" >/dev/null 2>&1 || true
export LLM_BASE_URL="http://127.0.0.1:${OLLAMA_PORT}/v1"
export LLM_EXTRA_HEADERS=""
export UNPAYWALL_EMAIL="${UNPAYWALL_EMAIL:-}"
export AMG_MESH_ONLINE="${AMG_MESH_ONLINE:-1}"

# --- configuration blocks --------------------------------------------------------------
phase13_env() {
  export AMG_ANSWER_STYLE=adr AMG_USE_EXTERNAL=0 AMG_KB_SOURCE=pharmgkb+pubmed_combo
  export AMG_COMBO_MAX_QUERIES=4 AMG_OPEN_PER_PHRASE=2 AMG_PAPER_DIGEST=1 AMG_EVIDENCE_LEDGER=1
  export AMG_CONTRADICTION_LAYER=1 AMG_PUBMED_FULLTEXT=1 AMG_FULLTEXT_MAX_CHARS=3000
  export AMG_DIGEST_MAX_PAPERS=6 AMG_DIGEST_BATCH_CHARS=2400 AMG_DIGEST_MAX_BATCHES=6
  export AMG_PATH_DISCOVERY=0 AMG_SEARCH_ROUNDS=0 AMG_FOLLOWUP_SEARCH=0
}
phase15_env() {
  phase13_env
  export AMG_PATH_DISCOVERY=1 AMG_PATH_MAX_CANDIDATES=10 AMG_SEARCH_ROUNDS=2 AMG_QUERY_BUDGET=6 AMG_FOLLOWUP_SEARCH=1
}
phase15_lite_env() {
  phase15_env
  export AMG_SEARCH_ROUNDS=1 AMG_QUERY_BUDGET=4 AMG_DIGEST_MAX_PAPERS=4
}
baselineA_env() {   # no retrieval at all: the model's own knowledge through the graph
  unset AMG_KB_SOURCE AMG_KB_CLINVAR AMG_KB_REL
  export AMG_ANSWER_STYLE=adr AMG_USE_EXTERNAL=0 AMG_PAPER_DIGEST=0 AMG_EVIDENCE_LEDGER=0
  export AMG_CONTRADICTION_LAYER=0 AMG_PATH_DISCOVERY=0 AMG_SEARCH_ROUNDS=0 AMG_FOLLOWUP_SEARCH=0 AMG_PUBMED_FULLTEXT=0
}
baselineB_env() {   # the original AMG-RAG retrieval: PubMed + Wikipedia through the graph
  baselineA_env
  export AMG_USE_EXTERNAL=1
}
clinpgx_only_env() {   # the curated tables alone through the graph (phase-3 setup): no PubMed, no ledger
  baselineA_env
  export AMG_KB_SOURCE=pharmgkb
}
plain_rag_env() {      # tables + the phase-13 PubMed retrieval, raw article text in the prompt: no digest, ledger or cards
  phase13_env
  export AMG_PAPER_DIGEST=0 AMG_EVIDENCE_LEDGER=0 AMG_CONTRADICTION_LAYER=0
}
run_set() {   # run_set <input.jsonl> <output.jsonl>
  export GENMED_INPUT="$1" GENMED_OUTPUT="$2" GENMED_OFFSET=0
  export GENMED_N="$(wc -l < "$1")"
  echo "=== $(date '+%H:%M') running $(basename "$1") -> $(basename "$2")"
  python -u run_genmedgpt.py
}

date
case "$STAGE" in
  pgxcorpus)
    phase13_env    # only the digest chain is used; the KB load is harmless
    python -u eval_pgxcorpus.py --mode llm --out results/pgxcorpus_llm.jsonl --limit "${PGXCORPUS_LIMIT:-0}"
    python -u eval_pgxcorpus.py --mode dict --out results/pgxcorpus_dict.jsonl
    python -u eval_pgxcorpus.py --score results/pgxcorpus_llm.jsonl results/pgxcorpus_dict.jsonl | tee results/pgxcorpus_extraction.md
    ;;
  masked)
    M="$SLURM_SUBMIT_DIR/dataset/ADR_DataSet_masked"
    [ -f "$M/masked_questions.jsonl" ] || { echo "run make_masked_recovery.py first"; exit 1; }
    baselineA_env;  run_set "$M/masked_questions.jsonl" results/maskrec_llmonly.jsonl
    phase13_env;    export AMG_KB_CLINVAR="$M/clinicalVariants.tsv" AMG_KB_REL="$M/relationships.tsv"
                    run_set "$M/masked_questions.jsonl" results/maskrec_phase13.jsonl
    phase15_env;    export AMG_KB_CLINVAR="$M/clinicalVariants.tsv" AMG_KB_REL="$M/relationships.tsv"
                    run_set "$M/masked_questions.jsonl" results/maskrec_phase15.jsonl
    python eval_masked_recovery.py phase15=results/maskrec_phase15.jsonl phase13=results/maskrec_phase13.jsonl llm=results/maskrec_llmonly.jsonl | tee results/masked_recovery.md
    ;;
  pgxqa15)
    phase15_lite_env; run_set dataset/pgxqa_eval.jsonl results/pgxqa_phase15.jsonl
    ;;
  pgxqa_base)
    baselineA_env; run_set dataset/pgxqa_eval.jsonl results/pgxqa_llmonly.jsonl
    baselineB_env; run_set dataset/pgxqa_eval.jsonl results/pgxqa_amgrag.jsonl
    ;;
  pgxqa_ablate)
    clinpgx_only_env; run_set dataset/pgxqa_eval.jsonl results/pgxqa_clinpgx_only.jsonl
    phase13_env; export AMG_COMBO_MAX_QUERIES=8 AMG_DIGEST_MAX_PAPERS=8     # = phase 15 lite's 4 base + 4 round
                 run_set dataset/pgxqa_eval.jsonl results/pgxqa_phase13.jsonl
    plain_rag_env; export AMG_COMBO_MAX_QUERIES=8
                 run_set dataset/pgxqa_eval.jsonl results/pgxqa_plainrag.jsonl
    ;;
  *) echo "unknown BENCH_STAGE=$STAGE"; exit 1 ;;
esac
kill $OLLAMA_PID 2>/dev/null || true
date
