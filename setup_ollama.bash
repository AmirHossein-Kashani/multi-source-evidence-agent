#!/bin/bash
# Run this ONCE on a Nibi LOGIN node (login nodes have internet; GPU compute nodes do NOT).
# It installs a rootless Ollama binary into ./bin and pre-pulls the Qwen model into
# ../AMG-RAG-models/ollama/models (outside the repo, override with AMG_MODELS_DIR) so the
# GPU job (run_pharmgkb_alliance.bash) can serve it
# fully OFFLINE. This is our own LLM infrastructure -- no ngrok tunnel, no remote host.
#
#   bash setup_ollama.bash                       # pulls qwen2.5:14b (Q4_K_M, ~9 GB)
#   LLM_MODEL=qwen2.5:14b-instruct-q8_0 bash setup_ollama.bash   # ~16 GB, uses more VRAM
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MODEL="${LLM_MODEL:-qwen2.5:14b}"

export AMG_MODELS_DIR="${AMG_MODELS_DIR:-$(dirname "$ROOT")/AMG-RAG-models}"
export OLLAMA_HOME="$AMG_MODELS_DIR/ollama"
export OLLAMA_MODELS="$OLLAMA_HOME/models"
export PATH="$ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$ROOT/lib/ollama:${LD_LIBRARY_PATH:-}"
mkdir -p "$ROOT/bin" "$OLLAMA_MODELS"

# Login nodes are SHARED and use a shared loopback: other users may already run ollama on
# :11434 (a pull sent there would populate THEIR store, not ours). Pick a free port so this
# setup talks only to our own server.
pick_free_port() {
  for p in 11544 11545 11546 11547 11548 11549 11550; do
    ss -ltn 2>/dev/null | grep -q ":$p " || { echo "$p"; return; }
  done
  echo 11544
}
export OLLAMA_HOST="127.0.0.1:$(pick_free_port)"

# ---- 1. Install the Ollama binary (rootless static tarball) ----------------
# Ollama ships a zstd-compressed tarball as a GitHub release asset; resolve the latest URL
# via the API so this survives version bumps.
if [ ! -x "$ROOT/bin/ollama" ]; then
  echo "Resolving latest Ollama release ..."
  URL=$(curl -fsSL https://api.github.com/repos/ollama/ollama/releases/latest \
        | python3 -c "import sys,json;print(next(a['browser_download_url'] for a in json.load(sys.stdin)['assets'] if a['name']=='ollama-linux-amd64.tar.zst'))")
  echo "Downloading $URL ..."
  curl -fsSL "$URL" -o /tmp/ollama.$$.tar.zst
  echo "Extracting ..."
  tar --zstd -xf /tmp/ollama.$$.tar.zst -C "$ROOT"    # -> $ROOT/bin/ollama, $ROOT/lib/ollama/*
  rm -f /tmp/ollama.$$.tar.zst
fi
"$ROOT/bin/ollama" --version || { echo "ollama binary failed to run"; exit 1; }

# ---- 2. Start OUR OWN temporary server just to pull the model --------------
echo "Starting temporary ollama serve on $OLLAMA_HOST to pull '$MODEL' ..."
ollama serve >/tmp/ollama_setup.$$.log 2>&1 &
SVPID=$!
trap 'kill $SVPID 2>/dev/null || true' EXIT
ready=""
for i in $(seq 1 60); do
  curl -sf "http://$OLLAMA_HOST/api/tags" >/dev/null && { ready=1; break; }
  sleep 2
done
[ -n "$ready" ] || { echo "ERROR: our ollama server did not come up on $OLLAMA_HOST"; cat /tmp/ollama_setup.$$.log; exit 1; }

ollama pull "$MODEL"
echo "---- cached models ----"
ollama list
echo
echo "Done. '$MODEL' is cached in $OLLAMA_MODELS"
echo "Next: sbatch run_pharmgkb_alliance.bash   (uses the same cache, offline, on a GPU)"
