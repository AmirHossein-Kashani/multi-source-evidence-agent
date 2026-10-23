"""MeSH vocabulary for synonym and drug-class expansion, cached locally.

Why MeSH: PubMed is indexed with it, so its entry terms are the synonyms the literature
actually uses, and its tree gives drug classes ("Cisplatin" sits under "Platinum Compounds")
from a maintained source instead of a hand-written list. Each term is looked up once through
NCBI E-utilities (db=mesh) and cached in dataset/mesh_cache.json, so repeated runs make no
further calls. Without network the cache is read-only and unknown terms fall back to the
caller's static tables (pgx_kb.PHENO_SYNONYMS / DRUG_CLASS_MEMBERS).

Decided in docs/PLAN.md, section 2.
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Set

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, "dataset", "mesh_cache.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _norm(s) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


class MeshVocab:
    """lookup(term) -> {uid, heading, entry_terms, parents, tree} | None (not a MeSH concept)."""

    # NCBI allows ~3 req/s per IP without an API key, and the PubMed client in the pipeline
    # shares that allowance, so this client stays well under it on its own.
    _MIN_INTERVAL = 0.6

    def __init__(self, cache_path: str = DEFAULT_CACHE, online: Optional[bool] = None,
                 api_key: str = ""):
        self.cache_path = cache_path
        self.online = (os.environ.get("AMG_MESH_ONLINE", "1") != "0") if online is None else online
        self.api_key = api_key or os.environ.get("pubmed_api", "") or os.environ.get("PUBMED_API_KEY", "")
        if self.api_key:
            self._MIN_INTERVAL = 0.2
        self._last_call = 0.0
        self._failed: set = set()        # terms whose lookup failed in this process: no retry storm
        self.cache: Dict[str, Optional[dict]] = {}
        try:
            with open(cache_path, encoding="utf-8") as f:
                self.cache = json.load(f)
        except (OSError, ValueError):
            self.cache = {}

    # ---- network -------------------------------------------------------------
    def _get_json(self, endpoint: str, params: dict) -> dict:
        wait = self._MIN_INTERVAL - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        params = {**params, "retmode": "json"}
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{EUTILS}/{endpoint}.fcgi?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "amg-rag-mesh/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(2.0)                      # rate-limited: back off once, then retry
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        finally:
            self._last_call = time.monotonic()
        return data

    def _summaries(self, uids: List[str]) -> Dict[str, dict]:
        if not uids:
            return {}
        res = self._get_json("esummary", {"db": "mesh", "id": ",".join(uids)}).get("result", {})
        return {u: res[u] for u in uids if isinstance(res.get(u), dict)}

    def save(self) -> None:
        tmp = self.cache_path + ".tmp"
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=1, sort_keys=True)
            os.replace(tmp, self.cache_path)
        except OSError as e:
            print(f"[mesh] could not write cache: {e}")

    # ---- lookup --------------------------------------------------------------
    def lookup(self, term: str) -> Optional[dict]:
        key = _norm(term)
        if not key:
            return None
        if key in self.cache:
            return self.cache[key]
        if not self.online or key in self._failed:
            return None                       # offline or failed earlier: do not cache, do not retry
        try:
            ids = self._get_json("esearch", {"db": "mesh", "term": f'"{key}"[MeSH Terms]',
                                             "retmax": 5})["esearchresult"].get("idlist", [])
            rec = None
            if ids:
                sums = self._summaries(ids)
                # Several headings can match an entry term; prefer the one named exactly so.
                uid = next((u for u in ids if u in sums and
                            key in {_norm(t) for t in sums[u].get("ds_meshterms", [])}), ids[0])
                s = sums.get(uid, {})
                terms = list(s.get("ds_meshterms") or [])
                parent_uids = sorted({str(l.get("parent")) for l in (s.get("ds_idxlinks") or [])
                                      if l.get("parent")})
                parents = []
                if parent_uids:
                    ps = self._summaries(parent_uids)
                    parents = [ps[u]["ds_meshterms"][0] for u in parent_uids
                               if u in ps and ps[u].get("ds_meshterms")]
                rec = {"uid": uid, "heading": terms[0] if terms else key,
                       "entry_terms": terms, "parents": parents,
                       "tree": [l.get("treenum") for l in (s.get("ds_idxlinks") or [])]}
        except Exception as e:                # network error: report once, do not cache
            print(f"[mesh] lookup failed for {key!r}: {e}")
            self._failed.add(key)
            return None
        self.cache[key] = rec                 # None = looked up, not a MeSH concept
        self.save()
        return rec

    def heading(self, term: str) -> str:
        rec = self.lookup(term)
        return _norm(rec["heading"]) if rec else _norm(term)

    def synonyms(self, term: str) -> Set[str]:
        out = {_norm(term)}
        rec = self.lookup(term)
        if rec:
            out |= {_norm(t) for t in rec.get("entry_terms", [])}
            out.add(_norm(rec["heading"]))
        return {t for t in out if t}

    def parents(self, term: str) -> List[str]:
        """Immediate tree parents (for a drug: its chemical class, e.g. 'platinum compounds')."""
        rec = self.lookup(term)
        return [_norm(p) for p in rec.get("parents", [])] if rec else []

    def same_concept(self, a: str, b: str) -> bool:
        a, b = _norm(a), _norm(b)
        if not a or not b:
            return False
        if a == b or (len(a) >= 5 and len(b) >= 5 and (a in b or b in a)):
            return True
        ra, rb = self.lookup(a), self.lookup(b)
        return bool(ra and rb and ra["uid"] == rb["uid"])


def outcome_family(term: str, question_outcome: str, vocab: Optional[MeshVocab] = None,
                   static_synonyms: Optional[Dict[str, str]] = None) -> str:
    """Normalise a claim's outcome for ledger grouping.

    Returns the question's outcome when the claim's outcome is the same concept or a
    synonym / sub-phrase of it ('clinically significant hearing loss' -> 'ototoxicity' family),
    the claim's own MeSH heading when it is a different concept ('acute kidney injury'), and
    '' when the claim states no outcome. Grouping by this key is what stops a kidney-injury
    finding from counting as ototoxicity evidence (audit case MLH1/MSH3) without splitting
    same-family evidence into fragments."""
    t, q = _norm(term), _norm(question_outcome)
    if not t:
        return ""
    if not q:
        return vocab.heading(t) if vocab else t
    family = {q}
    for k, v in (static_synonyms or {}).items():
        if _norm(v) == q or _norm(k) == q:
            family |= {_norm(k), _norm(v)}
    if vocab:
        family |= vocab.synonyms(q)
    t_syn = vocab.synonyms(t) if vocab else {t}
    if t_syn & family:
        return q
    for f in family:
        if len(f) >= 5 and (f in t or t in f):
            return q
    return vocab.heading(t) if vocab else t
