"""PaperQA2 (FutureHouse; github.com/Future-House/paper-qa) as a literature-agent baseline.

The open-source PaperQA2 agent searches a LOCAL index of papers (web discovery exists only
in the hosted product), so it is given the shared PubMed abstract corpus built by
extbase/build_pubmed_corpus.py: one text file per article with title, PMID, journal, year
and abstract. PaperQA2 indexes it once (embeddings through Ollama's nomic-embed-text), then
runs its agent (paper_search -> gather_evidence -> gen_answer) per question with the same
local qwen2.5:14b. Settings otherwise at PaperQA2 defaults except the model names,
temperature 0, and the evidence/answer-source counts, which are stated in the output.

    python extbase/run_paperqa_baseline.py --corpus <dir> --input q.jsonl --out r.jsonl
"""
import argparse
import json
import os
import time


def patch_get_router():
    """paper-qa 2026.8 builds its tool-selecting agent from `LLMModel.get_router()`, which the
    installed lmi (fhlmi 1.0.7) no longer has. Rebuild the litellm Router from the model's own
    config (the same `model_list` the removed method wrapped)."""
    from lmi.llms import LiteLLMModel
    if hasattr(LiteLLMModel, "get_router"):
        return
    import litellm
    cache = {}

    def get_router(self):
        key = id(self)
        if key not in cache:
            cache[key] = litellm.Router(model_list=self.config["model_list"])
        return cache[key]
    LiteLLMModel.get_router = get_router


