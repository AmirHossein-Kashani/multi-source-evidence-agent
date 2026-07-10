"""Convert the raw GenMedGPT-5k dataset into AMG-RAG's open-ended JSONL format.

Input : dataset/GenMedGPT-5k/GenMedGPT-5k.raw.json   (HuggingFace wangrongsheng/GenMedGPT-5k-en)
         a JSON list of {"instruction", "input", "output"}
Output: dataset/GenMedGPT-5k/genmedgpt5k.jsonl
         one line per item: {"id": i, "question": <input>, "reference": <output>}

If the raw file is missing, it is downloaded from HuggingFace (login node has internet).

Usage:
    python convert_genmedgpt.py                 # full 5452-item file
    python convert_genmedgpt.py --limit 5       # writes genmedgpt5k_debug.jsonl (5 items)
"""
import argparse
import json
import os
import urllib.request

RAW_URL = "https://huggingface.co/datasets/wangrongsheng/GenMedGPT-5k-en/resolve/main/GenMedGPT-5k.json"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "GenMedGPT-5k")
RAW_PATH = os.path.join(DATA_DIR, "GenMedGPT-5k.raw.json")


def ensure_raw():
    if os.path.exists(RAW_PATH):
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Downloading GenMedGPT-5k from {RAW_URL} ...")
    req = urllib.request.Request(RAW_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(RAW_PATH, "wb") as f:
        f.write(r.read())
    print(f"Saved to {RAW_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="If set, write only the first N items to a *_debug.jsonl file.")
    args = ap.parse_args()

    ensure_raw()
    records = json.load(open(RAW_PATH, encoding="utf-8"))
    print(f"Loaded {len(records)} raw records.")

    if args.limit:
        records = records[: args.limit]
        out_path = os.path.join(DATA_DIR, "genmedgpt5k_debug.jsonl")
    else:
        out_path = os.path.join(DATA_DIR, "genmedgpt5k.jsonl")

    n = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for i, rec in enumerate(records):
            question = (rec.get("input") or "").strip()
            reference = (rec.get("output") or "").strip()
            if not question:
                continue
            f.write(json.dumps({"id": i, "question": question, "reference": reference},
                               ensure_ascii=False) + "\n")
            n += 1
    print(f"Wrote {n} items to {out_path}")


if __name__ == "__main__":
    main()
