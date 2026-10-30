"""PGxQA's published model outputs -> results/pgxqa_ref_<model>.jsonl on OUR items.

The PGxQA repository ships every model's raw answer per question
(dataset/PGxQA/results/{DrugToGenes,GeneToDrugs,Refusal}_<model>_results.txt, column
llm_answer). Matching them to dataset/pgxqa_eval.jsonl by question text gives
reference rows (GPT-4o, GPT-4-turbo, GPT-3.5, Gemini Pro, Llama-3-70B) that eval_pgxqa.py
scores with the same gene/drug extraction and refusal rules as our systems. Those models
answered from parametric knowledge with no retrieval; the consult questions have no
published outputs.

    python convert_pgxqa_reference.py            # writes one file per model, prints coverage
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = os.path.join(HERE, "dataset", "PGxQA", "pgxqa_eval.jsonl")
RES = os.path.join(HERE, "dataset", "PGxQA", "results")
MODELS = {"gpt-4o": "gpt-4o", "gpt-4-turbo": "gpt-4-turbo", "gpt-3.5-turbo": "gpt-3.5-turbo",
          "gemini-pro": "gemini-pro", "Meta-Llama-3-70B-Instruct": "llama3-70b"}


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    items = [json.loads(l) for l in open(ITEMS, encoding="utf-8")]
    for model, tag in MODELS.items():
        answers = {}
        for fn in ("DrugToGenes", "GeneToDrugs", "Refusal"):
            p = os.path.join(RES, f"{fn}_{model}_results.txt")
            if not os.path.exists(p):
                continue
            for r in rows(p):
                q = r["question"].strip()
                if fn == "Refusal":
                    # the refusal file carries the opt-out wording in the question itself;
                    # llm_answer is the answer to that wording, llm_answer_no_opt_out to the
                    # plain one. Our items use the question text as it appears in the file.
                    answers[q] = r["llm_answer"]
                else:
                    answers.setdefault(q, r["llm_answer"])
        out = os.path.join(HERE, "results", f"pgxqa_ref_{tag}.jsonl")
        n = 0
        with open(out, "w", encoding="utf-8") as f:
            for it in items:
                a = answers.get(it["question"].strip())
                if a is None:
                    continue
                rec = {"id": it["id"], "question": it["question"], "reference": it.get("reference", ""),
                       "system": f"pgxqa_paper:{model}", "generated_answer": a, "risk_genes": [], "drugs": [],
                       **{k: v for k, v in it.items() if k.startswith("bench_")}}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1
        by = {}
        for it in items:
            by.setdefault(it["bench_subset"], [0, 0])
            by[it["bench_subset"]][1] += 1
            if it["question"].strip() in answers:
                by[it["bench_subset"]][0] += 1
        print(f"{tag:12s} {n:3d} items matched  " + "  ".join(f"{k} {a}/{b}" for k, (a, b) in sorted(by.items())))


if __name__ == "__main__":
    main()
