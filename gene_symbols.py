"""Official human gene symbols through NCBI Gene (E-utilities db=gene), cached locally.

Why: the digest names genes the way the paper wrote them. The first phase-15 run produced
candidate associations for "CBR" and "AKR" (enzyme families) and "MATE1" (an alias of
SLC47A1). A candidate association needs a real symbol, so each literature gene is checked
once against NCBI Gene: 'verified' when a human record carries that symbol, 'unverified'
otherwise. Unverified genes stay in the ledger (nothing is dropped) but are kept out of the
candidates block. 'unknown' = offline and not cached.

Cached in dataset/gene_cache.json; same rate-limit discipline as mesh_terms.
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, "dataset", "gene_cache.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
_SHAPE = re.compile(r"^[A-Z][A-Z0-9orf\-]{1,14}$")      # HGNC-like, e.g. ABCC3, C9orf72, HLA-B


class GeneSymbols:
    _MIN_INTERVAL = 0.6

    def __init__(self, cache_path: str = DEFAULT_CACHE, online: Optional[bool] = None,
                 api_key: str = ""):
        self.cache_path = cache_path
        self.online = (os.environ.get("AMG_MESH_ONLINE", "1") != "0") if online is None else online
        self.api_key = api_key or os.environ.get("pubmed_api", "") or os.environ.get("PUBMED_API_KEY", "")
        if self.api_key:
            self._MIN_INTERVAL = 0.2
        self._last_call = 0.0
        self._failed: set = set()
        self.cache: Dict[str, bool] = {}       # SYMBOL -> True (official) / False
        try:
            with open(cache_path, encoding="utf-8") as f:
                self.cache = json.load(f)
        except (OSError, ValueError):
            self.cache = {}

    def _get_json(self, endpoint: str, params: dict) -> dict:
        wait = self._MIN_INTERVAL - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        params = {**params, "retmode": "json"}
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{EUTILS}/{endpoint}.fcgi?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "amg-rag-genes/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(2.0)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        finally:
            self._last_call = time.monotonic()
        return data

    def save(self) -> None:
        tmp = self.cache_path + ".tmp"
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=0, sort_keys=True)
            os.replace(tmp, self.cache_path)
        except OSError as e:
            print(f"[genes] could not write cache: {e}")

    def status(self, symbol: str) -> str:
        """'verified' | 'unverified' | 'unknown' (offline, not cached)."""
        sym = (symbol or "").strip().upper()
        if not sym:
            return "unverified"
        if sym in self.cache:
            return "verified" if self.cache[sym] else "unverified"
        if not _SHAPE.match(sym):
            self.cache[sym] = False            # cannot be an HGNC symbol
            self.save()
            return "unverified"
        if not self.online or sym in self._failed:
            return "unknown"
        try:
            ids = self._get_json("esearch", {"db": "gene", "retmax": 5,
                                             "term": f'{sym}[sym] AND "Homo sapiens"[Organism]'}
                                 )["esearchresult"].get("idlist", [])
            ok = False
            if ids:
                res = self._get_json("esummary", {"db": "gene", "id": ",".join(ids)}).get("result", {})
                ok = any(isinstance(res.get(u), dict) and
                         (res[u].get("name") or "").upper() == sym for u in ids)
        except Exception as e:
            print(f"[genes] lookup failed for {sym!r}: {e}")
            self._failed.add(sym)
            return "unknown"
        self.cache[sym] = ok
        self.save()
        return "verified" if ok else "unverified"
