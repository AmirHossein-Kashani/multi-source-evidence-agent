"""Extraction test on PGxCorpus (Legrand et al., 2020): does the digest chain pull the right
genes and drugs out of a sentence?

    python eval_pgxcorpus.py --mode dict                 # dictionary baseline, no LLM
    python eval_pgxcorpus.py --mode llm --limit 300      # digest chain (needs LLM_BASE_URL)
    python eval_pgxcorpus.py --score results/pgxcorpus_llm.jsonl results/pgxcorpus_dict.jsonl

Sentences with at least one Gene_or_protein and one Chemical entity are used (874 of 945).
Gold genes = Gene_or_protein mentions; gold drugs = Chemical mentions. The question given
to the digest chain names the sentence's first chemical, as the pipeline would for a paper
retrieved for that drug. Metrics: per-sentence precision / recall / F1 (macro) and micro
P/R/F1, on all gold mentions and on the symbol-like mentions only (a prediction "TPMT"
cannot match the mention "thiopurine methyltransferase"; the symbol-only view removes
that penalty for every system alike). Resume-safe: sentences already in --out are skipped.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "dataset", "PGxCorpus", "data")
_SYM = re.compile(r"^[A-Z][A-Z0-9]{1,9}(-[A-Z0-9]+)?$")


def _n(s):
    return " ".join(str(s or "").strip().split())


def load_corpus():
    out = []
    for ann in sorted(glob.glob(os.path.join(DATA, "*.ann"))):
        sid = os.path.basename(ann)[:-4]
        text = open(ann[:-4] + ".txt", encoding="utf-8").read().strip()
        ents = {}
        equiv = []
        for ln in open(ann, encoding="utf-8"):
            p = ln.rstrip("\n").split("\t")
            if p[0].startswith("T") and len(p) >= 3:
                ents[p[0]] = (p[1].split(" ")[0], _n(p[2]))
            elif p[0].startswith("R"):
                m = re.match(r"isEquivalentTo Arg1:(\S+) Arg2:(\S+)", p[1])
                if m:
                    equiv.append((m[1], m[2]))
        genes = {t for ty, t in ents.values() if ty == "Gene_or_protein"}
        drugs = {t.lower() for ty, t in ents.values() if ty == "Chemical"}
        if not genes or not drugs:
            continue
        # equivalence classes among gene mentions ("TPMT" == "thiopurine methyltransferase")
        groups = []
        for a, b in equiv:
            ta, tb = ents.get(a, ("", ""))[1], ents.get(b, ("", ""))[1]
            if ta in genes and tb in genes:
                groups.append({ta, tb})
        out.append({"id": sid, "text": text, "gold_genes": sorted(genes), "gold_drugs": sorted(drugs),
                    "gene_groups": [sorted(g) for g in groups],
                    "drug": sorted(drugs, key=lambda d: text.lower().find(d))[0]})
    return out


def gene_match(pred, gold_mentions, groups):
    """A gold mention counts as found if the prediction equals it, is a token of it, or
    matches an equivalent mention."""
    pu = pred.upper()
    for g in gold_mentions:
        toks = {g.upper()} | set(re.findall(r"[A-Z][A-Z0-9]{1,9}", g.upper()))
        if pu in toks:
            return g
        for grp in groups:
            if g in grp and any(pu == x.upper() or pu in re.findall(r"[A-Z][A-Z0-9]{1,9}", x.upper()) for x in grp):
                return g
    return None


def score(rows):
    agg = defaultdict(list)
    micro = defaultdict(int)
    for r in rows:
        for view in ("all", "symbols"):
            gold_g = [g for g in r["gold_genes"] if view == "all" or _SYM.match(g.upper())]
            if not gold_g:
                continue
            # a star allele or a variant suffix names the gene ("HLA-B*57:01" -> HLA-B)
            pred_g = sorted({re.sub(r"\s*[\*(].*$", "", _n(g)).strip().upper() for g in r["pred_genes"] if _n(g)})
            hit_gold = {gene_match(p, gold_g, r["gene_groups"]) for p in pred_g} - {None}
            tp = len(hit_gold); fp = sum(1 for p in pred_g if gene_match(p, gold_g, r["gene_groups"]) is None)
            fn = len(gold_g) - tp
            P = tp / (tp + fp) if tp + fp else 0.0; R = tp / len(gold_g); F = 2 * P * R / (P + R) if P + R else 0.0
            agg[f"gene[{view}]:P"].append(P); agg[f"gene[{view}]:R"].append(R); agg[f"gene[{view}]:F1"].append(F)
            micro[f"gene[{view}]:tp"] += tp; micro[f"gene[{view}]:fp"] += fp; micro[f"gene[{view}]:fn"] += fn
        pred_d = {_n(d).lower() for d in r["pred_drugs"] if _n(d)}
        gold_d = set(r["gold_drugs"])
        hit_g = {g for g in gold_d if any(p == g or p in g or g in p for p in pred_d)}
        fp = sum(1 for p in pred_d if not any(p == g or p in g or g in p for g in gold_d))
        tp = len(hit_g); fn = len(gold_d) - tp
        P = tp / (tp + fp) if tp + fp else 0.0; R = tp / len(gold_d) if gold_d else 0.0
        F = 2 * P * R / (P + R) if P + R else 0.0
        agg["drug:P"].append(P); agg["drug:R"].append(R); agg["drug:F1"].append(F)
        micro["drug:tp"] += tp; micro["drug:fp"] += fp; micro["drug:fn"] += fn
    out = {k: sum(v) / len(v) for k, v in agg.items()}
    for key in ("gene[all]", "gene[symbols]", "drug"):
        tp, fp, fn = micro[f"{key}:tp"], micro[f"{key}:fp"], micro[f"{key}:fn"]
        P = tp / (tp + fp) if tp + fp else 0.0; R = tp / (tp + fn) if tp + fn else 0.0
        out[f"{key}:microF1"] = 2 * P * R / (P + R) if P + R else 0.0
    out["n"] = len(rows)
    return out


def run_dict(corpus, out_path):
    from pgx_kb import PharmGKBSearcher
    pgx = PharmGKBSearcher()
    gv = {g.upper() for g in pgx.gene_vocab if len(g) >= 3}
    with open(out_path, "w", encoding="utf-8") as f:
        for s in corpus:
            toks = set(re.findall(r"\b[A-Za-z][A-Za-z0-9]{1,9}\b", s["text"]))
            genes = sorted({t.upper() for t in toks if t.upper() in gv and (any(c.isdigit() for c in t) or t.isupper())})
            drugs = sorted({d for d in pgx.drug_vocab if len(d) >= 4 and
                            re.search(r"(?<![a-z0-9])" + re.escape(d) + r"(?![a-z0-9])", s["text"].lower())})
            f.write(json.dumps({**s, "pred_genes": genes, "pred_drugs": drugs, "system": "dict"}) + "\n")


def run_llm(corpus, out_path, limit):
    spec = importlib.util.spec_from_file_location("amg", os.path.join(HERE, "AMG-with-KG.py"))
    amg = importlib.util.module_from_spec(spec); spec.loader.exec_module(amg)
    S = amg.AMG_RAG_System(use_openai=True, openai_key=os.environ.get("OPENAI_API_KEY", "ollama"))
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["id"] for l in open(out_path, encoding="utf-8")}
    todo = [s for s in corpus if s["id"] not in done][: (limit or len(corpus))]
    print(f"[pgxcorpus] {len(done)} done, {len(todo)} to run")
    with open(out_path, "a", encoding="utf-8") as f:
        for i, s in enumerate(todo, 1):
            q = (f"Which genes or variants influence the response to, or adverse effects of, "
                 f"{s['drug']}?")
            try:
                res = S.paper_digest_chain.invoke({"question": q, "title": "",
                                                   "paragraphs": f"[0] {s['text']}"})
            except Exception as e:
                print(f"[pgxcorpus] {s['id']} failed: {e}")
                res = {}
            rec = {**s, "system": "llm",
                   "pred_genes": [str(g) for g in (res.get("genes_supported") or []) + (res.get("genes_refuted") or [])],
                   "pred_drugs": [str(d) for d in (res.get("drugs_studied") or [])],
                   "study_type": res.get("study_type", ""), "evidence_kind": res.get("evidence_kind", ""),
                   "direction": res.get("direction", "")}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if i % 25 == 0:
                print(f"[pgxcorpus] {i}/{len(todo)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dict", "llm"])
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--score", nargs="*")
    args = ap.parse_args()
    corpus = load_corpus()
    print(f"[pgxcorpus] {len(corpus)} usable sentences")
    if args.mode == "dict":
        run_dict(corpus, args.out or os.path.join(HERE, "results", "pgxcorpus_dict.jsonl"))
    elif args.mode == "llm":
        run_llm(corpus, args.out or os.path.join(HERE, "results", "pgxcorpus_llm.jsonl"), args.limit)
    if args.score:
        tables = {}
        for p in args.score:
            rows = [json.loads(l) for l in open(p, encoding="utf-8")]
            tables[os.path.basename(p)] = score(rows)
        keys = sorted({k for t in tables.values() for k in t})
        print("| metric | " + " | ".join(tables) + " |")
        print("|---|" + "---|" * len(tables))
        for k in keys:
            print(f"| {k} | " + " | ".join(f"{tables[t][k]:.3f}" if isinstance(tables[t].get(k), float) else str(tables[t].get(k, '-')) for t in tables) + " |")


if __name__ == "__main__":
    main()
