"""Edge queue: every candidate gene-drug(-outcome) relation with a status, a provenance and
a prior, plus the allocator that decides which edges the next search round tests.

Replaces the even split of AMG_COMBO_MAX_QUERIES: the query budget goes where
uncertainty x prior is highest, so a pair the ledger already settled is not searched again
while an INSUFFICIENT card or an untested path proposal is. No LLM call here; statuses come
from the rule-based ledger and the contradiction cards (docs/PLAN.md, section 3).
"""
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

PRIOR_BY_PROVENANCE = {
    "curated": 0.90,        # a ClinPGx row for the question's drug
    "hypothesised": 0.30,   # LLM pairwise relation extraction, uncalibrated
    "path:A:outcome": 0.50,
    "path:B:gene": 0.35,
    "path:C:class": 0.55,
    "literature": 0.45,     # a claim read from a paper in an earlier round
    "followup": 0.60,       # a disagreement card asked for this search
}
STATUSES = ("untested", "confirmed", "refuted", "disputed", "insufficient")
SETTLED = ("confirmed", "refuted")


def _norm(s) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


@dataclass
class Edge:
    gene: str
    drug: str
    outcome: str = ""
    provenance: List[str] = field(default_factory=list)
    prior: float = 0.3
    status: str = "untested"
    score: Optional[float] = None
    n_sources: int = 0
    refs: List[str] = field(default_factory=list)
    queries_issued: int = 0
    rounds: List[int] = field(default_factory=list)
    path: str = ""
    query_terms: List[str] = field(default_factory=list)   # explicit terms override gene/drug/outcome
    last_terms: List[str] = field(default_factory=list)    # terms chosen by the latest select()

    def key(self) -> Tuple[str, str, str]:
        return (self.gene.strip().upper(), _norm(self.drug), _norm(self.outcome))


def prior_for(provenance: str) -> float:
    base = provenance.split(":")[0] if provenance.startswith("followup") else provenance
    return PRIOR_BY_PROVENANCE.get(provenance, PRIOR_BY_PROVENANCE.get(base, 0.3))