def make_settings(corpus: str, index_name: str, manifest: str | None = None):
    from paperqa import Settings
    from paperqa.settings import AgentSettings, AnswerSettings, IndexSettings, ParsingSettings
    host = os.environ.get("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    # ollama_chat/ = Ollama's chat endpoint, which carries the model's native tool calling
    # (needed by the agent); ollama/ would emulate tools through prompting.
    model = "ollama_chat/" + os.environ.get("LLM_MODEL", "qwen2.5:14b")
    llm_cfg = {"model_list": [{"model_name": model,
                               "litellm_params": {"model": model, "api_base": host,
                                                  "temperature": 0, "num_ctx": 16384}}]}
    emb_cfg = {"model_list": [{"model_name": "ollama/nomic-embed-text",
                               "litellm_params": {"model": "ollama/nomic-embed-text", "api_base": host}}]}
    return Settings(
        llm=model, llm_config=llm_cfg,
        summary_llm=model, summary_llm_config=llm_cfg,
        embedding="ollama/nomic-embed-text", embedding_config=emb_cfg,
        temperature=0,
        paper_directory=corpus,
        index_directory=os.path.join(os.path.dirname(corpus.rstrip("/")), "paperqa_index"),
        parsing=ParsingSettings(use_doc_details=False),      # no Crossref/S2 calls per file
        answer=AnswerSettings(evidence_k=10, answer_max_sources=5, evidence_summary_length="about 150 words"),
        agent=AgentSettings(agent_llm=model, agent_llm_config=llm_cfg,
                            index=IndexSettings(name=index_name, paper_directory=corpus,
                                                index_directory=os.path.join(os.path.dirname(corpus.rstrip("/")), "paperqa_index"),
                                                # Keys must stay RELATIVE: paper-qa 2026.8's directory sync compares the
                                                # index keys with relative paths, so absolute keys look like files that
                                                # vanished and every build wipes and re-indexes the whole corpus (33 min
                                                # on a full H100; one job lost its hour to that). The manifest's absolute
                                                # file_location column is still found through the fallback lookup.
                                                use_absolute_paper_directory=False,
                                                manifest_file=manifest,      # title/journal/year per file: no LLM call at index time
                                                # defaults (5 readers, commit after every file) index ~36 files/min
                                                # on this filesystem; the commit is the cost, not the embedding
                                                concurrency=10, batch_size=50),
                            # The index is built once per job by build_index(); ask() must not re-sync it
                            # for every question (rebuild_index defaults to True).
                            rebuild_index=False,
                            search_count=12),
    )


def patch_manifest_empties():
    """On Python < 3.12 paper-qa reads the manifest CSV with empty cells as '' and feeds them to
    DocDetails, whose `year` is an int: one file without a journal/year line aborted the whole
    build. Drop empty cells from a manifest entry before it is validated."""
    import paperqa.agents.search as pqs
    orig = pqs.fetch_kwargs_from_manifest

    def fetch(file_location, manifest, manifest_fallback_location):
        for key in (file_location, manifest_fallback_location):
            entry = manifest.get(key)
            if entry:
                manifest[key] = {k: v for k, v in entry.items() if v not in ("", None)}
        return orig(file_location, manifest, manifest_fallback_location)
    pqs.fetch_kwargs_from_manifest = fetch


async def build_index(settings):
    """Build / sync the index explicitly (ask() would do it implicitly on the first question)
    and report how many files it holds."""
    from paperqa.agents.search import get_directory_index
    patch_manifest_empties()
    idx = await get_directory_index(settings=settings)
    files = await idx.index_files
    failed = sum(1 for v in files.values() if v == "ERROR")
    return len(files), failed


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
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--manifest", help="default: <corpus parent>/paperqa_manifest.csv (extbase/build_paperqa_manifest.py)")
    args = ap.parse_args()
    import asyncio
    from paperqa import ask
    patch_get_router()
    corpus = os.path.abspath(args.corpus)
    manifest = args.manifest or os.path.join(os.path.dirname(corpus), "paperqa_manifest.csv")
    if not os.path.exists(manifest):
        print(f"[paperqa] no manifest at {manifest}; indexing will call the LLM once per file")
        manifest = None
    settings = make_settings(corpus, "pubmed_pgx", manifest)
    t0 = time.time()
    n_files, n_failed = asyncio.run(build_index(settings))
    print(f"[paperqa] index ready: {n_files} files ({n_failed} failed) in {time.time() - t0:.0f}s")

    items = [json.loads(l) for l in open(args.input, encoding="utf-8")]
    done = load_done(args.out)
    todo = [it for it in items if it["id"] not in done][: (args.limit or None)]
    print(f"[paperqa] {len(done)} answered, {len(todo)} to answer")
    # PAPERQA_AGENT=fake runs PaperQA2's fixed pipeline (paper_search -> gather_evidence ->
    # gen_answer, the same tools in their canonical order) as a second configuration: with a
    # 14B model the tool-selecting agent sometimes answers before it has searched.
    forced = os.environ.get("PAPERQA_AGENT")
    agent_order = (forced,) if forced else ("ToolSelector", "fake")
    system = f"paperqa2:{forced}" if forced else "paperqa2"

    def run(question, agent_type):
        settings.agent.agent_type = agent_type
        resp = ask(question, settings=settings)
        sess = getattr(resp, "session", resp)
        answer = getattr(sess, "answer", "") or getattr(sess, "formatted_answer", "") or str(sess)
        ctxs = getattr(sess, "contexts", []) or []
        refs = [{"ref": getattr(getattr(c, "text", None), "name", ""), "score": getattr(c, "score", None)}
                for c in ctxs[:10]]
        return answer, refs

    with open(args.out, "a", encoding="utf-8") as f:
        for n, it in enumerate(todo, 1):
            t0 = time.time()
            rec = {"id": it["id"], "question": it["question"], "reference": it.get("reference", ""),
                   "system": system, **{k: v for k, v in it.items() if k.startswith("bench_")}}
            # Default agent (LLM tool selection); if that path errors with this model, fall back to
            # the fixed "fake" agent. The agent used is recorded per row.
            for agent_type in agent_order:
                try:
                    rec["generated_answer"], rec["references"] = run(it["question"], agent_type)
                    rec["agent_type"] = agent_type
                    rec.pop("error", None)
                    break
                except Exception as e:
                    rec.update({"generated_answer": "", "error": f"{agent_type}: {type(e).__name__}: {e}"})
                    print(f"[paperqa] id={it['id']} {agent_type} failed: {e}")
            rec.update({"risk_genes": [], "drugs": [], "seconds": round(time.time() - t0, 1)})
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(f"[paperqa] {n}/{len(todo)} id={it['id']} {rec['seconds']}s len={len(rec['generated_answer'])}")


if __name__ == "__main__":
    main()
