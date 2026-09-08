#!/bin/bash
#SBATCH --account=def-ester_cpu
#SBATCH --job-name=git_cleanup
#SBATCH --time=1:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --output=/scratch/kashi77/AMG-RAG/git_cleanup_%j.out

# One-off maintenance job: strip committed model binaries / caches out of the
# git history of /scratch/kashi77/AMG-RAG and repack. Runs on a compute node
# because the login node's CVMFS mount (which provides git) is broken.
# Safety net: the untouched pre-rewrite .git still exists in
# /project/def-ester/kashi77/AMG-RAG/.git and is left alone by this job.

set -euo pipefail
REPO=/scratch/kashi77/AMG-RAG
WORK=$SLURM_TMPDIR/AMG.git

command -v git >/dev/null || module load StdEnv/2023
git --version

echo "== copy .git to node-local disk =="
rsync -a "$REPO/.git/" "$WORK/"
export GIT_DIR=$WORK
git config core.bare true

echo "== state before =="
du -sh "$WORK"
git for-each-ref
git rev-list --count --all

echo "== blobs larger than 95MB in history (size path) =="
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3>95000000 {print $3, substr($0, index($0,$4))}' \
  | sort -rn > "$SLURM_TMPDIR/bigblobs.txt"
cat "$SLURM_TMPDIR/bigblobs.txt"

# top-level roots of the big blobs + known cache/binary dirs
cut -d' ' -f3- "$SLURM_TMPDIR/bigblobs.txt" | sed 's#/.*##' | sort -u > "$SLURM_TMPDIR/roots.txt"
printf '%s\n' .ollama .venv .hf_cache lib bin __pycache__ .vscode >> "$SLURM_TMPDIR/roots.txt"
ROOTS=$(sort -u "$SLURM_TMPDIR/roots.txt" | tr '\n' ' ')
echo "== paths to purge from history: $ROOTS =="

echo "== drop codex tool refs =="
git for-each-ref --format='%(refname)' refs/codex | xargs -r -n1 git update-ref -d

echo "== rewrite history =="
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --prune-empty \
  --index-filter "git rm -rq --cached --ignore-unmatch $ROOTS" \
  --tag-name-filter cat -- --all

echo "== cleanup and repack =="
git for-each-ref --format='%(refname)' refs/original | xargs -r -n1 git update-ref -d
git reflog expire --expire=now --all
git gc --prune=now
du -sh "$WORK"

echo "== verify =="
git fsck --no-dangling
git rev-list --count --all
git log --oneline | head -20

echo "== swap cleaned .git into place =="
git config core.bare false
git config core.logallrefupdates true
mv "$REPO/.git" "$REPO/.git.pre-rewrite"
rsync -a "$WORK/" "$REPO/.git/"

cd "$REPO"
unset GIT_DIR
echo "== post-swap status (first 15 lines) =="
git status --short | head -15

echo "== ensure caches are gitignored =="
touch .gitignore
for p in .ollama/ .venv/ .hf_cache/ lib/ bin/ __pycache__/ .vscode/ 'ollama_*.log' '*.out'; do
  grep -qxF "$p" .gitignore || echo "$p" >> .gitignore
done
git add .gitignore
git -c user.name=kashi77 -c user.email=danielkordm@gmail.com commit -m "Remove model binaries from git history; ignore caches and logs

The Ollama model blobs, venv, HF cache and ollama runtime had been
committed, inflating .git to 12G. History was rewritten to drop them.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" || echo "gitignore commit skipped"

echo "== final =="
du -sh "$REPO/.git" "$REPO/.git.pre-rewrite"
echo "DONE - .git.pre-rewrite can be deleted once the repo is confirmed good"
