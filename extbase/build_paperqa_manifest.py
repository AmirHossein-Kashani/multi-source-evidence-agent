"""Manifest CSV for PaperQA2's index build (IndexSettings.manifest_file).

Without a manifest PaperQA2 asks the LLM for a citation for every file it indexes (~2.6 s
per abstract here, ~2.7 h for the corpus, and the result is only a display string). The
corpus files carry title, journal and year in their first lines, so the manifest supplies
them and indexing needs embeddings only. Columns are DocDetails attributes; file_location is
the absolute path (the runner indexes with use_absolute_paper_directory=True).

    python extbase/build_paperqa_manifest.py --corpus /scratch/kashi77/ext_baselines/corpus_pubmed
        -> <corpus parent>/paperqa_manifest.csv
"""
import argparse
import csv
import os
import re

META = re.compile(r"^PMID:\s*(\d+)\.\s*(.*?)\s*\((\d{4})\)\.?\s*$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    corpus = os.path.abspath(args.corpus)
    out = args.out or os.path.join(os.path.dirname(corpus), "paperqa_manifest.csv")
    n = n_meta = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file_location", "title", "journal", "year", "doi"])
        for name in sorted(os.listdir(corpus)):
            if not (name.startswith("PMID_") and name.endswith(".txt")):
                continue
            lines = [l.strip() for l in open(os.path.join(corpus, name), encoding="utf-8").read().splitlines()]
            lines = [l for l in lines if l]
            title = lines[0] if lines else name
            journal = year = ""
            for l in lines[1:4]:
                m = META.match(l)
                if m:
                    journal, year = m.group(2), m.group(3); n_meta += 1
                    break
            w.writerow([os.path.join(corpus, name), title, journal, year, ""])
            n += 1
    print(f"wrote {out}: {n} files, {n_meta} with journal/year")


if __name__ == "__main__":
    main()
