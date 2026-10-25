"""MedRAG / i-MedRAG (Xiong et al., 2024) as external baselines on our question files.

Uses the authors' toolkit unchanged (github.com/Teddy-XiongGZ/MedRAG) with:
  * the local Ollama server through its OpenAI-compatible endpoint
    (llm_name="OpenAI/<model>", OPENAI_BASE_URL / OPENAI_API_KEY from the environment);
  * the MedCPT retriever over the "MedText" corpus (Textbooks + StatPearls), the toolkit's
    own corpora; BM25 is not used (it needs pyserini/Java);
  * open-ended prompts in place of the multiple-choice ones: the toolkit's templates ask
    the model to pick an answer letter, so the two system prompts and two user templates
    are replaced by the same text minus the option machinery. Retrieval, context packing
    and (for i-MedRAG) the follow-up-question loop are the toolkit's code.

    python extbase/run_medrag_baseline.py --mode medrag  --input dataset/PGxQA/pgxqa_eval.jsonl --out results/pgxqa_medrag.jsonl
    python extbase/run_medrag_baseline.py --mode imedrag --input ... --out results/pgxqa_imedrag.jsonl

Output records follow run_genmedgpt.py (id, question, generated_answer, references,
bench_* passthrough) so eval_pgxqa.py / eval_masked_recovery.py score them unchanged.
Resume-safe.
"""
import argparse
import json
import os
import re
import sys
import time

MEDRAG_DIR = os.environ.get("MEDRAG_DIR", "/scratch/kashi77/ext_baselines/MedRAG")
sys.path.insert(0, os.path.join(MEDRAG_DIR, "src"))
os.chdir(MEDRAG_DIR)                       # the toolkit resolves corpus/ and templates relative to its root

OPEN_COT_SYSTEM = ("You are a helpful medical expert, and your task is to answer a medical question. "
                   "Please first think step-by-step and then give a definite answer. Organize your output "
                   "in a json formatted as Dict{\"step_by_step_thinking\": Str(explanation), "
                   "\"answer\": Str(answer)}. Your responses will be used for research purposes only.")
OPEN_COT_PROMPT = "Here is the question:\n{{question}}\n\nPlease think step-by-step and generate your output in json:"
OPEN_RAG_SYSTEM = ("You are a helpful medical expert, and your task is to answer a medical question using the "
                   "relevant documents. Please first think step-by-step and then give a definite answer. "
                   "Organize your output in a json formatted as Dict{\"step_by_step_thinking\": Str(explanation), "
                   "\"answer\": Str(answer)}. Your responses will be used for research purposes only.")
OPEN_RAG_PROMPT = ("Here are the relevant documents:\n{{context}}\n\nHere is the question:\n{{question}}\n\n"
                   "Please think step-by-step and generate your output in json:")


def parse_answer(raw: str) -> str:
    """The toolkit returns the model's raw JSON-ish text; keep the answer field when it parses."""
    if not isinstance(raw, str):
        raw = str(raw)
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            a = d.get("answer") or d.get("answer_choice") or ""
            th = d.get("step_by_step_thinking") or ""
            return (str(a) + ("\n\n" + str(th) if th else "")).strip() or raw
        except Exception:
            pass
    return raw.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["medrag", "imedrag", "cot"], required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL", "qwen2.5:14b"))
    ap.add_argument("--corpus", default="MedText")
    ap.add_argument("--k", type=int, default=32)
    ap.add_argument("--n-rounds", type=int, default=3)
    ap.add_argument("--n-queries", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    inp, out = os.path.abspath(args.input), os.path.abspath(args.out)

    from liquid import Template
    from medrag import MedRAG
    import utils as medrag_utils
    rag = args.mode != "cot"

    # Build the MedCPT index ourselves when it is missing. The toolkit would otherwise try to
    # download precomputed Textbooks embeddings from a OneDrive link (dead / unreachable from
    # the cluster) and then crash on the empty embedding folder; its own embed() and
    # construct_index() are used unchanged.
    if rag:
        db = os.path.join(MEDRAG_DIR, "corpus")
        for cname in medrag_utils.corpus_names[args.corpus]:
            idx = os.path.join(db, cname, "index", "ncbi/MedCPT-Article-Encoder")
            if not os.path.exists(os.path.join(idx, "faiss.index")):
                print(f"[index] building MedCPT index for {cname} ...")
                h = medrag_utils.embed(chunk_dir=os.path.join(db, cname, "chunk"), index_dir=idx,
                                       model_name="ncbi/MedCPT-Article-Encoder", batch_size=128)
                medrag_utils.construct_index(index_dir=idx, model_name="ncbi/MedCPT-Article-Encoder", h_dim=h)
                print(f"[index] {cname} done")
    m = MedRAG(llm_name=f"OpenAI/{args.model}", rag=rag, follow_up=(args.mode == "imedrag"),
               retriever_name="MedCPT", corpus_name=args.corpus,
               db_dir=os.path.join(MEDRAG_DIR, "corpus"), corpus_cache=False)
    # open-ended prompts (see module docstring)
    m.templates["cot_system"] = OPEN_COT_SYSTEM
    m.templates["cot_prompt"] = Template(OPEN_COT_PROMPT)
    m.templates["medrag_system"] = OPEN_RAG_SYSTEM
    m.templates["medrag_prompt"] = Template(OPEN_RAG_PROMPT)
    if "follow_up_answer" in m.templates:       # i-MedRAG: "answer choice" -> "answer"
        m.templates["follow_up_answer"] = m.templates["follow_up_answer"].replace("answer choice", "answer")

    items = [json.loads(l) for l in open(inp, encoding="utf-8")]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["id"] for l in open(out, encoding="utf-8") if l.strip()}
    todo = [it for it in items if it["id"] not in done][: (args.limit or None)]
    print(f"[{args.mode}] {len(done)} done, {len(todo)} to run; corpus={args.corpus} k={args.k}")
    with open(out, "a", encoding="utf-8") as f:
        for n, it in enumerate(todo, 1):
            t0 = time.time()
            rec = {"id": it["id"], "question": it["question"], "reference": it.get("reference", ""),
                   "system": args.mode, **{k: v for k, v in it.items() if k.startswith("bench_")}}
            try:
                if args.mode == "imedrag":
                    ans, history = m.answer(question=it["question"], options=None, k=args.k,
                                            n_rounds=args.n_rounds, n_queries=args.n_queries)
                    rec.update({"generated_answer": parse_answer(ans),
                                "history": [h.get("content", "")[:2000] for h in history][-8:]})
                else:
                    ans, snippets, scores = m.answer(question=it["question"], options=None, k=args.k)
                    raw = ans[0] if isinstance(ans, list) else ans
                    rec.update({"generated_answer": parse_answer(raw),
                                "references": [{"ref": s.get("id", ""), "title": s.get("title", "")}
                                               for s in (snippets or [])[:args.k]]})
            except Exception as e:
                rec.update({"generated_answer": "", "error": f"{type(e).__name__}: {e}"})
                print(f"[{args.mode}] id={it['id']} failed: {e}")
            rec.update({"risk_genes": [], "drugs": [], "seconds": round(time.time() - t0, 1)})
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(f"[{args.mode}] {n}/{len(todo)} id={it['id']} {rec['seconds']}s len={len(rec['generated_answer'])}")


if __name__ == "__main__":
    main()
