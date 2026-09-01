"""Contradiction resolution: normalise claims, group them, and explain WHY sources disagree.

The evidence ledger answers *whether* sources conflict. That is not enough: a count of
contradictions rewards retrieving more mechanistic papers, because an in-vitro study reporting
no effect is scored like a clinical replication failure. Two things are needed beyond it.

**Comparability.** Evidence is classified into tiers -- curated, clinical (human association
studies), mechanistic (animal / in vitro), narrative (reviews). A mechanistic result that
disagrees with a clinical association is NOT a clinical contradiction; it is mechanistic
context. Only claims in comparable tiers can conflict with each other.

**Explanation.** When comparable claims do disagree, the disagreement is typed by the axis it
falls on -- population, cancer type, dose, endpoint, direction, or study design -- so that an
apparent conflict that dissolves once context is taken into account is reported as
CONTEXT-DEPENDENT rather than as a conflict.

Each (drug, gene, phenotype) group is resolved to one status:

    CONSISTENT                 comparable credible evidence agrees
    CONFLICTING                comparable credible evidence supports both directions
    CONTEXT-DEPENDENT          the conflict disappears once population / dose / type is fixed
    CURATED-LITERATURE CONFLICT  the curated database and recent literature disagree
    INSUFFICIENT               too little comparable evidence to judge

No LLM call happens here: the model extracts the fields, this module decides.
"""
from collections import Counter, defaultdict
from typing import Dict, List, Optional

# Which kinds of evidence can contradict each other. A curated clinical association and an
# in-vitro assay are not commensurable, so they are never scored as a direct conflict.
TIER = {
    "curated": "curated",
    "meta_analysis": "clinical", "systematic_review": "clinical", "gwas": "clinical",
    "human_cohort": "clinical", "clinical_trial": "clinical", "case_report": "clinical",
    "animal": "mechanistic", "in_vitro": "mechanistic",
    "review": "narrative", "unknown": "narrative",
}
# Study designs ranked by the weight the field gives them, used to explain design conflicts.
DESIGN_RANK = {"meta_analysis": 5, "systematic_review": 5, "gwas": 4, "clinical_trial": 3,
               "human_cohort": 3, "case_report": 1, "curated": 4,
               "animal": 1, "in_vitro": 1, "review": 1, "unknown": 1}

# Context axes compared between the supporting and refuting sides of a group. Order matters:
# the first axis that separates the two sides is reported as the explanation.
CONTEXT_AXES = [
    ("population", "population differs (e.g. children vs adults)"),
    ("cancer_type", "cancer type differs"),
    ("dose_context", "dose or regimen differs"),
    ("endpoint", "endpoint differs (e.g. threshold shift vs clinically significant loss)"),
]

STATUS_CONSISTENT = "CONSISTENT"
STATUS_CONFLICTING = "CONFLICTING"
STATUS_CONTEXT = "CONTEXT-DEPENDENT"
STATUS_CURATED_CONFLICT = "CURATED-LITERATURE CONFLICT"
STATUS_INSUFFICIENT = "INSUFFICIENT"


def _norm(v) -> str:
    v = " ".join(str(v or "").strip().lower().split())
    return "" if v in ("", "unknown", "n/a", "none", "not reported", "unspecified") else v


def tier_of(claim) -> str:
    return TIER.get(_norm(getattr(claim, "study_type", "")) .replace(" ", "_"), "narrative")


def _ctx(claim, axis: str) -> str:
    return _norm(getattr(claim, axis, "") or (claim.get(axis) if isinstance(claim, dict) else ""))


def _side_values(claims, axis) -> set:
    return {_ctx(c, axis) for c in claims if _ctx(c, axis)}


def _explain_axis(supporting, refuting) -> Optional[dict]:
    """First context axis on which the two sides do not overlap -- i.e. the apparent conflict
    is explained by studying different things rather than by disagreeing."""
    for axis, description in CONTEXT_AXES:
        sup, ref = _side_values(supporting, axis), _side_values(refuting, axis)
        if sup and ref and not (sup & ref):
            return {"axis": axis, "detail": description,
                    "supporting_values": sorted(sup), "refuting_values": sorted(ref)}
    return None


