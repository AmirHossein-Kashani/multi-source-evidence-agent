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

# Base confidence when the pair is not in the curated tables at all, and when the curators
# explicitly say the pair is NOT associated.
BASE_ABSENT = 0.25
BASE_NOT_ASSOCIATED = 0.15
BASE_ASSOCIATED_NO_LEVEL = 0.55

SUPPORT_K = 0.18      # how fast independent support raises confidence
REFUTE_M = 0.30       # how hard refuting evidence pulls it down
AMBIGUOUS_DAMPING = 0.9   # curators call the pair ambiguous -> it cannot score like a clean one

# A pair with no curated row is only "unsupported" when nothing better than a review, an
# animal study or an unclassified source backs it. Above this weight it is instead an
# uncurated literature claim -- a candidate novel finding, which is worth surfacing.
NOVEL_SUPPORT_MIN = 0.8

LABEL_HIGH, LABEL_MODERATE, LABEL_LOW = 0.75, 0.50, 0.25


@dataclass
class Claim:
    """One assertion about a gene-drug(-phenotype) relationship, from one source."""
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

    def source_id(self) -> str:
        """Identity for counting INDEPENDENT sources (several paragraphs of one paper
        must not count as several studies)."""
        return self.pmid or self.ref.split("#")[0] or self.ref


def _norm(s: str) -> str:
    return " ".join(str(s or "").strip().lower().split())


def _weight(claim: Claim) -> float:
    return STUDY_WEIGHT.get(_norm(claim.study_type).replace(" ", "_"), STUDY_WEIGHT["unknown"])


def compute_confidence(level: str, assoc: Optional[str],
                       supporting: List[Claim], refuting: List[Claim]) -> Tuple[float, dict]:
    """Confidence for one gene-drug pair, plus the components that produced it.

    base       curated evidence level (1A .98 ... 4 .40); 0.25 if the pair is absent from
               ClinPGx, 0.15 if the curators record it as NOT associated
    support    sum of study weights over DISTINCT supporting sources (log-damped)
    refute     same for refuting sources, subtracted
    """
    lvl = _norm(level)
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


def build_ledger(claims: List[Claim], pgx=None) -> List[dict]:
    """Aggregate claims into one entry per gene-drug pair, strongest confidence first.

    `pgx` is an optional PharmGKBSearcher; when given, its `is_associated` supplies the
    curated stance even for pairs no retrieved claim mentioned.
    """
    groups: Dict[Tuple[str, str], List[Claim]] = {}
    for c in claims:
        if not c.gene:
            continue
        groups.setdefault((c.gene.strip().upper(), _norm(c.drug)), []).append(c)

    out = []
    for (gene, drug), group in groups.items():
        supporting = [c for c in group if _norm(c.stance) == "supports"]
        refuting = [c for c in group if _norm(c.stance) == "refutes"]
        inconclusive = [c for c in group if _norm(c.stance) == "inconclusive"]
        curated = [c for c in group if c.source == "ClinPGx"]
        level = ""
        for c in curated:                      # strongest curated level wins
            if c.level and (not level or LEVEL_CONF.get(_norm(c.level), 0)
                            > LEVEL_CONF.get(_norm(level), 0)):
                level = c.level

        assoc = None
        if pgx is not None and drug:
            try:
                assoc = pgx.is_associated(gene, drug)
            except Exception:
                assoc = None

        score, parts = compute_confidence(level, assoc, supporting, refuting)
        flags = detect_contradictions(assoc, supporting, refuting, bool(curated))
        variants = sorted({c.variant for c in group if c.variant})
        phenos = sorted({c.phenotype for c in group if c.phenotype})

        out.append({
            "gene": gene, "drug": drug,
            "variants": variants[:4], "phenotypes": phenos[:3],
            "confidence": round(score, 3),
            "label": label_for(score),
            "disputed": bool(flags and any(f["type"] != "unsupported_claim" for f in flags)),
            "contradictions": flags,
            "supporting": [{"ref": c.ref, "study_type": c.study_type, "text": c.text[:200]}
                           for c in supporting[:5]],
            "refuting": [{"ref": c.ref, "study_type": c.study_type, "text": c.text[:200]}
                         for c in refuting[:5]],
            "inconclusive_count": len(inconclusive),
            "components": parts,
        })
    out.sort(key=lambda e: (-e["confidence"], e["gene"]))
    return out


def ledger_to_prompt(ledger: List[dict], max_entries: int = 12) -> str:
    """Render the ledger for the answer prompt: every gene, with its confidence and conflict."""
    lines = []
    for e in ledger[:max_entries]:
        bits = [f"{e['gene']}"]
        if e["variants"]:
            bits.append("(" + ", ".join(e["variants"][:2]) + ")")
        bits.append(f"- confidence {e['confidence']:.2f} [{e['label']}]")
        if e["disputed"]:
            bits.append("** DISPUTED: " + "; ".join(f["type"] for f in e["contradictions"]) + " **")
        lines.append(" ".join(bits))
        for s in e["supporting"][:2]:
            lines.append(f"    supports  ({s['ref']}, {s['study_type']})")
        for s in e["refuting"][:2]:
            lines.append(f"    REFUTES   ({s['ref']}, {s['study_type']})")
        for f in e["contradictions"]:
            lines.append(f"    conflict: {f['detail']}")
    return "\n".join(lines)
