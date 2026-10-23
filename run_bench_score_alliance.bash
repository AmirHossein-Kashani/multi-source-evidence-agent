#!/bin/bash
# Final scoring of the benchmark runs (CPU only; BERTScore loads roberta-large from the
# offline HF cache). Writes results/benchmarks_tables.md.
#
#   sbatch run_bench_score_alliance.bash

#SBATCH --job-name=amg-bench-score
#SBATCH --account=def-ester_cpu
#SBATCH --time=00:30:00
#SBATCH --mem=8G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --output=amg_bench_score_%j.out

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
export AMG_MESH_ONLINE=0

OUT=results/benchmarks_tables.md
{
  echo "# Benchmark tables (generated $(date '+%Y-%m-%d %H:%M'))"
  echo
  echo "## PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl)"
  echo
  python eval_pgxqa.py llm_only=results/pgxqa_llmonly.jsonl amg_rag=results/pgxqa_amgrag.jsonl phase15=results/pgxqa_phase15.jsonl --bertscore 2>/dev/null | grep -E '^\|'
  echo
  echo "## Masked-association recovery (E1)"
  echo
  python eval_masked_recovery.py phase15=results/maskrec_phase15.jsonl phase13=results/maskrec_phase13.jsonl llm_only=results/maskrec_llmonly.jsonl 2>/dev/null
  echo
  echo "## PGxCorpus extraction"
  echo
  cat results/pgxcorpus_extraction.md
} > "$OUT"
echo "wrote $OUT"
