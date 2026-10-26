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

    # ollama_embed is itself an EmbeddingFunc declared for bge-m3 (1024-d); calling it through
    # another EmbeddingFunc runs the inner 1024-d check on nomic's 768-d vectors and every
    # embedding fails ("vector count mismatch"). The library's documented pattern is to wrap
    # the raw function, ollama_embed.func. nomic-embed-text v1.5 expects task prefixes.
    async def embed(texts, context="document"):
        return await ollama_embed.func(texts, embed_model="nomic-embed-text", host=host, context=context,
                                       query_prefix="search_query: ", document_prefix="search_document: ")

    rag = LightRAG(
        working_dir=workdir,
        llm_model_func=ollama_model_complete,
        llm_model_name=model,
        # Indexing cost: one extraction call per chunk (~1k generated tokens). LIGHTRAG_ASYNC
        # concurrent requests at an 8k context (the job sets OLLAMA_NUM_PARALLEL to match):
        # 4 on a 20 GB MIG slice (~40 s/abstract, too slow for 3.7k abstracts), 8 on a full
        # H100. No gleaning pass.
        llm_model_max_async=int(os.environ.get("LIGHTRAG_ASYNC", "4")),
        # Abstracts are one chunk each, so the LLM concurrency actually reached is the number
        # of documents processed at once (default 3), not llm_model_max_async.
        max_parallel_insert=int(os.environ.get("LIGHTRAG_ASYNC", "4")),
        # num_predict: an extraction answer for one abstract is well under 3k tokens; without
        # a cap the model occasionally loops (18k-token outputs were observed) and holds a
        # slot for minutes.
        llm_model_kwargs={"host": host, "options": {"num_ctx": 8192, "temperature": 0, "num_predict": 3072}},
        entity_extract_max_gleaning=0,
        tiktoken_model_name="gpt-3.5-turbo",      # cl100k_base is pre-cached; the default (gpt-4o-mini) would need a download
        embedding_func=EmbeddingFunc(embedding_dim=768, max_token_size=8192, model_name="nomic-embed-text",
                                     supports_asymmetric=True, func=embed),
    )
    return rag


async def init(rag):
    await rag.initialize_storages()
    try:
        from lightrag.kg.shared_storage import initialize_pipeline_status
        await initialize_pipeline_status()
    except Exception:
        pass


async def doc_status_counts(rag):
    """{status: n} over LightRAG's document-status store (what actually made it into the index)."""
    from collections import Counter
    from lightrag.base import DocStatus
    counts = Counter()
    for st in DocStatus:
        try:
            docs = await rag.doc_status.get_docs_by_status(st)
        except Exception:
            try:
                docs = await rag.doc_status.get_docs_by_statuses([st])
            except Exception:
                continue
        if docs:
            counts[st.value] = len(docs)
    return dict(counts)


async def retry_failed(rag, corpus: str):
    """This LightRAG version does not re-queue FAILED documents on insert (only an explicit
    server-side scan does), so failed ones are deleted and inserted again once."""
    from lightrag.base import DocStatus
    try:
        failed = await rag.doc_status.get_docs_by_status(DocStatus.FAILED)
    except Exception:
        failed = await rag.doc_status.get_docs_by_statuses([DocStatus.FAILED])
    ids = sorted(failed or {})
    print(f"[lightrag] retrying {len(ids)} failed documents")
    for doc_id in ids:
        name = f"PMID_{doc_id}.txt"
        path = os.path.join(corpus, name)
        if not os.path.exists(path):
            print(f"[lightrag]   no source file for failed doc {doc_id}, skipped"); continue
        try:
            await rag.adelete_by_doc_id(doc_id)
            await rag.ainsert([open(path, encoding="utf-8").read()], ids=[doc_id], file_paths=[name])
        except Exception as e:
            print(f"[lightrag]   retry of {doc_id} failed: {type(e).__name__}: {e}")


def load_done(out_path: str):
    """Ids already answered. Rows without an answer (errors) are dropped from the file so a
    re-run retries them, matching run_genmedgpt.py's 'failed items are never kept' contract."""
    if not os.path.exists(out_path):
        return set()
    rows = [json.loads(l) for l in open(out_path, encoding="utf-8") if l.strip()]
    good = [r for r in rows if r.get("generated_answer")]
    if len(good) != len(rows):
        with open(out_path, "w", encoding="utf-8") as f:
            for r in good:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {r["id"] for r in good}


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
        print(f"[lightrag] document status after indexing: {asyncio.run(doc_status_counts(rag))}")
        asyncio.run(retry_failed(rag, args.corpus))
        print(f"[lightrag] document status after retry: {asyncio.run(doc_status_counts(rag))}")

    if args.input:
        from lightrag import QueryParam
        print(f"[lightrag] document status: {asyncio.run(doc_status_counts(rag))}")
        items = [json.loads(l) for l in open(args.input, encoding="utf-8")]
        done = load_done(args.out)
        todo = [it for it in items if it["id"] not in done][: (args.limit or None)]
        print(f"[lightrag] {len(done)} answered, {len(todo)} to answer (mode={args.mode})")
        with open(args.out, "a", encoding="utf-8") as f:
            for n, it in enumerate(todo, 1):
                t0 = time.time()
                rec = {"id": it["id"], "question": it["question"], "reference": it.get("reference", ""),
                       "system": "lightrag", **{k: v for k, v in it.items() if k.startswith("bench_")}}
                try:
                    # context budget below the server's num_ctx; no rerank model is configured
                    ans = rag.query(it["question"], param=QueryParam(mode=args.mode, max_total_tokens=6000,
                                                                     enable_rerank=False))
                    rec["generated_answer"] = str(ans)
                except Exception as e:
                    rec.update({"generated_answer": "", "error": f"{type(e).__name__}: {e}"})
                rec.update({"risk_genes": [], "drugs": [], "seconds": round(time.time() - t0, 1)})
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                print(f"[lightrag] {n}/{len(todo)} id={it['id']} {rec['seconds']}s len={len(rec['generated_answer'])}")


if __name__ == "__main__":
    main()
