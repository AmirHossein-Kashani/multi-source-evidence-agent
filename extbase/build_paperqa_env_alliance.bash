#!/bin/bash
# Build the PaperQA2 virtual environment. paper-qa depends on tantivy (Rust); this Python
# does not accept PyPI's compiled wheels and the wheelhouse has no tantivy, so it is compiled
# here with the cluster's Rust module. Compiled dependencies that the wheelhouse does have are
# installed from it first; the rest (pure Python + tantivy) come from PyPI.
#SBATCH --job-name=paperqa-env
#SBATCH --account=def-ester_cpu
#SBATCH --time=01:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --output=/scratch/kashi77/ext_baselines/paperqa_env_%j.out
set -u
module load StdEnv/2023 python/3.11.5 rust/1.76.0   # 1.85 is a nightly build: old crates (ahash) fail on it, new ones need 1.88
cd /scratch/kashi77/ext_baselines || exit 1
rm -rf venv-paperqa && virtualenv --no-download venv-paperqa && source venv-paperqa/bin/activate
pip install --no-index --upgrade pip
pip install --no-index tiktoken tokenizers numpy pydantic pydantic_core aiohttp httpx anyio rapidfuzz pymupdf pyyaml orjson maturin || exit 1
export CARGO_HOME=$SLURM_TMPDIR/cargo CARGO_BUILD_JOBS=$SLURM_CPUS_PER_TASK
# tantivy 0.27 needs rustc 1.88 and the cluster's newest Rust module is 1.85: pin the last
# release whose crates build with it, then let paper-qa use it.
PIP_CONFIG_FILE=/dev/null pip install --no-build-isolation "tantivy==0.22.2" || PIP_CONFIG_FILE=/dev/null pip install --no-build-isolation "tantivy==0.24.0" || exit 1
PIP_CONFIG_FILE=/dev/null pip install --prefer-binary "paper-qa" || exit 1
python -c "import paperqa, tantivy, litellm; print('paper-qa', paperqa.__version__, '| tantivy OK | litellm', litellm.__version__ if hasattr(litellm,'__version__') else 'ok')"
echo "PAPERQA_ENV_OK"
