import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evidence_ledger import Claim, build_ledger, ledger_to_prompt, compute_confidence
from contradiction_layer import build_cards, followup_queries
from pgx_kb import PharmGKBSearcher
from mesh_terms import MeshVocab
from graph_paths import ClinPGxGraph, propose_for_question

v = MeshVocab(); pgx = PharmGKBSearcher(vocab=v)
print("== class matching")
for g in ["MLH1", "MSH3", "ACYP2", "SLCO1B1"]:
    print(f"  {g}-cisplatin ->", pgx.association_detailed(g, "cisplatin"))
rows = pgx.search_detailed("cisplatin ototoxicity in children", max_results=40)
from collections import Counter
print("  search_detailed match types:", Counter(r["match"] for r in rows), "| class example:",
      next((r["ref"] + " " + r["text"][-70:] for r in rows if r["match"] == "class"), None))

print("\n== ledger")
def lit(gene, pmid, st="human_cohort", stance="supports", **kw):
    return Claim(gene=gene, drug="cisplatin", stance=stance, study_type=st, ref=f"PMID:{pmid}", pmid=str(pmid), source="PubMed", **kw)
claims = [
  Claim(gene="ACYP2", drug="cisplatin", stance="supports", study_type="curated", level="3", source="ClinPGx", ref="ClinPGx:ACYP2:L3", outcome="ototoxicity"),
  lit("ACYP2", 1, outcome="ototoxicity"), lit("ACYP2", 2, outcome="ototoxicity"),
  lit("MLH1", 3, outcome="acute kidney injury"),                 # wrong outcome -> own group
  lit("MLH1", 4, outcome="ototoxicity", drug_match="class"),
  lit("SLCO1B1", 5, outcome="ototoxicity", drug_match="mismatch"),   # methotrexate paper -> excluded
  lit("KCNK17", 6, outcome="cardiotoxicity"), lit("KCNK17", 7, outcome="cardiotoxicity"),   # 2 cohorts, no curated row
  lit("PIGR", 8, outcome="cardiotoxicity", evidence_kind="protein_biomarker"),
  lit("TTN", 9, st="in_vitro", outcome="cardiotoxicity"),
]
L = build_ledger(claims, pgx)
for e in L:
    print(f"  {e['gene']:8s} [{e['outcome']:20s}] conf={e['confidence']:.2f} {e['label']:8s} curated={e['curated']!s:5s} cand={e['candidate']!s:5s} disputed={e['disputed']!s:5s} "
          f"flags={[f['type'] for f in e['contradictions']]} match={e['components'].get('clinpgx_match')} litest={e['components']['literature_established']}")
by = {(e["gene"], e["outcome"]): e for e in L}
assert ("SLCO1B1", "ototoxicity") not in by, "mismatch claim must be excluded"
assert ("MLH1", "acute kidney injury") in by and ("MLH1", "ototoxicity") in by, "outcome must split groups"
assert by[("MLH1","ototoxicity")]["components"]["clinpgx_association"] == "not associated", "class-level negative must be found"
assert by[("KCNK17","cardiotoxicity")]["components"]["literature_established"] and by[("KCNK17","cardiotoxicity")]["label"] == "moderate"
assert by[("KCNK17","cardiotoxicity")]["candidate"] and not by[("KCNK17","cardiotoxicity")]["disputed"]
assert by[("PIGR","cardiotoxicity")]["components"]["support_weight"] == 0.425, "protein biomarker should weigh half"
print("  10 meta-analyses, no curated row ->", round(compute_confidence("", None, [lit("X", i, "meta_analysis") for i in range(10)], [])[0], 2), "(must stay < 0.75)")
print("\n--- prompt ---"); print(ledger_to_prompt(L, max_entries=2))

print("\n== cards + follow-ups")
cbp = {}
for c in claims:
    if c.drug_match == "mismatch": continue
    k = (c.gene, c.drug, c.outcome); cbp.setdefault(k, ([], []))[0 if c.stance=="supports" else 1].append(c)
cards = build_cards(L, cbp, pgx)
print("  statuses:", Counter(c["status"] for c in cards))
for q in followup_queries(cards, "ototoxicity")[:4]:
    print(f"   {q['provenance']:24s} {' AND '.join(q['terms'])}")

print("\n== path priors after fix")
G = ClinPGxGraph()
top = propose_for_question(G, pgx, "cisplatin-induced hearing loss in children", vocab=v, k=5)
print("  ", [(c["gene"], c["prior"], c["via"]) for c in top])
assert max(c["prior"] for c in top) <= 0.6, "single-pattern prior must not exceed its PRIOR"
print("ALL OK")