def _design_note(supporting, refuting) -> Optional[dict]:
    """A conflict where the two sides sit at clearly different levels of evidence."""
    def top(cs):
        return max((DESIGN_RANK.get(_norm(getattr(c, "study_type", "")), 1) for c in cs),
                   default=0)
    s, r = top(supporting), top(refuting)
    if abs(s - r) >= 2:
        stronger = "refuting" if r > s else "supporting"
        return {"axis": "study_design",
                "detail": f"the {stronger} side rests on a stronger design "
                          f"(rank {max(s, r)} vs {min(s, r)})"}
    return None


def _direction_conflict(supporting) -> Optional[dict]:
    """Same side of the argument, opposite reported effect directions."""
    dirs = {_ctx(c, "direction") for c in supporting if _ctx(c, "direction")}
    opposed = {"increases", "increased", "higher", "risk"} & dirs and \
              {"decreases", "decreased", "lower", "protective"} & dirs
    if opposed:
        return {"axis": "direction",
                "detail": "the same association is reported in opposite directions",
                "values": sorted(dirs)}
    return None


def resolve_group(supporting: List, refuting: List, curated_assoc: Optional[str],
                  min_sources: int = 2) -> dict:
    """Status + explanation for one (drug, gene, phenotype) group."""
    by_tier = defaultdict(lambda: {"support": [], "refute": []})
    for c in supporting:
        by_tier[tier_of(c)]["support"].append(c)
    for c in refuting:
        by_tier[tier_of(c)]["refute"].append(c)

    clin_sup = by_tier["clinical"]["support"] + by_tier["curated"]["support"]
    clin_ref = by_tier["clinical"]["refute"] + by_tier["curated"]["refute"]
    mech_sup = by_tier["mechanistic"]["support"]
    mech_ref = by_tier["mechanistic"]["refute"]

    reasons, notes = [], []
    if mech_ref and not clin_ref:
        notes.append("the only refuting evidence is mechanistic (animal / in vitro); it "
                     "qualifies the mechanism but does not contradict a clinical association")
    if mech_sup and not clin_sup:
        notes.append("support is mechanistic only; no human association evidence was found")

    # curated vs literature is its own status: the database and recent work disagree
    lit_sup = [c for c in clin_sup if tier_of(c) != "curated"]
    lit_ref = [c for c in clin_ref if tier_of(c) != "curated"]
    curated_side = "support" if curated_assoc == "associated" else (
        "refute" if curated_assoc == "not associated" else "")

    n_comparable = len(clin_sup) + len(clin_ref)
    if n_comparable < min_sources:
        status = STATUS_INSUFFICIENT
        notes.append(f"only {n_comparable} comparable clinical source(s) were found")
    elif clin_sup and clin_ref:
        # Distinguish "the database is the only thing supporting this, and the literature says
        # otherwise" from a genuine disagreement between studies -- these call for different
        # actions (revisit the curated entry vs treat the association as unsettled).
        if curated_side == "support" and lit_ref and not lit_sup:
            status = STATUS_CURATED_CONFLICT
            reasons.append({"axis": "curated_vs_literature",
                            "detail": "the curated database records an association that the "
                                      "retrieved literature does not support"})
        elif curated_side == "refute" and lit_sup and not lit_ref:
            status = STATUS_CURATED_CONFLICT
            reasons.append({"axis": "curated_vs_literature",
                            "detail": "the curated database records no association, but the "
                                      "retrieved literature reports one"})
        else:
            ctx = _explain_axis(clin_sup, clin_ref)
            if ctx:
                status, _ = STATUS_CONTEXT, reasons.append(ctx)
            else:
                status = STATUS_CONFLICTING
                for finder in (_design_note(clin_sup, clin_ref), _direction_conflict(clin_sup)):
                    if finder:
                        reasons.append(finder)
                if not reasons:
                    reasons.append({"axis": "unexplained",
                                    "detail": "comparable studies disagree with no contextual "
                                              "difference detected"})
    elif curated_side == "support" and lit_ref and not lit_sup:
        status = STATUS_CURATED_CONFLICT
        reasons.append({"axis": "curated_vs_literature",
                        "detail": "the curated database records an association that the "
                                  "retrieved literature does not support"})
    elif curated_side == "refute" and lit_sup:
        status = STATUS_CURATED_CONFLICT
        reasons.append({"axis": "curated_vs_literature",
                        "detail": "the curated database records no association, but the "
                                  "retrieved literature reports one"})
    elif curated_assoc == "ambiguous":
        status = STATUS_CONFLICTING
        reasons.append({"axis": "curator_ambiguous",
                        "detail": "the curators themselves record conflicting reports"})
    else:
        status = STATUS_CONSISTENT

    return {
        "status": status,
        "reasons": reasons,
        "notes": notes,
        "evidence_tiers": {t: {"support": len(v["support"]), "refute": len(v["refute"])}
                           for t, v in by_tier.items()},
        "populations": sorted(_side_values(clin_sup + clin_ref, "population")),
        "cancer_types": sorted(_side_values(clin_sup + clin_ref, "cancer_type")),
        "endpoints": sorted(_side_values(clin_sup + clin_ref, "endpoint")),
    }


