"""Build a local PubMed abstract corpus for the external baselines (PaperQA2, LightRAG).

The open-source PaperQA2 agent and LightRAG answer over a LOCAL document set, so each gets
the same corpus: for every drug / gene named in the benchmark questions, the top PubMed
abstracts for "<term> AND (pharmacogenomic OR pharmacogenetic OR polymorphism OR genotype
OR variant)" plus, for the masked-recovery drugs, "<drug> AND <outcome>". PubMed's own search
is used, as in our pipeline; no ClinPGx information enters the corpus.

    python extbase/build_pubmed_corpus.py --out /scratch/kashi77/ext_baselines/corpus_pubmed \
        --per-term 80

Writes one UTF-8 text file per article (PMID_<id>.txt: title, journal/year, abstract) and
corpus_manifest.json (term -> PMIDs). Resume-safe.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PGX = "(pharmacogenomic OR pharmacogenetic OR polymorphism OR genotype OR variant OR allele)"
_last = 0.0


def _get(endpoint, params):
    global _last
    wait = 0.4 - (time.monotonic() - _last)
    if wait > 0:
        time.sleep(wait)
    key = os.environ.get("pubmed_api") or os.environ.get("PUBMED_API_KEY")
    if key:
        params = {**params, "api_key": key}
    url = f"{EUTILS}/{endpoint}.fcgi?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "amg-extbase/1.0"}), timeout=60) as r:
                data = r.read().decode("utf-8", "replace")
            _last = time.monotonic()
            return data
        except Exception as e:
            time.sleep(2 + 2 * attempt)
            err = e
    raise err


def esearch(term, retmax):
    root = ET.fromstring(_get("esearch", {"db": "pubmed", "term": term, "retmax": retmax, "sort": "relevance"}))
    return [e.text for e in root.findall(".//Id") if e.text]


def efetch(pmids):
    out = {}
    for i in range(0, len(pmids), 100):
        root = ET.fromstring(_get("efetch", {"db": "pubmed", "id": ",".join(pmids[i:i + 100]), "retmode": "xml"}))
        for art in root.findall(".//PubmedArticle"):
            pmid = (art.findtext(".//MedlineCitation/PMID") or "").strip()
            title = " ".join("".join(art.find(".//ArticleTitle").itertext()).split()) if art.find(".//ArticleTitle") is not None else ""
            abstract = " ".join(" ".join(a.itertext()) for a in art.findall(".//Abstract/AbstractText")).strip()
            journal = art.findtext(".//Journal/Title") or ""
            year = art.findtext(".//JournalIssue/PubDate/Year") or ""
            if pmid and abstract:
                out[pmid] = {"title": title, "abstract": " ".join(abstract.split()), "journal": journal, "year": year}
    return out


def terms_from_benchmarks():
    terms = []
    p = os.path.join(HERE, "dataset", "PGxQA", "pgxqa_eval.jsonl")
    for it in map(json.loads, open(p, encoding="utf-8")):
        q = it["question"]
        if it.get("bench_drug"):
            terms.append((it["bench_drug"], f"{it['bench_drug']} AND {PGX}"))
        elif it.get("bench_key"):
            terms.append((it["bench_key"], f"{it['bench_key']} AND {PGX}"))
        else:
            m = re.search(r"patient ([A-Za-z0-9\-]+)\.|guidelines for ([A-Za-z0-9\-\*]+)\?", q)
            name = next((x for x in (m.groups() if m else ()) if x), "")
            if name:
                terms.append((name, f"{name} AND {PGX}"))
            else:                                    # consult questions: use the question itself
                words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9\*\-]{3,}", q) if w.lower() not in
                         {"patient", "patients", "which", "there", "should", "would", "about", "testing", "their", "they", "what", "this", "that", "with", "from", "have", "been", "dosing", "guide"}]
                terms.append((q[:40], " AND ".join(words[:4]) + f" AND {PGX}"))
    m = os.path.join(HERE, "dataset", "ADR_DataSet_masked", "masked_pairs.json")
    if os.path.exists(m):
        for pr in json.load(open(m)):
            terms.append((f"{pr['drug']}-{pr['outcome']}", f"{pr['drug']} AND {pr['outcome']} AND {PGX}"))
            terms.append((f"{pr['drug']}-{pr['outcome']}-broad", f"{pr['drug']} AND ({pr['outcome']} OR toxicity)"))
    seen, out = set(), []
    for k, t in terms:
        if t not in seen:
            seen.add(t); out.append((k, t))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-term", type=int, default=80)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    mpath = os.path.join(args.out, "corpus_manifest.json")
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    terms = terms_from_benchmarks()
    print(f"[corpus] {len(terms)} search terms")
    have = {f[5:-4] for f in os.listdir(args.out) if f.startswith("PMID_") and f.endswith(".txt")}
    for i, (key, term) in enumerate(terms, 1):
        if term in manifest:
            continue
        try:
            pmids = esearch(term, args.per_term)
        except Exception as e:
            print(f"[corpus] esearch failed for {term!r}: {e}"); continue
        new = [p for p in pmids if p not in have]
        arts = efetch(new) if new else {}
        for pmid, a in arts.items():
            with open(os.path.join(args.out, f"PMID_{pmid}.txt"), "w", encoding="utf-8") as f:
                f.write(f"{a['title']}\n\nPMID: {pmid}. {a['journal']} ({a['year']}).\n\n{a['abstract']}\n")
            have.add(pmid)
        manifest[term] = {"key": key, "pmids": pmids}
        json.dump(manifest, open(mpath, "w"), indent=0)
        print(f"[corpus] {i}/{len(terms)} {key[:30]:30s} {len(pmids):3d} pmids, {len(arts):3d} new abstracts (total {len(have)})")
    print(f"[corpus] done: {len(have)} articles in {args.out}")


if __name__ == "__main__":
    main()
