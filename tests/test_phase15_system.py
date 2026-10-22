"""Structural test of the phase-15 loop inside AMG_RAG_System, with PubMed and the digest
chain replaced by deterministic fakes (no LLM, no network). Run under the cluster modules."""
import os, sys, importlib.util, hashlib
os.environ.update({
    "LLM_BASE_URL": "http://127.0.0.1:1/v1", "LLM_MODEL": "fake", "AMG_USE_EXTERNAL": "0",
    "AMG_KB_SOURCE": "pharmgkb+pubmed_combo", "AMG_PAPER_DIGEST": "1", "AMG_EVIDENCE_LEDGER": "1",
    "AMG_CONTRADICTION_LAYER": "1", "AMG_PATH_DISCOVERY": "1", "AMG_SEARCH_ROUNDS": "2",
    "AMG_FOLLOWUP_SEARCH": "1", "AMG_QUERY_BUDGET": "6", "AMG_MESH_ONLINE": "0",
    "HF_HUB_OFFLINE": "1", "AMG_ANSWER_STYLE": "adr",
})
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
spec = importlib.util.spec_from_file_location("amg", os.path.join(REPO, "AMG-with-KG.py"))
amg = importlib.util.module_from_spec(spec); spec.loader.exec_module(amg)

S = amg.AMG_RAG_System(use_openai=True, openai_key="ollama")
q = "Which genetic variants put a child with neuroblastoma at higher risk of cisplatin-induced hearing loss?"

# ---- fakes ------------------------------------------------------------------------
def pmid_of(term): return str(200000 + int(hashlib.md5(term.encode()).hexdigest(), 16) % 700000)
def fake_search(term, max_results=2):
    p = pmid_of(term)
    return [{"source": "PubMed", "ref": f"PMID:{p}", "pmid": p, "title": f"Study: {term[:50]}",
             "abstract": "fake", "text": f"[PMID {p}] fake", "pub_types": ["Journal Article"]}]
def fake_fetch(pmids): return [{"pmid": p, "abstract": "fake", "pub_types": []} for p in pmids]
S.pubmed.search_detailed = fake_search
S.pubmed.fetch_by_pmids = fake_fetch
S.pubmed.fetch_fulltext = lambda pmid, max_chars=0: None
def fake_digest(question, paper):
    gene = (paper.get("edge") or "ACYP2|cisplatin|hearing loss").split("|")[0]
    drugs = ["methotrexate"] if gene == "HNF1B" else ["cisplatin"]       # one off-drug paper
    return {"ref": paper["ref"], "pmid": paper["pmid"], "title": paper.get("title", ""),
            "source": "abstract", "via": paper.get("via", ""),
            "proposed_via": paper.get("proposed_via", ""), "edge": paper.get("edge", ""),
            "n_paragraphs": 1, "batches_read": 1, "batches_total": 1,
            "study_type": "human_cohort", "study_type_llm": "human_cohort", "pub_types": [],
            "drugs_studied": drugs, "evidence_kind": "germline_variant",
            "genes_supported": [gene], "genes_refuted": [],
            "population": "children", "cancer_type": "", "endpoint": "hearing loss",
            "dose_context": "", "direction": "increases",
            "paragraphs": [{"ref": paper["ref"] + "#p1", "idx": 1, "section": "Results", "text": "fake"}],
            "summary": f"{gene} associated with hearing loss"}
S._digest_one_paper = fake_digest

# ---- per-question state, as answer_open_question sets it ---------------------------
S.evidence_log, S._phrase_cache, S.combo_stats, S.paper_digests = [], {}, [], []
S.gene_ledger, S.contradiction_cards, S._current_question = [], [], q
S.path_candidates, S.rounds, S.off_drug_claims, S._digest_cache = [], [], [], {}
S.edge_queue = amg.EdgeQueue()
S._seed_pgx_edges(q, {})                               # curated edges into the KG, as build_knowledge_graph does
print("KG after seeding:", len(S.kg.entities), "entities", len(S.kg.relations), "relations")

d, l, c = S._assess_evidence(q)
print("\n== base assessment: ledger groups", len(S.gene_ledger), "| cards", len(S.contradiction_cards))
d, l, c = S._run_search_rounds(q, d, l, c)

print("\n== rounds")
for r in S.rounds:
    print(f"  round {r['round']}: {len(r['queries'])} queries, new papers {r['new_papers']}, strong {r['new_strong_papers']}, written {r['edges_written']}, queue {r['queue']}")
    for qq in r["queries"][:6]:
        print(f"     {qq['provenance']:22s} {' AND '.join(qq['terms'])[:95]}")
print("\n== path candidates:", [(x["gene"], x["prior"]) for x in S.path_candidates[:6]])
cands = [e for e in S.gene_ledger if e.get("candidate")]
print("== ledger candidates:", [(e["gene"], e["outcome"], e["confidence"], e["proposed_via"]) for e in cands][:6])
print("== off-drug claims:", S.off_drug_claims)
lit = [r for r in S.kg.relations if r.relation_type.startswith("literature_supported")]
print("== literature edges written back:", [(r.source, r.target, r.relation_type, round(r.confidence, 2)) for r in lit][:6])
print("\n--- ledger prompt (tail) ---\n" + "\n".join(l.splitlines()[-12:]))
assert S.rounds, "no round ran"
assert any(e["proposed_via"] for e in S.gene_ledger), "entries should carry their proposing path"
print("== entries with proposed_via:", [(e["gene"], e["proposed_via"]) for e in S.gene_ledger if e["proposed_via"]][:6])
issued=[tuple(q["terms"]) for r in S.rounds for q in r["queries"]]; assert len(issued)==len(set(issued)), "a query was issued twice"
assert any(cl["drugs_studied"] == ["methotrexate"] for cl in S.off_drug_claims), "off-drug paper must be excluded"
assert sum(r["edges_written"] for r in S.rounds) > 0, "write-back missing"
print("\nSTRUCTURAL TEST OK")