def conclusion_for(entry: dict, resolution: dict) -> str:
    """One-sentence read-out a clinician or reviewer can act on."""
    g, d = entry.get("gene", "?"), entry.get("drug", "the drug")
    st = resolution["status"]
    if st == STATUS_CONSISTENT:
        return (f"Evidence consistently supports a {g}-{d} association; confidence "
                f"{entry['confidence']:.2f}.")
    if st == STATUS_CONFLICTING:
        return (f"The {g}-{d} association remains disputed; evidence is insufficient to base "
                f"clinical screening on {g} alone.")
    if st == STATUS_CONTEXT:
        ax = (resolution["reasons"] or [{}])[0].get("axis", "context")
        return (f"The apparent {g}-{d} disagreement is explained by {ax}; the association may "
                f"hold in one setting and not another.")
    if st == STATUS_CURATED_CONFLICT:
        return (f"The curated database and the retrieved literature disagree about {g}-{d}; "
                f"the curated entry may need revisiting.")
    return (f"Too little comparable clinical evidence was retrieved to judge {g}-{d}.")


def build_cards(ledger: List[dict], claims_by_pair: Dict, pgx=None) -> List[dict]:
    """One resolution card per ledger entry, ordered by how actionable the status is."""
    order = {STATUS_CURATED_CONFLICT: 0, STATUS_CONFLICTING: 1, STATUS_CONTEXT: 2,
             STATUS_CONSISTENT: 3, STATUS_INSUFFICIENT: 4}
    cards = []
    for e in ledger:
        key = (e.get("gene", "").upper(), _norm(e.get("drug", "")))
        sup, ref = claims_by_pair.get(key, ([], []))
        assoc = (e.get("components") or {}).get("clinpgx_association")
        res = resolve_group(sup, ref, assoc)
        cards.append({
            "gene": e.get("gene"), "drug": e.get("drug"),
            "variants": e.get("variants", []),
            "phenotypes": e.get("phenotypes", []),
            "status": res["status"],
            "confidence": e.get("confidence"),
            "label": e.get("label"),
            "reasons": res["reasons"],
            "notes": res["notes"],
            "evidence_tiers": res["evidence_tiers"],
            "populations": res["populations"],
            "cancer_types": res["cancer_types"],
            "endpoints": res["endpoints"],
            "supporting": e.get("supporting", []),
            "refuting": e.get("refuting", []),
            "conclusion": conclusion_for(e, res),
        })
    cards.sort(key=lambda c: (order.get(c["status"], 9), -(c["confidence"] or 0)))
    return cards


def cards_to_prompt(cards: List[dict], max_cards: int = 10) -> str:
    """Render the cards for the answer prompt."""
    out = []
    for c in cards[:max_cards]:
        head = f"{c['gene']} - {c['drug']} :: {c['status']} (confidence {c['confidence']:.2f})"
        out.append(head)
        for r in c["reasons"]:
            out.append(f"    why: {r['detail']}")
        for n in c["notes"]:
            out.append(f"    note: {n}")
        if c["populations"]:
            out.append(f"    populations: {', '.join(c['populations'][:3])}")
        for s in c["supporting"][:2]:
            out.append(f"    supports ({s['ref']}, {s['study_type']})")
        for s in c["refuting"][:2]:
            out.append(f"    REFUTES  ({s['ref']}, {s['study_type']})")
        out.append(f"    => {c['conclusion']}")
    return "\n".join(out)
