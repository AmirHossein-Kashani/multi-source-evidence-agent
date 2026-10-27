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
# existing <prefix> name=suffix ...  ->  "name=results/<prefix>_<suffix>.jsonl" for the files that exist
existing() { local pre=$1; shift; for spec in "$@"; do f="results/${pre}_${spec#*=}.jsonl"; [ -s "$f" ] && printf '%s=%s ' "${spec%%=*}" "$f"; done; }
{
  echo "# Benchmark tables (generated $(date '+%Y-%m-%d %H:%M'))"
  echo
  echo "## PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl)"
  echo
  # our systems and the ablation ladder (section 3), the external published systems
  # (section 4, with the ClinPGx-augmented PaperQA2), then the PGxQA paper's own models on
  # the same items (convert_pgxqa_reference.py); files that do not exist are skipped.
  # --ci: 95% bootstrap intervals per cell and paired differences against phase 15.
  python eval_pgxqa.py $(existing pgxqa phase15=phase15 phase13=phase13 plain_rag=plainrag clinpgx_only=clinpgx_only llm_only=llmonly amg_rag=amgrag \
                         medrag=medrag imedrag=imedrag paperqa2=paperqa paperqa2_fixed=paperqa_fake paperqa2_fixed_clinpgx=paperqa_fake_clinpgx lightrag=lightrag \
                         gpt4o=ref_gpt-4o gpt4turbo=ref_gpt-4-turbo llama3_70b=ref_llama3-70b gpt35=ref_gpt-3.5-turbo gemini=ref_gemini-pro) \
                         --bertscore --ci 2000 --ci-ref phase15 2>/dev/null | grep -E '^\||^$'
  echo
  echo "## Masked-association recovery (E1)"
  echo
  python eval_masked_recovery.py $(existing maskrec phase15=phase15 phase13=phase13 llm_only=llmonly medrag=medrag imedrag=imedrag paperqa2=paperqa paperqa2_fixed=paperqa_fake paperqa2_fixed_clinpgx=paperqa_fake_clinpgx lightrag=lightrag) 2>/dev/null
  echo
  echo "## PGxCorpus extraction"
  echo
  cat results/pgxcorpus_extraction.md
} > "$OUT"
echo "wrote $OUT"
