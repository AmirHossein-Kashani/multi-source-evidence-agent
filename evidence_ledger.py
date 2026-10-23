"""Per-gene evidence ledger: contradictions between sources + rule-computed confidence.

The research goal is to surface as many candidate genes as possible while attaching a
*correct* confidence to each, and to make disagreement between sources explicit rather than
averaging it away. This module is the scoring half of that and deliberately contains **no LLM
call**: every number here is produced by a formula over structured evidence, so a score can
always be traced back to the claims that produced it. (LLM-emitted confidences are not
calibrated and cannot be defended.)

Inputs are `Claim` records, which come from two places:
  * ClinPGx table rows      -> study_type="curated", stance from the Association column
  * digested paper paragraphs -> stance/study_type classified by the digest chain, each
                                 carrying a citable ref such as PMID:123/PMC456#p12

Contradiction detection uses signal that already exists in the ClinPGx bulk download but was
previously unused: of 127,988 relationship rows, 33,100 say "not associated" and 20,032 say
"ambiguous" -- the latter meaning the curators themselves found conflicting evidence.

Phase 15 changes (docs/PLAN.md, section 4): claims are grouped by gene + drug + OUTCOME, a
claim whose paper studied another drug is excluded from this drug's ledger, expression /
protein-biomarker findings weigh half of an inherited-variant finding, a literature-only
pair backed by two independent strong sources starts from a higher base, and a candidate
association is no longer reported as "disputed".
"""
from dataclasses import dataclass, field
from math import log1p
from typing import Dict, List, Optional, Tuple

# Evidence-level -> base confidence. Imported from pgx_kb so the KG edge weights and the
# ledger cannot drift apart.
try:
    from pgx_kb import LEVEL_CONF
except Exception:  # keep the module importable standalone (tests, notebooks)
    LEVEL_CONF = {"1a": 0.98, "1b": 0.9, "2a": 0.8, "2b": 0.7, "3": 0.55, "4": 0.4}

# How much a source of each kind counts toward (or against) a claim.
STUDY_WEIGHT = {
    "curated": 1.0,            # a ClinPGx curated row
    "meta_analysis": 1.0,
    "systematic_review": 0.95,
    "gwas": 0.9,
    "human_cohort": 0.85,
    "clinical_trial": 0.85,
    "case_report": 0.45,
    "review": 0.4,
    "animal": 0.3,
    "in_vitro": 0.2,
    "unknown": 0.4,
}
# What kind of biological evidence the claim rests on. A pharmacogenomic association is about
# inherited variation; an expression or plasma-protein finding (audit case CPVL/PIGR) is
# related evidence, not the same claim, so it counts half.
KIND_FACTOR = {
    "germline_variant": 1.0, "unknown": 1.0,
    "somatic": 0.5, "expression": 0.5, "protein_biomarker": 0.5,
}

# Base confidence when the pair is not in the curated tables at all, and when the curators
# explicitly say the pair is NOT associated.
BASE_ABSENT = 0.25
BASE_NOT_ASSOCIATED = 0.15
BASE_ASSOCIATED_NO_LEVEL = 0.55
# A pair with no curated row but at least LIT_ESTABLISHED_MIN_SOURCES independent sources of
# weight >= LIT_ESTABLISHED_MIN_WEIGHT (cohort or better) starts between curated level 4
# (0.40) and level 3 (0.55). The most such a pair can reach is ~0.64 (moderate): "high" stays
# curated-only. Decided in docs/PLAN.md, section 2.
BASE_LITERATURE_ESTABLISHED = 0.45
LIT_ESTABLISHED_MIN_WEIGHT = 0.85
LIT_ESTABLISHED_MIN_SOURCES = 2

SUPPORT_K = 0.18      # how fast independent support raises confidence
REFUTE_M = 0.30       # how hard refuting evidence pulls it down
AMBIGUOUS_DAMPING = 0.9   # curators call the pair ambiguous -> it cannot score like a clean one

# A pair with no curated row is only "unsupported" when nothing better than a review, an
# animal study or an unclassified source backs it. Above this weight it is instead an
# uncurated literature claim -- a candidate novel finding, which is worth surfacing.
NOVEL_SUPPORT_MIN = 0.8

LABEL_HIGH, LABEL_MODERATE, LABEL_LOW = 0.75, 0.50, 0.25

# Flags that describe a pair's standing rather than a disagreement between sources.
NON_DISPUTE_FLAGS = ("unsupported_claim", "uncurated_literature_claim")


