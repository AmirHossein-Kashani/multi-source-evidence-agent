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


def make_settings(corpus: str, index_name: str):
    from paperqa import Settings
    from paperqa.settings import AgentSettings, AnswerSettings, IndexSettings, ParsingSettings
    host = os.environ.get("OLLAMA_API_BASE", "http://127.0.0.1:11434")
    model = "ollama/" + os.environ.get("LLM_MODEL", "qwen2.5:14b")
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
                                                use_absolute_paper_directory=True),
                            search_count=12),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    from paperqa import ask
    settings = make_settings(os.path.abspath(args.corpus), "pubmed_pgx")

    items = [json.loads(l) for l in open(args.input, encoding="utf-8")]
    done = set()
    if os.path.exists(args.out):
        done = {json.loads(l)["id"] for l in open(args.out, encoding="utf-8") if l.strip()}
    todo = [it for it in items if it["id"] not in done][: (args.limit or None)]
    print(f"[paperqa] {len(done)} answered, {len(todo)} to answer")
    with open(args.out, "a", encoding="utf-8") as f:
        for n, it in enumerate(todo, 1):
            t0 = time.time()
            rec = {"id": it["id"], "question": it["question"], "reference": it.get("reference", ""),
                   "system": "paperqa2", **{k: v for k, v in it.items() if k.startswith("bench_")}}
            try:
                resp = ask(it["question"], settings=settings)
                sess = getattr(resp, "session", resp)
                rec["generated_answer"] = getattr(sess, "answer", "") or getattr(sess, "formatted_answer", "") or str(sess)
                ctxs = getattr(sess, "contexts", []) or []
                rec["references"] = [{"ref": getattr(getattr(c, "text", None), "name", ""),
                                      "score": getattr(c, "score", None)} for c in ctxs[:10]]
            except Exception as e:
                rec.update({"generated_answer": "", "error": f"{type(e).__name__}: {e}"})
                print(f"[paperqa] id={it['id']} failed: {e}")
            rec.update({"risk_genes": [], "drugs": [], "seconds": round(time.time() - t0, 1)})
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(f"[paperqa] {n}/{len(todo)} id={it['id']} {rec['seconds']}s len={len(rec['generated_answer'])}")


if __name__ == "__main__":
    main()
