"""Batch runner: evaluate AMG-RAG (open-ended mode) on GenMedGPT-5k.

For each patient question it builds a per-question knowledge graph and produces a
free-text doctor reply via AMG_RAG_System.answer_open_question, then appends the result
to a JSONL file. Safe to interrupt/resume: already-processed ids are skipped. Failed
items (exception, empty answer, or the salvage fallback sentence) are NOT written, so a
re-run retries them; after 3 consecutive failures the run aborts (endpoint likely down).

The LLM is routed to the remote Ollama endpoint by AMG_RAG_System.__init__ when the
env var LLM_BASE_URL is set (see run_genmedgpt_alliance.bash / .env).

Config (CLI flags override env vars):
    --input   / GENMED_INPUT   default dataset/GenMedGPT-5k/genmedgpt5k.jsonl
    --output  / GENMED_OUTPUT  default results/genmedgpt5k_results.jsonl
    --n       / GENMED_N       number of items to process (default 3)
    --offset  / GENMED_OFFSET  start index into the dataset slice (default 0)
"""
import argparse
import importlib.util
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))

# Sentinel produced by AMG_RAG_System._salvage_open_answer when every LLM call failed
# (e.g. the remote endpoint is down). Rows carrying it are failures, not answers.
FALLBACK_ANSWER = "Unable to generate a reliable answer for this question."


def load_amg_module():
    """AMG-with-KG.py has a hyphen, so import it by file path."""
    path = os.path.join(HERE, "AMG-with-KG.py")
    spec = importlib.util.spec_from_file_location("amg_kg", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_dataset(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def processed_ids(output_path):
    """Ids already answered successfully. Errored/empty/fallback rows are NOT counted,
    so a re-run retries them."""
    done = set()
    if os.path.exists(output_path):
        with open(output_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                answer = rec.get("generated_answer", "").strip()
                if answer and answer != FALLBACK_ANSWER:
                    done.add(rec.get("id"))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.environ.get(
        "GENMED_INPUT", os.path.join(HERE, "dataset", "GenMedGPT-5k", "genmedgpt5k.jsonl")))
    ap.add_argument("--output", default=os.environ.get(
        "GENMED_OUTPUT", os.path.join(HERE, "results", "genmedgpt5k_results.jsonl")))
    ap.add_argument("--n", type=int, default=int(os.environ.get("GENMED_N", "3")))
    ap.add_argument("--offset", type=int, default=int(os.environ.get("GENMED_OFFSET", "0")))
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    amg = load_amg_module()
    system = amg.AMG_RAG_System(
        use_openai=True,
        openai_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    )

    data = load_dataset(args.input)
    sliced = data[args.offset: args.offset + args.n]
    done = processed_ids(args.output)
    print(f"Dataset: {len(data)} items | slice [{args.offset}:{args.offset + args.n}] "
          f"= {len(sliced)} | already done: {len(done)}")

    n_ok, n_err = 0, 0
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 3  # a dead endpoint fails every item; stop instead of writing junk
    with open(args.output, "a", encoding="utf-8") as out:
        for item in sliced:
            qid = item.get("id")
            if qid in done:
                print(f"skip id={qid} (already processed)")
                continue

            # Fresh KG per question so entities/relations do not bleed across items.
            system.kg = amg.MedicalKnowledgeGraph()

            record = {
                "id": qid,
                "question": item.get("question", ""),
                "reference": item.get("reference", ""),
            }
            # Benchmark items carry gold labels (bench_gene/bench_drug/bench_label/...).
            # Pass them through so results are self-contained for the evaluator.
            record.update({k: v for k, v in item.items() if k.startswith("bench_")})
            try:
                result = system.answer_open_question({
                    "id": qid,
                    "question": item.get("question", ""),
                    "reference": item.get("reference", ""),
                })
                record.update({
                    "generated_answer": result.get("answer", ""),
                    "diagnosis": result.get("diagnosis", ""),
                    "drugs": result.get("drugs", []),
                    "tests": result.get("tests", []),
                    "risk_genes": result.get("risk_genes", []),
                    "reasoning": result.get("reasoning", ""),
                    "graph_stats": result.get("graph_stats", {}),
                    "search_context": result.get("search_context", ""),
                    # Provenance (phase 4+): deduped citations + full retrieval log.
                    "references": result.get("references", []),
                    "evidence_log": result.get("evidence_log", []),
                    # Phases 8/9: how the combined queries were shaped (arity, back-offs, hits).
                    "search_shape": result.get("search_shape", []),
                    # Phase 10 digest stage: per-paper relevant paragraphs + summaries.
                    "paper_digests": result.get("paper_digests", []),
                    # Phase 11: per-gene confidence + contradictions between sources.
                    "gene_ledger": result.get("gene_ledger", []),
                    # Phase 13: status + explanation per gene-drug pair.
                    "contradiction_cards": result.get("contradiction_cards", []),
                })
                if result.get("error"):
                    record["error"] = result["error"]
            except Exception as e:
                record["generated_answer"] = ""
                record["error"] = f"{type(e).__name__}: {e}"
                traceback.print_exc()

            failed = (not record.get("generated_answer", "").strip()
                      or record.get("generated_answer") == FALLBACK_ANSWER)
            if failed:
                n_err += 1
                consecutive_failures += 1
            else:
                n_ok += 1
                consecutive_failures = 0
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()
            print(f"done id={qid} | ok={n_ok} err={n_err} | "
                  f"answer_len={len(record.get('generated_answer', ''))}")

            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"\nABORT: {consecutive_failures} consecutive failures "
                      f"(last error: {record.get('error', 'n/a')}). "
                      f"The LLM endpoint is likely offline; re-run to resume.")
                sys.exit(1)

    print(f"\nFinished. ok={n_ok} err={n_err}. Results -> {args.output}")


if __name__ == "__main__":
    main()
