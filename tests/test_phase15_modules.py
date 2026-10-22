import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mesh_terms import MeshVocab, outcome_family
from pgx_kb import PharmGKBSearcher, PHENO_SYNONYMS
from graph_paths import ClinPGxGraph, propose_for_question
from edge_queue import EdgeQueue

v = MeshVocab()
print("== MeSH")
for d in ["cisplatin", "doxorubicin", "mercaptopurine", "platinol"]:
    print(f"  parents({d}) = {v.parents(d)}")
print("  synonyms(hearing loss) ⊇", sorted(v.synonyms("hearing loss"))[:6])
print("  heading(hearing impairment) =", v.heading("hearing impairment"))
print("  heading(ototoxicity) =", v.heading("ototoxicity"), "| heading(cardiotoxicity) =", v.heading("cardiotoxicity"))
for t in ["clinically significant hearing loss", "hearing threshold shift", "acute kidney injury", "tinnitus", ""]:
    print(f"  outcome_family({t!r}, 'ototoxicity') = {outcome_family(t, 'ototoxicity', v, PHENO_SYNONYMS)!r}")
print("  cache entries:", len(v.cache))

print("\n== graph_paths")
pgx = PharmGKBSearcher(); G = ClinPGxGraph()
q = "Which genetic variants put a child with neuroblastoma at higher risk of cisplatin-induced hearing loss?"
cands = propose_for_question(G, pgx, q, vocab=v, k=60)
from collections import Counter
print("  candidates:", len(cands), "| by via:", Counter(x for c in cands for x in c["via"]))
for c in cands[:10]:
    print(f"   {c['gene']:9s} prior={c['prior']:.2f} via={c['via']}  | {c['paths'][0][:90]}")
names = {c["gene"] for c in cands}
print("  MLH1/MSH3 proposed via class?", "MLH1" in names, "MSH3" in names, "| curated gene ACYP2 excluded?", "ACYP2" not in names)

print("\n== edge_queue")
Q = EdgeQueue()
for c in cands[:5]:
    Q.add(c["gene"], c["drug"], c["outcome"], provenance=c["via"][0], prior=c["prior"], path=c["paths"][0])
Q.add("ACYP2", "cisplatin", "ototoxicity", provenance="curated")
Q.add("TPMT", "cisplatin", "ototoxicity", provenance="curated")
Q.add("FOO1", "cisplatin", "ototoxicity", provenance="hypothesised")
ledger = [
  {"gene":"ACYP2","drug":"cisplatin","outcome":"ototoxicity","confidence":0.81,"supporting":[{"ref":"ClinPGx:ACYP2"},{"ref":"PMID:1"},{"ref":"PMID:2"}],"refuting":[],
   "components":{"clinpgx_level":"3","support_sources":3,"refute_sources":0,"support_weight":2.7,"refute_weight":0}},
  {"gene":"TPMT","drug":"cisplatin","outcome":"ototoxicity","confidence":0.48,"supporting":[{"ref":"ClinPGx:TPMT"}],"refuting":[{"ref":"PMID:9"}],
   "components":{"clinpgx_level":"3","support_sources":1,"refute_sources":1,"support_weight":1.0,"refute_weight":0.85}},
]
cards = [{"gene":"ACYP2","drug":"cisplatin","outcome":"ototoxicity","status":"CONSISTENT"},
         {"gene":"TPMT","drug":"cisplatin","outcome":"ototoxicity","status":"INSUFFICIENT"}]
Q.update_from_ledger(ledger, cards)
print("  counts:", Q.counts())
sel = Q.select(budget=4, round_no=1)
for e in sel: print(f"   pick {e.gene:9s} status={e.status:12s} prior={e.prior:.2f} u={Q.uncertainty(e):.2f} prio={Q.priority(e):.3f} terms={Q.query_terms(e)}")
assert all(e.gene != "ACYP2" for e in sel), "confirmed edge must not be re-searched"
assert any(e.gene == "TPMT" for e in sel), "INSUFFICIENT curated edge must be selected"
assert sum(e.status == "untested" for e in sel) >= 2, "a third of the budget is reserved for untested edges"
print("  OK")