@dataclass
class Claim:
    """One assertion about a gene-drug(-outcome) relationship, from one source."""
    gene: str
    drug: str = ""
    phenotype: str = ""
    variant: str = ""
    direction: str = ""            # increases | decreases | no_effect | ""
    stance: str = "supports"       # supports | refutes | inconclusive
    study_type: str = "unknown"
    ref: str = ""                  # PMID:x/PMCy#pN, or ClinPGx:GENE/variant:Llevel
    pmid: str = ""                 # source identity for de-duplication
    level: str = ""                # ClinPGx evidence level, curated claims only
    source: str = ""               # "ClinPGx" | "PubMed"
    text: str = ""                 # the sentence(s) the claim came from
    # phase 15
    outcome: str = ""              # normalised outcome family (mesh_terms.outcome_family)
    evidence_kind: str = "unknown" # germline_variant | somatic | expression | protein_biomarker
    drug_match: str = "exact"      # exact | class | mismatch (paper studied another drug)
    proposed_via: str = ""         # how the search that found this source was proposed
    symbol_status: str = ""        # verified | unverified | unknown (gene_symbols), "" = not checked
    # study context, compared by the contradiction layer
    population: str = ""
    cancer_type: str = ""
    endpoint: str = ""
    dose_context: str = ""

    def source_id(self) -> str:
        """Identity for counting INDEPENDENT sources (several paragraphs of one paper
        must not count as several studies)."""
        return self.pmid or self.ref.split("#")[0] or self.ref


def _norm(s: str) -> str:
    return " ".join(str(s or "").strip().lower().split())


def _weight(claim: Claim) -> float:
    w = STUDY_WEIGHT.get(_norm(claim.study_type).replace(" ", "_"), STUDY_WEIGHT["unknown"])
    return w * KIND_FACTOR.get(_norm(getattr(claim, "evidence_kind", "")) or "unknown", 1.0)


def compute_confidence(level: str, assoc: Optional[str],
                       supporting: List[Claim], refuting: List[Claim]) -> Tuple[float, dict]:
    """Confidence for one gene-drug(-outcome) group, plus the components that produced it.

    base       curated evidence level (1A .98 ... 4 .40); 0.25 if the pair is absent from
               ClinPGx (0.45 once two independent strong sources support it), 0.15 if the
               curators record it as NOT associated
    support    sum of study weights over DISTINCT supporting sources (log-damped)
    refute     same for refuting sources, subtracted
    """
    lvl = _norm(level)
    literature_established = False
    if lvl and lvl in LEVEL_CONF:
        base = LEVEL_CONF[lvl]
    elif assoc == "not associated":
        base = BASE_NOT_ASSOCIATED
    elif assoc == "associated":
        base = BASE_ASSOCIATED_NO_LEVEL
    elif assoc == "ambiguous":
        base = BASE_ASSOCIATED_NO_LEVEL * 0.8
    else:
        base = BASE_ABSENT
        strong = {c.source_id() for c in supporting if _weight(c) >= LIT_ESTABLISHED_MIN_WEIGHT}
        if len(strong) >= LIT_ESTABLISHED_MIN_SOURCES:
            base = BASE_LITERATURE_ESTABLISHED
            literature_established = True

    def summed(claims):
        best: Dict[str, float] = {}
        for c in claims:                      # one contribution per distinct source
            sid = c.source_id()
            best[sid] = max(best.get(sid, 0.0), _weight(c))
        return sum(best.values()), len(best)

    sup_w, sup_n = summed(supporting)
    ref_w, ref_n = summed(refuting)

    score = base * (1.0 + SUPPORT_K * log1p(sup_w)) - REFUTE_M * log1p(ref_w)
    # A pair the curators themselves call ambiguous should never score like an undisputed one
    # of the same evidence level, even when the level is high.
    if assoc == "ambiguous":
        score *= AMBIGUOUS_DAMPING
    score = max(0.0, min(1.0, score))
    return score, {
        "base": round(base, 3),
        "support_weight": round(sup_w, 3), "support_sources": sup_n,
        "refute_weight": round(ref_w, 3), "refute_sources": ref_n,
        "clinpgx_level": lvl.upper() or None, "clinpgx_association": assoc,
        "literature_established": literature_established,
    }


