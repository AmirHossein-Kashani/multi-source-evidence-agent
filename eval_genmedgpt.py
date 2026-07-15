"""Evaluate GenMedGPT-5k results produced by run_genmedgpt.py.

Primary metric: BERTScore (P/R/F1) of the generated answer vs the reference doctor reply
-- the same automatic metric reported in the MindMap paper.

Optional (--judge): an LLM-as-judge using the SAME Ollama model that generated the
answers. NOTE: this is a llama3.1:8b *approximation* of the paper's GPT-4 ranking -- it
is a weaker, higher-variance judge and should be used only for relative comparison, not
as a faithful reproduction of the paper's numbers.

Usage:
    python eval_genmedgpt.py                              # BERTScore only
    python eval_genmedgpt.py --input results/genmedgpt5k_results.jsonl
    python eval_genmedgpt.py --judge                      # also run the Ollama judge
"""
import argparse
import csv
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))

# Salvage sentinel from AMG-with-KG.py -- a failure marker, not a real answer.
FALLBACK_ANSWER = "Unable to generate a reliable answer for this question."


def load_results(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_bertscore(cands, refs):
    from bert_score import score
    P, R, F1 = score(cands, refs, lang="en", model_type="roberta-large",
                     rescale_with_baseline=True, verbose=True)
    return P.tolist(), R.tolist(), F1.tolist()


def build_judge():
    """A ChatOpenAI pointed at the same Ollama endpoint used for generation."""
    from langchain_openai import ChatOpenAI
    base_url = os.environ.get("LLM_BASE_URL", "https://widen-oops-sandfish.ngrok-free.dev/v1")
    model = os.environ.get("LLM_MODEL", "llama3.1:8b")
    headers = json.loads(os.environ.get("LLM_EXTRA_HEADERS",
                                        '{"ngrok-skip-browser-warning": "true"}'))
    return ChatOpenAI(model=model, temperature=0.0,
                      api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
                      base_url=base_url, default_headers=headers)


JUDGE_PROMPT = """You are grading a doctor's answer against a reference answer.
Rate the candidate answer from 1 (poor) to 10 (excellent) on how well it matches the
reference for: disease diagnosis, drug/treatment recommendation, and recommended tests.

Patient question: {question}

Reference answer: {reference}

Candidate answer: {candidate}

Respond ONLY with a JSON object: {{"diagnosis": <1-10>, "drugs": <1-10>, "tests": <1-10>}}"""


def run_judge(rows):
    judge = build_judge()
    scores = {"diagnosis": [], "drugs": [], "tests": []}
    for r in rows:
        cand = r.get("generated_answer", "")
        if not cand.strip():
            continue
        prompt = JUDGE_PROMPT.format(question=r.get("question", ""),
                                     reference=r.get("reference", ""),
                                     candidate=cand)
        try:
            resp = judge.invoke(prompt).content
            start, end = resp.find("{"), resp.rfind("}")
            obj = json.loads(resp[start:end + 1])
            for k in scores:
                scores[k].append(float(obj.get(k, 0)))
        except Exception as e:
            print(f"  judge parse error on id={r.get('id')}: {e}")
    return scores


def summarize(name, values):
    vals = [v for v in values if v is not None]
    if not vals:
        print(f"{name}: (no values)")
        return
    print(f"{name}: mean={statistics.mean(vals):.4f}  median={statistics.median(vals):.4f}  n={len(vals)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.path.join(HERE, "results", "genmedgpt5k_results.jsonl"))
    ap.add_argument("--output", default=os.path.join(HERE, "results", "genmedgpt5k_scores.csv"))
    ap.add_argument("--judge", action="store_true",
                    help="Also run the Ollama LLM-as-judge (approximation of the paper's GPT-4 ranking).")
    args = ap.parse_args()

    rows = load_results(args.input)
    # Keep only real answers; if an id appears twice (old junk + retried row), keep the last.
    by_id = {}
    for r in rows:
        a = r.get("generated_answer", "").strip()
        if a and a != FALLBACK_ANSWER:
            by_id[r.get("id")] = r
    scored = list(by_id.values())
    skipped = len(rows) - len(scored)
    print(f"Loaded {len(rows)} results; {len(scored)} scored, {skipped} skipped (empty/failed/duplicate).")
    if not scored:
        print("Nothing to score.")
        return

    cands = [r["generated_answer"] for r in scored]
    refs = [r.get("reference", "") for r in scored]

    print("\n=== BERTScore (roberta-large, rescaled) ===")
    P, R, F1 = run_bertscore(cands, refs)
    summarize("BERTScore-P ", P)
    summarize("BERTScore-R ", R)
    summarize("BERTScore-F1", F1)

    judge_scores = None
    if args.judge:
        print("\n=== LLM-as-judge (Ollama llama3.1:8b -- APPROXIMATION of GPT-4 ranking) ===")
        judge_scores = run_judge(scored)
        for k, v in judge_scores.items():
            summarize(f"judge-{k}", v)

    # Per-item CSV
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "bertscore_p", "bertscore_r", "bertscore_f1"])
        for r, p, rr, f1 in zip(scored, P, R, F1):
            w.writerow([r.get("id"), f"{p:.4f}", f"{rr:.4f}", f"{f1:.4f}"])
    print(f"\nPer-item scores -> {args.output}")


if __name__ == "__main__":
    main()
