"""Convert the PharmGKB / ADR dataset into AMG-RAG's open-ended JSONL format (Framing 1).

The PharmGKB tables are a pharmacogenomics knowledge base, NOT a Q&A set: every row is a
fact. This turns each variant annotation into a (question, reference) pair by templating a
question from the structured fields (gene / variant / drug) and using the curated,
plain-English `Sentence` field as the gold reference answer -- exactly the schema that
run_genmedgpt.py / eval_genmedgpt.py already consume for GenMedGPT-5k.

Input : dataset/ADR_DataSet/.../variantAnnotations/var_drug_ann.tsv   (12,975 rows)
        (optionally var_pheno_ann.tsv with --source both)
Output: dataset/PharmGKB/pharmgkb.jsonl
        one line per item: {"id", "question", "reference", + metadata}

No answer leakage: the question names only the gene/variant/drug; the effect/direction it
asks about lives only in the reference `Sentence`.

Usage:
    python convert_pharmgkb.py                     # var_drug_ann -> pharmgkb.jsonl
    python convert_pharmgkb.py --source both       # + var_pheno_ann
    python convert_pharmgkb.py --limit 5           # small pharmgkb_debug.jsonl smoke test
"""
import argparse
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ADR_ROOT = os.path.join(HERE, "dataset", "ADR_DataSet")
OUT_DIR = os.path.join(HERE, "dataset", "PharmGKB")

MIN_SENTENCE_LEN = 20  # drop stubs that make useless references


def find_tsv(filename):
    """Locate a TSV under the (possibly nested) extracted ADR_DataSet tree."""
    hits = glob.glob(os.path.join(ADR_ROOT, "**", filename), recursive=True)
    if not hits:
        sys.exit(f"ERROR: could not find {filename} under {ADR_ROOT}. "
                 f"Did you unzip ADR_DataSet.zip into dataset/ADR_DataSet/ ?")
    return hits[0]


def make_question(gene, variant, drug):
    """Template a natural pharmacogenomics question whose answer is the row's Sentence."""
    gene = (gene or "").strip()
    variant = (variant or "").strip()
    drug = (drug or "").strip().replace(";", ", ")

    # Subject: prefer "variant (gene)", fall back to whichever exists.
    if variant and gene and gene not in variant:
        subj = f"{variant} ({gene})"
    else:
        subj = variant or gene

    if not subj:
        return None
    if drug:
        return (f"What is the known pharmacogenomic effect of the {subj} "
                f"variant on {drug}?")
    return (f"What is the known clinical or pharmacogenomic significance of the "
            f"{subj} variant?")


def rows_from(path, source_tag):
    """Yield converted records from a var_*_ann.tsv file."""
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            sentence = (row.get("Sentence") or "").strip()
            if len(sentence) < MIN_SENTENCE_LEN:
                continue
            gene = row.get("Gene", "")
            variant = row.get("Variant/Haplotypes", "")
            drug = row.get("Drug(s)", "")
            question = make_question(gene, variant, drug)
            if not question:
                continue
            yield {
                "question": question,
                "reference": sentence,
                "src": source_tag,
                "ann_id": row.get("Variant Annotation ID", ""),
                "gene": gene.strip(),
                "variant": variant.strip(),
                "drug": drug.strip(),
                "category": (row.get("Phenotype Category") or "").strip(),
                "significance": (row.get("Significance") or "").strip(),
                "direction": (row.get("Direction of effect") or "").strip(),
            }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["drug", "pheno", "both"], default="drug",
                    help="Which variant-annotation table(s) to convert (default: drug).")
    ap.add_argument("--limit", type=int, default=None,
                    help="If set, write only the first N items to pharmgkb_debug.jsonl.")
    args = ap.parse_args()

    sources = []
    if args.source in ("drug", "both"):
        sources.append((find_tsv("var_drug_ann.tsv"), "var_drug_ann"))
    if args.source in ("pheno", "both"):
        sources.append((find_tsv("var_pheno_ann.tsv"), "var_pheno_ann"))

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(
        OUT_DIR, "pharmgkb_debug.jsonl" if args.limit else "pharmgkb.jsonl")

    seen = set()  # dedup identical (question, reference) pairs
    n = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for path, tag in sources:
            print(f"Reading {tag} <- {path}")
            for rec in rows_from(path, tag):
                key = (rec["question"], rec["reference"])
                if key in seen:
                    continue
                seen.add(key)
                rec = {"id": n, **rec}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
                if args.limit and n >= args.limit:
                    print(f"Wrote {n} items (limit) to {out_path}")
                    return
    print(f"Wrote {n} items to {out_path}")


if __name__ == "__main__":
    main()