def label_for(score: float) -> str:
    if score >= LABEL_HIGH:
        return "high"
    if score >= LABEL_MODERATE:
        return "moderate"
    if score >= LABEL_LOW:
        return "low"
    return "very_low"


def detect_contradictions(assoc: Optional[str], supporting: List[Claim],
                          refuting: List[Claim], has_curated: bool) -> List[dict]:
    """Explicit disagreement, typed so it can be reported and scored.

    `curator_ambiguous` is the cheapest and most reliable signal: ClinPGx marks a pair
    ambiguous precisely when its own curators found conflicting reports.
    """
    flags = []
    if assoc == "ambiguous":
        flags.append({"type": "curator_ambiguous",
                      "detail": "ClinPGx curators record conflicting evidence for this pair"})
    lit_support = [c for c in supporting if c.source != "ClinPGx"]
    lit_refute = [c for c in refuting if c.source != "ClinPGx"]
    if assoc == "not associated" and lit_support:
        flags.append({"type": "curated_vs_literature",
                      "detail": "ClinPGx records NO association, but retrieved papers support one",
                      "refs": [c.ref for c in lit_support[:4]]})
    if assoc == "associated" and lit_refute:
        flags.append({"type": "curated_vs_literature",
                      "detail": "ClinPGx records an association, but retrieved papers refute it",
                      "refs": [c.ref for c in lit_refute[:4]]})
    if lit_support and lit_refute:
        flags.append({"type": "literature_internal",
                      "detail": "retrieved papers disagree with each other",
                      "refs": [c.ref for c in (lit_support[:2] + lit_refute[:2])]})
    if not has_curated and assoc is None:
        # Distinguish "the literature knows something ClinPGx has not curated yet" (a candidate
        # novel finding, worth reporting) from "asserted on nothing solid" (a risk).
        best = max([_weight(c) for c in lit_support], default=0.0)
        if best >= NOVEL_SUPPORT_MIN:
            flags.append({"type": "uncurated_literature_claim",
                          "detail": "not curated in ClinPGx, but supported by human studies "
                                    "-- candidate novel association",
                          "refs": [c.ref for c in lit_support[:4]]})
        else:
            flags.append({"type": "unsupported_claim",
                          "detail": "no curated row and no strong supporting study for this pair",
                          "refs": [c.ref for c in lit_support[:4]]})
    return flags


def _association(pgx, gene: str, drug: str) -> Tuple[Optional[str], str]:
    """Curated association for the pair and how it matched ('exact' drug name or a 'class')."""
    if pgx is None or not drug:
        return None, ""
    try:
        if hasattr(pgx, "association_detailed"):
            rec = pgx.association_detailed(gene, drug)
            return (rec["assoc"], rec["match"]) if rec else (None, "")
        return pgx.is_associated(gene, drug), "exact"
    except Exception:
        return None, ""