class EdgeQueue:
    def __init__(self):
        self.edges: Dict[Tuple[str, str, str], Edge] = {}
        self.issued: set = set()          # query term tuples already sent, never repeated

    # ---- population ------------------------------------------------------------
    def add(self, gene: str, drug: str, outcome: str = "", provenance: str = "hypothesised",
            prior: Optional[float] = None, path: str = "",
            query_terms: Optional[List[str]] = None) -> Edge:
        e = Edge(gene=gene.strip().upper(), drug=_norm(drug), outcome=_norm(outcome))
        prior = prior_for(provenance) if prior is None else prior
        cur = self.edges.get(e.key())
        if cur is None:
            e.provenance, e.prior, e.path = [provenance], prior, path
            e.query_terms = list(query_terms or [])
            self.edges[e.key()] = e
            return e
        if provenance not in cur.provenance:
            cur.provenance.append(provenance)
        cur.prior = max(cur.prior, prior)             # the strongest reason to test it wins
        cur.path = cur.path or path
        if query_terms:
            cur.query_terms = list(query_terms)
        return cur

    def update_from_ledger(self, ledger: List[dict], cards: Optional[List[dict]] = None) -> None:
        """Pull score / source counts / status from the ledger (and the cards, when present)."""
        card_status = {(c.get("gene", "").upper(), _norm(c.get("drug")), _norm(c.get("outcome"))):
                       c.get("status") for c in (cards or [])}
        for entry in ledger:
            key = (entry.get("gene", "").upper(), _norm(entry.get("drug")), _norm(entry.get("outcome")))
            comp = entry.get("components") or {}
            curated = bool(comp.get("clinpgx_level") or comp.get("clinpgx_association"))
            e = self.edges.get(key) or self.add(*key, provenance="curated" if curated else "literature")
            e.score = entry.get("confidence")
            sup_n, ref_n = comp.get("support_sources", 0), comp.get("refute_sources", 0)
            e.n_sources = sup_n + ref_n
            e.refs = [s["ref"] for s in (entry.get("supporting") or [])[:3]] + \
                     [s["ref"] for s in (entry.get("refuting") or [])[:3]]
            st = card_status.get(key)
            if st == "CONSISTENT":
                e.status = "confirmed"
            elif st in ("CONFLICTING", "CONTEXT-DEPENDENT", "CURATED-LITERATURE CONFLICT"):
                e.status = "disputed"
            elif st == "INSUFFICIENT":
                e.status = "insufficient"
            elif comp.get("refute_weight", 0) > comp.get("support_weight", 0):
                e.status = "refuted"
            elif (e.score or 0) >= 0.5 and sup_n >= 2:
                e.status = "confirmed"
            elif e.n_sources == 0:
                e.status = "untested"
            else:
                e.status = "insufficient"

    # ---- allocation ------------------------------------------------------------
    @staticmethod
    def uncertainty(e: Edge) -> float:
        """1 for an untested edge; highest near a 0.5 score; falls with the number of sources."""
        u = 1.0 if e.score is None else max(0.2, 1.0 - 2.0 * abs(e.score - 0.5))
        u /= math.sqrt(1 + e.n_sources)
        if e.status == "insufficient":
            u = max(u, 0.8)
        if e.status in SETTLED:
            u *= 0.1
        return u

    def priority(self, e: Edge) -> float:
        return self.uncertainty(e) * e.prior

    def select(self, budget: int, round_no: int = 1, max_queries_per_edge: int = 2,
               reserve_untested: float = 0.34) -> List[Edge]:
        """Top-`budget` edges by priority. A share of the budget (`reserve_untested`) goes to
        edges nothing has tested yet, otherwise curated-but-insufficient pairs (priority ~0.7)
        would always outrank fresh path proposals (<= 0.55) and discovery would starve."""
        pool = [e for e in self.edges.values()
                if e.queries_issued < max_queries_per_edge and e.status not in SETTLED
                and tuple(self.query_terms(e)) not in self.issued]   # a repeat finds nothing new
        pool.sort(key=lambda e: (-self.priority(e), e.gene))
        budget = max(0, budget)
        n_reserved = int(math.ceil(budget * reserve_untested)) if budget else 0
        chosen = [e for e in pool if e.status == "untested"][:n_reserved]
        for e in pool:
            if len(chosen) >= budget:
                break
            if e not in chosen:
                chosen.append(e)
        for e in chosen:
            e.last_terms = self.query_terms(e)      # fixed before the attempt counter moves
            self.issued.add(tuple(e.last_terms))
            e.queries_issued += 1
            e.rounds.append(round_no)
        return chosen

    @staticmethod
    def query_terms(e: Edge) -> List[str]:
        """Terms for the edge's NEXT query. A card's follow-up terms win; otherwise the first
        attempt asks for the pair and the outcome, the second drops the outcome and asks for
        genetic-association language instead, so the two attempts do not return the same
        papers."""
        if e.query_terms:
            return list(e.query_terms)
        if e.queries_issued == 0:
            return [t for t in (e.gene, e.drug, e.outcome) if t]
        return [e.gene, e.drug, "(polymorphism OR genotype OR variant OR allele)"]

    # ---- reporting -------------------------------------------------------------
    def counts(self) -> Dict[str, int]:
        out = {s: 0 for s in STATUSES}
        for e in self.edges.values():
            out[e.status] = out.get(e.status, 0) + 1
        return out

    def summary(self) -> List[dict]:
        rows = []
        for e in sorted(self.edges.values(), key=lambda e: (-self.priority(e), e.gene)):
            d = asdict(e)
            d["priority"] = round(self.priority(e), 3)
            rows.append(d)
        return rows
