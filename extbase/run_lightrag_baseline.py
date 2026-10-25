"""LightRAG (Guo et al., 2024; github.com/HKUDS/LightRAG) as a graph-RAG baseline whose graph
is built FROM the documents (LLM entity/relation extraction), with no curated knowledge
graph. Same local model and the same PubMed abstract corpus as the other external baselines.

    python extbase/run_lightrag_baseline.py --corpus <dir> --workdir <dir> --index
    python extbase/run_lightrag_baseline.py --corpus <dir> --workdir <dir> --input q.jsonl --out r.jsonl

LLM: qwen2.5:14b through Ollama (OLLAMA_API_BASE); embeddings: nomic-embed-text (768-d)
through Ollama. Query mode "hybrid" (local entity context + global relation context), the
mode the authors report as their default. Resume-safe on the query side.
"""
import argparse
import asyncio
import json
import os
import time


def build_rag(workdir: str):
    from lightrag import LightRAG
    from lightrag.llm.ollama import ollama_model_complete, ollama_embed
    from lightrag.utils import EmbeddingFunc
    host = os.environ.get("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    model = os.environ.get("LLM_MODEL", "qwen2.5:14b")
    rag = LightRAG(
        working_dir=workdir,
        llm_model_func=ollama_model_complete,
        llm_model_name=model,
        llm_model_max_async=2,
        llm_model_kwargs={"host": host, "options": {"num_ctx": 16384, "temperature": 0}},
        tiktoken_model_name="gpt-3.5-turbo",      # cl100k_base is pre-cached; the default (gpt-4o-mini) would need a download
        embedding_func=EmbeddingFunc(
            embedding_dim=768, max_token_size=8192,
            func=lambda texts: ollama_embed(texts, embed_model="nomic-embed-text", host=host)),
    )
    return rag


async def init(rag):
    await rag.initialize_storages()
    try:
        from lightrag.kg.shared_storage import initialize_pipeline_status
        await initialize_pipeline_status()
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--input")
    ap.add_argument("--out")
    ap.add_argument("--mode", default="hybrid")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)
    rag = build_rag(args.workdir)
    asyncio.run(init(rag))

    if args.index:
        files = sorted(f for f in os.listdir(args.corpus) if f.startswith("PMID_") and f.endswith(".txt"))
        done_path = os.path.join(args.workdir, "indexed_files.json")
        done = set(json.load(open(done_path))) if os.path.exists(done_path) else set()
        todo = [f for f in files if f not in done]
        print(f"[lightrag] {len(done)} indexed, {len(todo)} to index")
        batch = 25
        for i in range(0, len(todo), batch):
            names = todo[i:i + batch]
            docs = [open(os.path.join(args.corpus, n), encoding="utf-8").read() for n in names]
            ids = [n[5:-4] for n in names]                         # PMID as document id
            t0 = time.time()
            try:
                rag.insert(docs, ids=ids, file_paths=names)
            except TypeError:
                rag.insert(docs)
            done |= set(names)
            json.dump(sorted(done), open(done_path, "w"))
            print(f"[lightrag] indexed {len(done)}/{len(files)} ({time.time() - t0:.0f}s for {len(names)})")

    if args.input:
        from lightrag import QueryParam
        items = [json.loads(l) for l in open(args.input, encoding="utf-8")]
        done = set()
        if os.path.exists(args.out):
            done = {json.loads(l)["id"] for l in open(args.out, encoding="utf-8") if l.strip()}
        todo = [it for it in items if it["id"] not in done][: (args.limit or None)]
        print(f"[lightrag] {len(done)} answered, {len(todo)} to answer (mode={args.mode})")
        with open(args.out, "a", encoding="utf-8") as f:
            for n, it in enumerate(todo, 1):
                t0 = time.time()
                rec = {"id": it["id"], "question": it["question"], "reference": it.get("reference", ""),
                       "system": "lightrag", **{k: v for k, v in it.items() if k.startswith("bench_")}}
                try:
                    # context budget below the server's num_ctx; no rerank model is configured
                    ans = rag.query(it["question"], param=QueryParam(mode=args.mode, max_total_tokens=14000,
                                                                     enable_rerank=False))
                    rec["generated_answer"] = str(ans)
                except Exception as e:
                    rec.update({"generated_answer": "", "error": f"{type(e).__name__}: {e}"})
                rec.update({"risk_genes": [], "drugs": [], "seconds": round(time.time() - t0, 1)})
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                print(f"[lightrag] {n}/{len(todo)} id={it['id']} {rec['seconds']}s len={len(rec['generated_answer'])}")


if __name__ == "__main__":
    main()