def build_ledger(claims: List[Claim], pgx=None) -> List[dict]:
    """Aggregate claims into one entry per gene-drug-outcome group, strongest confidence first.

    `pgx` is an optional PharmGKBSearcher; when given, it supplies the curated stance even for
    pairs no retrieved claim mentioned. Claims whose paper studied another drug
    (drug_match == "mismatch") never enter a group: they are the caller's to log."""
    groups: Dict[Tuple[str, str, str], List[Claim]] = {}
    for c in claims:
        if not c.gene or getattr(c, "drug_match", "exact") == "mismatch":
            continue
        key = (c.gene.strip().upper(), _norm(c.drug), _norm(getattr(c, "outcome", "")))
        groups.setdefault(key, []).append(c)

    out = []
    for (gene, drug, outcome), group in groups.items():
        supporting = [c for c in group if _norm(c.stance) == "supports"]
        refuting = [c for c in group if _norm(c.stance) == "refutes"]
        inconclusive = [c for c in group if _norm(c.stance) == "inconclusive"]
        curated = [c for c in group if c.source == "ClinPGx"]
        level = ""
        for c in curated:                      # strongest curated level wins
            if c.level and (not level or LEVEL_CONF.get(_norm(c.level), 0)
                            > LEVEL_CONF.get(_norm(level), 0)):
                level = c.level

        assoc, match = _association(pgx, gene, drug)
        score, parts = compute_confidence(level, assoc, supporting, refuting)
        parts["clinpgx_match"] = match or None
        flags = detect_contradictions(assoc, supporting, refuting, bool(curated))
        variants = sorted({c.variant for c in group if c.variant})
        phenos = sorted({c.phenotype for c in group if c.phenotype})
        kinds = sorted({_norm(getattr(c, "evidence_kind", "")) for c in group
                        if _norm(getattr(c, "evidence_kind", "")) not in ("", "unknown")})
        via = sorted({c.proposed_via for c in group if getattr(c, "proposed_via", "")})
        # A symbol is unverified when NCBI Gene has no human record for it (family names,
        # aliases). Curated rows vouch for their own symbols.
        statuses = {getattr(c, "symbol_status", "") for c in group}
        symbol_status = ("verified" if curated or "verified" in statuses else
                         "unverified" if "unverified" in statuses else
                         "unknown" if "unknown" in statuses else "")
        is_candidate = (any(f["type"] == "uncurated_literature_claim" for f in flags)
                        and symbol_status != "unverified")

        def _src(c: Claim) -> dict:
            d = {"ref": c.ref, "study_type": c.study_type, "text": c.text[:200]}
            if getattr(c, "evidence_kind", "unknown") not in ("", "unknown"):
                d["evidence_kind"] = c.evidence_kind
            if getattr(c, "drug_match", "exact") != "exact":
                d["drug_match"] = c.drug_match
            return d

        out.append({
            "gene": gene, "drug": drug, "outcome": outcome,
            "variants": variants[:4], "phenotypes": phenos[:3],
            "confidence": round(score, 3),
            "label": label_for(score),
            "curated": bool(curated) or assoc is not None,
            "candidate": is_candidate,
            "symbol_status": symbol_status,
            "disputed": any(f["type"] not in NON_DISPUTE_FLAGS for f in flags),
            "contradictions": flags,
            "evidence_kinds": kinds,
            "proposed_via": via,
            "supporting": [_src(c) for c in supporting[:5]],
            "refuting": [_src(c) for c in refuting[:5]],
            "inconclusive_count": len(inconclusive),
            "components": parts,
        })
    out.sort(key=lambda e: (-e["confidence"], e["gene"]))
    return out


def ledger_to_prompt(ledger: List[dict], max_entries: int = 12, max_candidates: int = 8) -> str:
    """Render the ledger for the answer prompt: every gene, with its confidence and conflict.

    Candidate associations (literature-only, strong support) get their own block that sits
    OUTSIDE the max_entries cut, so a low-scoring candidate still reaches the answer."""
    def _entry_lines(e: dict) -> List[str]:
        bits = [f"{e['gene']}"]
        if e.get("variants"):
            bits.append("(" + ", ".join(e["variants"][:2]) + ")")
        if e.get("outcome"):
            bits.append(f"[{e['outcome']}]")
        bits.append(f"- confidence {e['confidence']:.2f} [{e['label']}]")
        if e.get("disputed"):
            bits.append("** DISPUTED: " + "; ".join(
                f["type"] for f in e["contradictions"] if f["type"] not in NON_DISPUTE_FLAGS) + " **")
        if e.get("evidence_kinds"):
            bits.append("(evidence kind: " + ", ".join(e["evidence_kinds"]) + ")")
        if e.get("symbol_status") == "unverified":
            bits.append("(not an official gene symbol)")
        lines = [" ".join(bits)]
        for s in e["supporting"][:2]:
            lines.append(f"    supports  ({s['ref']}, {s['study_type']})")
        for s in e["refuting"][:2]:
            lines.append(f"    REFUTES   ({s['ref']}, {s['study_type']})")
        for f in e["contradictions"]:
            if f["type"] not in NON_DISPUTE_FLAGS:
                lines.append(f"    conflict: {f['detail']}")
        return lines

    lines: List[str] = []
    main = [e for e in ledger if not e.get("candidate")]
    for e in main[:max_entries]:
        lines += _entry_lines(e)
    cands = [e for e in ledger if e.get("candidate")]
    if cands:
        lines.append("")
        lines.append("CANDIDATE ASSOCIATIONS NOT IN ClinPGx (literature only; report them as "
                     "candidates needing verification, never as established):")
        for e in cands[:max_candidates]:
            lines += _entry_lines(e)
            if e.get("proposed_via"):
                lines.append(f"    proposed by: {', '.join(e['proposed_via'])}")
    weak = sum(1 for e in ledger if not e.get("curated") and not e.get("candidate"))
    if weak:
        lines.append(f"({weak} further literature-only pair(s) have only weak support and are "
                     f"omitted)")
    return "\n".join(lines)
