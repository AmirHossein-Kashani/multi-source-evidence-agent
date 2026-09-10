#!/bin/bash
# BERTScore evaluation of GenMedGPT-5k results, as a SLURM job (NOT on the login node).
#
# Scores results/genmedgpt5k_results.jsonl (generated vs reference) with BERTScore
# (roberta-large, rescaled). roberta-large is cached under $AMG_MODELS_DIR/hf_cache, so this runs with
# no internet needed. Short + CPU-only. Does NOT run --judge (that would need the LLM tunnel).

#SBATCH --job-name=amg-eval
#SBATCH --account=def-ester_cpu
#SBATCH --time=00:30:00
#SBATCH --mem=16G
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mail-user=danielkordm@gmail.com
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=amg_eval_%j.out

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

date
echo "Scoring $(python3 -c "print(sum(1 for _ in open('results/genmedgpt5k_results.jsonl')))") result rows with BERTScore"
python eval_genmedgpt.py

deactivate
date
