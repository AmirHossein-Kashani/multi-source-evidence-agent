"""
AMG-RAG: Autonomous Medical Knowledge Graph RAG System
Complete implementation with dynamic KG generation and medical QA
"""

import json
import os
import re
import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
import networkx as nx
from langchain_openai import ChatOpenAI
try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
# HuggingFaceEmbeddings + Chroma are only used for the (never-queried) vector store, which
# is skipped in offline mode. Guard the imports so offline runs don't require chromadb.
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    Chroma = None
import requests
from xml.etree import ElementTree as ET
try:
    import wikipedia
except ImportError:
    wikipedia = None
from typing_extensions import TypedDict
from langgraph.graph import END, StateGraph, START
from decouple import config
# Configuration - Replace with your API keys
# Defaults let the system run against a local/remote Ollama endpoint without an OpenAI key.
OPENAI_API_KEY = config('OPENAI_API_KEY', default='ollama')  # any non-empty string works for Ollama
PUBMED_API_KEY = config('pubmed_api', default='')  # Optional, empty => unauthenticated (lower rate limit)

# Local ClinPGx/PharmGKB table lookup (used when AMG_KB_SOURCE=pharmgkb). Import robustly:
# this file is loaded by path via importlib, so ensure its dir is importable.
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pgx_kb import PharmGKBSearcher, LEVEL_CONF as PGX_LEVEL_CONF
except Exception as _e:  # keep the pipeline importable even if the KB module/tables are absent
    PharmGKBSearcher = None
    PGX_LEVEL_CONF = {}
# Per-gene confidence + contradiction detection (phase 11). Guarded the same way, so the
# pipeline still imports if the module is missing.
try:
    from evidence_ledger import Claim, build_ledger, ledger_to_prompt
except Exception as _e:
    Claim = None
    build_ledger = ledger_to_prompt = None
# Contradiction resolution (phase 13): normalises claims, groups them and explains WHY
# sources disagree, instead of only flagging that they do.
try:
    from contradiction_layer import build_cards, cards_to_prompt
except Exception as _e:
    build_cards = cards_to_prompt = None

@dataclass
class MedicalEntity:
    """Represents a medical entity in the knowledge graph"""
    name: str
    description: str
    entity_type: str  # drug, disease, symptom, treatment, etc.
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)

@dataclass
class MedicalRelation:
    """Represents a relationship between medical entities"""
    source: str
    target: str
    relation_type: str
    confidence: float
    evidence: str
    sources: List[str] = field(default_factory=list)

class MedicalKnowledgeGraph:
    """Dynamic Medical Knowledge Graph with confidence scoring"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entities = {}
        self.relations = []
        
    def add_entity(self, entity: MedicalEntity):
        """Add a medical entity to the graph"""
        self.entities[entity.name] = entity
        self.graph.add_node(
            entity.name,
            description=entity.description,
            entity_type=entity.entity_type,
            confidence=entity.confidence,
            sources=entity.sources
        )
        
    def add_relation(self, relation: MedicalRelation):
        """Add a relationship between entities"""
        self.relations.append(relation)
        self.graph.add_edge(
            relation.source,
            relation.target,
            relation_type=relation.relation_type,
            confidence=relation.confidence,
            evidence=relation.evidence,
            sources=relation.sources
        )
        
    def get_connected_nodes(self, node_name: str, confidence_threshold: float = 0.5):
        """Get nodes connected to a given node with confidence above threshold"""
        connected = []
        if node_name in self.graph:
            for neighbor in self.graph.neighbors(node_name):
                edge_data = self.graph[node_name][neighbor]
                if edge_data.get('confidence', 0) >= confidence_threshold:
                    connected.append({
                        'node': neighbor,
                        'relation': edge_data.get('relation_type'),
                        'confidence': edge_data.get('confidence'),
                        'evidence': edge_data.get('evidence')
                    })
        return connected
    
    def explore_path(self, start_node: str, max_depth: int = 3, 
                    confidence_threshold: float = 0.5):
        """Explore paths from a starting node with confidence propagation"""
        paths = []
        visited = set()
        
        def dfs(node, path, accumulated_confidence, depth):
            if depth > max_depth or node in visited:
                return
            
            visited.add(node)
            
            if len(path) > 0:
                paths.append({
                    'path': path.copy(),
                    'confidence': accumulated_confidence,
                    'final_node': node
                })
            
            for neighbor_data in self.get_connected_nodes(node, confidence_threshold):
                neighbor = neighbor_data['node']
                new_confidence = accumulated_confidence * neighbor_data['confidence']
                
                if new_confidence >= confidence_threshold:
                    new_path = path + [(node, neighbor, neighbor_data['relation'])]
                    dfs(neighbor, new_path, new_confidence, depth + 1)
            
            visited.remove(node)
        
        dfs(start_node, [], 1.0, 0)
        return paths

# Ordering used to pick the strongest study type a paper's read sections reported.
STUDY_RANK = {"meta_analysis": 6, "systematic_review": 6, "gwas": 5, "human_cohort": 4,
              "clinical_trial": 4, "case_report": 3, "review": 2, "animal": 1, "in_vitro": 1}


def _xml_text(elem) -> str:
    """Flatten an XML element (with inline markup) to a plain string."""
    if elem is None:
        return ""
    return " ".join("".join(elem.itertext()).split())


class PubMedSearcher:
    """PubMed E-utilities wrapper with provenance (PMIDs), caching, rate limiting,
    and optional PMC full-text retrieval (phase 5).

    All fetch methods return "detailed" records:
        {source, ref, pmid, title, abstract, journal, year, text}
    where `text` is the prompt-ready evidence string tagged with its PMID, and `ref`
    is the stable citation id (PMID:xxx, extended with /PMC:xxx when full text is used).
    The legacy `search()` -> List[str] contract is preserved on top of these.
    """

    # NCBI allows ~3 req/s without an API key (10/s with one); stay under it.
    _MIN_INTERVAL = 0.34

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self._last_call = 0.0
        self._article_cache: Dict[str, dict] = {}   # pmid -> detailed record
        self._fulltext_cache: Dict[str, Optional[dict]] = {}  # pmid -> fulltext record | None
        self._search_cache: Dict[tuple, List[str]] = {}  # (query, retmax) -> pmids

    def _get(self, url: str, params: dict) -> requests.Response:
        """Rate-limited GET against NCBI (adds api_key when configured)."""
        wait = self._MIN_INTERVAL - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        if self.api_key:
            params = {**params, "api_key": self.api_key}
        resp = requests.get(url, params=params, timeout=20)
        self._last_call = time.monotonic()
        resp.raise_for_status()
        return resp

    # ---- abstracts ---------------------------------------------------------
    def search_pmids(self, query: str, max_results: int = 3) -> List[str]:
        # The same query is issued at several pipeline stages; cache so NCBI sees it once.
        ck = (query, max_results)
        if ck in self._search_cache:
            return self._search_cache[ck]
        try:
            resp = self._get(f"{self.base_url}/esearch.fcgi",
                             {"db": "pubmed", "term": query, "retmode": "xml",
                              "retmax": max_results})
            root = ET.fromstring(resp.text)
            pmids = [e.text for e in root.findall(".//Id") if e.text]
            self._search_cache[ck] = pmids
            return pmids
        except Exception as e:
            print(f"PubMed esearch error: {e}")
            return []

    def fetch_by_pmids(self, pmids: List[str]) -> List[dict]:
        """Detailed records for specific PMIDs (order preserved, cached)."""
        todo = [p for p in pmids if p and p not in self._article_cache]
        if todo:
            try:
                resp = self._get(f"{self.base_url}/efetch.fcgi",
                                 {"db": "pubmed", "id": ",".join(todo), "retmode": "xml"})
                root = ET.fromstring(resp.text)
                for art in root.findall(".//PubmedArticle"):
                    pmid = (art.findtext(".//MedlineCitation/PMID") or "").strip()
                    if not pmid:
                        continue
                    title = _xml_text(art.find(".//Article/ArticleTitle"))
                    abstract = " ".join(
                        _xml_text(a) for a in art.findall(".//Abstract/AbstractText"))
                    journal = _xml_text(art.find(".//Journal/Title"))
                    year = art.findtext(".//JournalIssue/PubDate/Year") or ""
                    doi = ""
                    for aid in art.findall(".//ArticleId"):
                        if (aid.get("IdType") or "").lower() == "doi" and aid.text:
                            doi = aid.text.strip()
                            break
                    src_tag = f" ({journal}, {year})" if journal else ""
                    self._article_cache[pmid] = {
                        "source": "PubMed",
                        "ref": f"PMID:{pmid}",
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "journal": journal,
                        "year": year,
                        "doi": doi,
                        "text": f"[PMID {pmid}]{src_tag} {title} {abstract}".strip()[:2000],
                    }
            except Exception as e:
                print(f"PubMed efetch error for {todo}: {e}")
        # Return copies so callers (e.g. full-text upgrade) can't corrupt the cache.
        return [dict(self._article_cache[p]) for p in pmids if p in self._article_cache]

    def search_detailed(self, query: str, max_results: int = 3) -> List[dict]:
        return self.fetch_by_pmids(self.search_pmids(query, max_results))

    def search(self, query: str, max_results: int = 3) -> List[str]:
        """Legacy contract: PMID-tagged abstract strings."""
        return [d["text"] for d in self.search_detailed(query, max_results)]

    # ---- full text (phase 5) ----------------------------------------------
    def pmcid_for_pmid(self, pmid: str) -> str:
        """Map a PMID to its PMC id via elink ('' if the article is not in PMC)."""
        try:
            resp = self._get(f"{self.base_url}/elink.fcgi",
                             {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "retmode": "xml"})
            root = ET.fromstring(resp.text)
            for linkset in root.findall(".//LinkSetDb"):
                if linkset.findtext("LinkName") == "pubmed_pmc":
                    pmc_num = linkset.findtext("Link/Id")
                    if pmc_num:
                        return f"PMC{pmc_num}"
        except Exception as e:
            print(f"PubMed elink error for PMID {pmid}: {e}")
        return ""

    @staticmethod
    def _jats_paragraphs(root) -> List[dict]:
        """Paragraphs of a JATS <body>, each tagged with its innermost <sec> title.

        Shared by PMC and Europe PMC, which both serve JATS XML."""
        body = root.find(".//body")
        if body is None:
            return []
        sec_of = {}
        for sec in body.iter("sec"):
            title = (sec.findtext("title") or "").strip()
            if not title:
                continue
            for p in sec.iter("p"):
                sec_of[id(p)] = title
        out = []
        for p in body.iter("p"):
            text = _xml_text(p)
            if len(text) > 80:
                out.append({"text": text, "section": sec_of.get(id(p), "")})
        return out

    def _europepmc_paragraphs(self, pmid: str) -> Tuple[List[dict], str]:
        """Europe PMC full text -> ([{text, section}], pmcid).

        Europe PMC mirrors PMC but also serves author manuscripts and other open content PMC
        does not expose, so it recovers articles the PMC route misses. Free, no key."""
        base = "https://www.ebi.ac.uk/europepmc/webservices/rest"
        try:
            r = requests.get(f"{base}/search",
                             params={"query": f"EXT_ID:{pmid} AND SRC:MED",
                                     "resultType": "core", "format": "json"}, timeout=20)
            r.raise_for_status()
            hits = (r.json().get("resultList") or {}).get("result") or []
            if not hits:
                return [], ""
            hit = hits[0]
            if hit.get("inEPMC") != "Y" or not hit.get("pmcid"):
                return [], ""            # indexed but full text not served
            pmcid = hit["pmcid"]
            x = requests.get(f"{base}/{pmcid}/fullTextXML", timeout=30)
            x.raise_for_status()
            return self._jats_paragraphs(ET.fromstring(x.text)), pmcid
        except Exception as e:
            print(f"Europe PMC fetch error for PMID {pmid}: {e}")
            return [], ""

    def _unpaywall_pdf(self, doi: str, max_chars: int) -> str:
        """Legally-available OA copy located via Unpaywall, extracted with pypdf.

        Unpaywall indexes publisher OA, accepted manuscripts and repository deposits, so it
        reaches content that is paywalled at the publisher but openly posted elsewhere. It
        needs only an email address (UNPAYWALL_EMAIL), never a subscription credential."""
        email = os.environ.get("UNPAYWALL_EMAIL", "").strip()
        if not doi or not email:
            return ""
        try:
            from pypdf import PdfReader
        except ImportError:
            print("[unpaywall] pypdf not installed -- skipping the PDF route")
            return ""
        try:
            import io
            r = requests.get(f"https://api.unpaywall.org/v2/{doi}",
                             params={"email": email}, timeout=20)
            r.raise_for_status()
            data = r.json() or {}
            # Try every OA location, REPOSITORY copies first. The large publishers
            # (ScienceDirect, Wiley) answer scripted requests with 403 even for open-access
            # PDFs, so their landing pages are effectively unusable here; repository deposits
            # (PMC, institutional archives, preprint servers) serve the same content openly.
            locs = [l for l in (data.get("oa_locations") or []) if l.get("url_for_pdf")]
            best = data.get("best_oa_location") or {}
            if best.get("url_for_pdf") and best not in locs:
                locs.append(best)
            locs.sort(key=lambda l: 0 if l.get("host_type") == "repository" else 1)
            for loc in locs[:4]:
                url = loc.get("url_for_pdf")
                try:
                    pdf = requests.get(url, timeout=60, headers={
                        "User-Agent": "Mozilla/5.0 (compatible; AMG-RAG/1.0; academic research)"})
                    pdf.raise_for_status()
                    if not pdf.content[:5].startswith(b"%PDF"):
                        continue                      # an HTML interstitial, not a PDF
                    reader = PdfReader(io.BytesIO(pdf.content))
                    chunks = []
                    for page in reader.pages:
                        chunks.append(page.extract_text() or "")
                        if sum(len(c) for c in chunks) >= max_chars * 4:
                            break
                    text = "\n\n".join(chunks).strip()
                    if len(text) > 500:
                        print(f"[unpaywall] {doi} -> {loc.get('host_type','?')} copy "
                              f"({len(text):,} chars)")
                        return text
                except Exception:
                    continue                          # blocked or unreadable: try the next
            return ""
        except Exception as e:
            print(f"Unpaywall fetch error for DOI {doi}: {e}")
            return ""

    def _pmc_xml_paragraphs(self, pmcid: str) -> List[dict]:
        """Full-text body from PMC JATS XML as [{text, section}, ...] (open access only).

        Paragraphs are the unit the digest stage cites, so they are kept separate rather
        than being flattened into one blob. The enclosing <sec> title travels with each
        paragraph: findings live in Results/Discussion, and knowing that is what stops the
        digest from spending its budget on the Introduction."""
        try:
            resp = self._get(f"{self.base_url}/efetch.fcgi",
                             {"db": "pmc", "id": pmcid, "retmode": "xml"})
            return self._jats_paragraphs(ET.fromstring(resp.text))
        except Exception as e:
            print(f"PMC full-text fetch error for {pmcid}: {e}")
            return []

    def _pmc_xml_body(self, pmcid: str) -> str:
        """Full-text body from the PMC JATS XML (open-access articles only)."""
        try:
            resp = self._get(f"{self.base_url}/efetch.fcgi",
                             {"db": "pmc", "id": pmcid, "retmode": "xml"})
            root = ET.fromstring(resp.text)
            body = root.find(".//body")
            if body is None:  # not OA: PMC returns metadata without a <body>
                return ""
            paras = [_xml_text(p) for p in body.iter("p")]
            return "\n".join(p for p in paras if p)
        except Exception as e:
            print(f"PMC full-text fetch error for {pmcid}: {e}")
            return ""

    def _pmc_pdf_text(self, pmcid: str, max_chars: int) -> str:
        """Fallback: download the OA PDF and extract text (needs pypdf; else skip)."""
        try:
            from pypdf import PdfReader
        except ImportError:
            return ""
        try:
            import io
            resp = self._get("https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",
                             {"id": pmcid})
            root = ET.fromstring(resp.text)
            href = ""
            for link in root.findall(".//link"):
                if link.get("format") == "pdf":
                    href = link.get("href", "")
                    break
            if not href:
                return ""
            # The OA service returns ftp:// URLs; the same paths are served over https.
            href = href.replace("ftp://ftp.ncbi.nlm.nih.gov/", "https://ftp.ncbi.nlm.nih.gov/")
            pdf_resp = requests.get(href, timeout=60)
            pdf_resp.raise_for_status()
            reader = PdfReader(io.BytesIO(pdf_resp.content))
            chunks = []
            for page in reader.pages:
                chunks.append(page.extract_text() or "")
                if sum(len(c) for c in chunks) >= max_chars * 2:
                    break
            return "\n".join(chunks)
        except Exception as e:
            print(f"PMC OA PDF fetch error for {pmcid}: {e}")
            return ""

    def fetch_fulltext(self, pmid: str, max_chars: int = 3000) -> Optional[dict]:
        """Full text for a PMID, trying the legally-open routes in order of quality.

          1. PMC JATS XML      -- structured, section-tagged paragraphs
          2. Europe PMC XML    -- same structure; also serves author manuscripts PMC omits
          3. Unpaywall -> PDF  -- publisher OA / accepted manuscript / repository deposit
          4. PMC OA PDF        -- last resort

        Every route uses openly available content only: no subscription credentials and no
        proxy login, which library licences prohibit using for automated retrieval.

        Returns {pmcid, via, chars_total, text, paragraphs} or None. Cached per PMID.
        """
        if pmid in self._fulltext_cache:
            return self._fulltext_cache[pmid]
        record, paras, via, pmcid = None, [], "", ""

        # 1. PubMed Central
        pmcid = self.pmcid_for_pmid(pmid)
        if pmcid:
            paras, via = self._pmc_xml_paragraphs(pmcid), "pmc_xml"

        # 2. Europe PMC -- wider open corpus than PMC
        if not paras:
            paras, epmc_id = self._europepmc_paragraphs(pmid)
            if paras:
                via, pmcid = "europepmc_xml", (epmc_id or pmcid)

        # 3. Unpaywall -- a legally-posted OA copy elsewhere
        if not paras:
            art = self._article_cache.get(pmid) or {}
            text = self._unpaywall_pdf(art.get("doi", ""), max_chars)
            if text:
                paras, via = ([{"text": x.strip(), "section": ""}
                               for x in text.split("\n\n") if len(x.strip()) > 80],
                              "unpaywall_pdf")

        # 4. PMC open-access PDF
        if not paras and pmcid:
            text = self._pmc_pdf_text(pmcid, max_chars)
            if text:
                paras, via = ([{"text": x.strip(), "section": ""}
                               for x in text.split("\n\n") if len(x.strip()) > 80],
                              "pmc_pdf")

        if paras:
            text = "\n".join(p["text"] for p in paras)
            record = {"pmcid": pmcid, "via": via, "chars_total": len(text),
                      "text": text[:max_chars], "paragraphs": paras}
        self._fulltext_cache[pmid] = record
        return record

class AMG_RAG_System:
    """Main AMG-RAG system for medical question answering"""
    
    def __init__(self, use_openai: bool = True, openai_key: str = None):
        # Initialize LLM.
        # If LLM_BASE_URL is set (e.g. an Ollama server exposing the OpenAI-compatible
        # /v1 endpoint), route all calls there via ChatOpenAI. This lets us use a custom
        # local/remote model without any real OpenAI account.
        llm_base_url = os.environ.get("LLM_BASE_URL", "").strip()
        llm_model = os.environ.get("LLM_MODEL", "").strip()

        if llm_base_url:
            openai_kwargs = dict(
                model=llm_model or "llama3.1:8b",
                temperature=0.0,
                api_key=openai_key or "ollama",
                base_url=llm_base_url,
            )
            # ngrok tunnels need this header to bypass the browser-warning interstitial.
            extra_headers = os.environ.get("LLM_EXTRA_HEADERS", "").strip()
            if extra_headers:
                try:
                    openai_kwargs["default_headers"] = json.loads(extra_headers)
                except json.JSONDecodeError:
                    pass
            self.llm = ChatOpenAI(**openai_kwargs)
        elif use_openai and openai_key:
            self.llm = ChatOpenAI(
                model=llm_model or "gpt-4o-mini",  # Use gpt-4o-mini for cost efficiency
                temperature=0.0,
                api_key=openai_key
            )
        else:
            # Fallback to local Ollama if available
            if ChatOllama is not None:
                self.llm = ChatOllama(
                    model=llm_model or "llama3.2",
                    temperature=0.0
                )
            else:
                raise ImportError("Neither OpenAI API key provided nor Ollama available. Please install langchain_ollama or provide OpenAI API key.")
            
        # Offline mode: when AMG_USE_EXTERNAL=0, use ONLY the provided question -- no
        # PubMed, no Wikipedia, no vector store. The KG is built by the LLM alone. Default
        # "1" preserves the original online behaviour for the MCQ path.
        self.use_external_sources = os.environ.get("AMG_USE_EXTERNAL", "1") != "0"

        # Open-ended answer style. "doctor" (default) = empathetic patient reply, used for
        # GenMedGPT-5k. "pgx" = terse factual pharmacogenomics statement, used for the
        # PharmGKB/ADR dataset whose references are single factual sentences. Selects which
        # answer chain reason_open_with_graph uses.
        self.answer_style = os.environ.get("AMG_ANSWER_STYLE", "doctor").strip().lower()

        # Knowledge-base source for external evidence. "pubmed" (default) = the paper's live
        # PubMed/Wikipedia retrieval (gated by AMG_USE_EXTERNAL). "pharmgkb" = local ClinPGx
        # tables (clinicalVariants.tsv + relationships.tsv) -- real curated biomarkers with
        # evidence levels, no network. "pharmgkb+pubmed" (phase 4) = ClinPGx first, then a
        # PubMed check: fetch the exact PMIDs relationships.tsv cites for the retrieved
        # gene-drug pairs (topped up by a live search). Needs internet regardless of
        # AMG_USE_EXTERNAL. Selected via _evidence_search at every retrieval seam.
        # "pharmgkb+pubmed_open" (phases 6/7) = ClinPGx grounding kept, but the PubMed
        # search is NOT restricted to the PMIDs ClinPGx cites: an LLM that has seen the
        # question AND the evidence/graph retrieved so far picks the topics to search.
        self.kb_source = os.environ.get("AMG_KB_SOURCE", "pubmed").strip().lower()
        if self.kb_source in ("pubmed+pharmgkb", "phase4"):
            self.kb_source = "pharmgkb+pubmed"
        if self.kb_source in ("phase6", "phase7", "pharmgkb+pubmed+open", "open"):
            self.kb_source = "pharmgkb+pubmed_open"
        # "pharmgkb+pubmed_combo" (phases 8/9) = COMBINED-topic search: entities that are
        # related in the knowledge graph are put into ONE conjunctive PubMed query
        # ("cisplatin AND ACYP2 AND hearing loss") to find literature about the link itself.
        # The LLM decides how many terms to combine per query (the query "arity").
        if self.kb_source in ("phase8", "phase9", "combo", "pharmgkb+pubmed+combo"):
            self.kb_source = "pharmgkb+pubmed_combo"
        # "pharmgkb+pubmed_free" (phase 10) = the model has FULL control of the query: it may
        # search ONE item or combine any number of them, and it writes the PubMed query string
        # itself (field tags, quoted phrases, boolean operators are all allowed). Phases 8/9
        # forced >=2 terms joined by AND; phase 10 removes both the arity floor and the
        # code-imposed phrasing.
        if self.kb_source in ("phase10", "free", "pharmgkb+pubmed+free"):
            self.kb_source = "pharmgkb+pubmed_free"

        # Modes that do a free, LLM-directed PubMed search instead of citation-following.
        self.open_search = self.kb_source in ("pharmgkb+pubmed_open", "pubmed_open")
        self.combo_search = self.kb_source in ("pharmgkb+pubmed_combo", "pubmed_combo")
        self.free_search = self.kb_source in ("pharmgkb+pubmed_free", "pubmed_free")
        # Max terms the model may put in one combined query, and max such queries per stage.
        self.combo_max_terms = int(os.environ.get("AMG_COMBO_MAX_TERMS", "4"))
        # Paper-digest stage (AMG_PAPER_DIGEST=1): instead of pasting raw article text into the
        # prompt, each retrieved paper is READ paragraph by paragraph, the model picks the
        # paragraphs that answer the question, and the final decision is made from ClinPGx plus
        # those per-paper digests (each carrying a paragraph-level citation).
        self.paper_digest = os.environ.get("AMG_PAPER_DIGEST", "0") == "1"
        # Evidence ledger (AMG_EVIDENCE_LEDGER=1): aggregate every claim per gene-drug pair,
        # flag contradictions between the curated tables and the literature, and attach a
        # rule-computed confidence. Recall is the objective -- nothing is suppressed.
        self.evidence_ledger_on = os.environ.get("AMG_EVIDENCE_LEDGER", "0") == "1" and Claim is not None
        # Phase 13: resolve each gene-drug group to CONSISTENT / CONFLICTING /
        # CONTEXT-DEPENDENT / CURATED-LITERATURE CONFLICT / INSUFFICIENT, with the axis that
        # explains the disagreement. Requires the ledger.
        self.contradiction_layer_on = (os.environ.get("AMG_CONTRADICTION_LAYER", "0") == "1"
                                       and build_cards is not None)
        self.digest_max_papers = int(os.environ.get("AMG_DIGEST_MAX_PAPERS", "6"))
        self.digest_batch_chars = int(os.environ.get("AMG_DIGEST_BATCH_CHARS", "2400"))
        self.digest_max_batches = int(os.environ.get("AMG_DIGEST_MAX_BATCHES", "6"))
        self.combo_max_queries = int(os.environ.get("AMG_COMBO_MAX_QUERIES", "4"))
        # How many PubMed hits to take per generated topic phrase.
        self.open_per_phrase = int(os.environ.get("AMG_OPEN_PER_PHRASE", "2"))
        self.max_search_phrases = int(os.environ.get("AMG_MAX_SEARCH_PHRASES", "3"))

        # Phase 5: upgrade PubMed abstracts to full text (PMC JATS XML, OA-PDF fallback)
        # at the reasoning stage. AMG_FULLTEXT_MAX_CHARS caps how much of each article
        # enters the prompt (mind the serving model's context window).
        self.pubmed_fulltext = os.environ.get("AMG_PUBMED_FULLTEXT", "0") == "1"
        self.fulltext_max_chars = int(os.environ.get("AMG_FULLTEXT_MAX_CHARS", "3000"))

        # Per-question provenance: every retrieval appends here (see _log_evidence);
        # answer_question/answer_open_question reset it and attach it to the result.
        self.evidence_log: List[dict] = []
        # Per-question cache of LLM-generated search topics (open-search modes), so the
        # phrase chain runs once per stage instead of once per retrieval call.
        self._phrase_cache: Dict[str, List[str]] = {}
        # Search-shape telemetry for the combined-query phases: one entry per issued query
        # (how many terms, whether it hit, whether it needed a back-off).
        self.combo_stats: List[dict] = []
        # Per-question paper digests (paragraph selections + summaries), attached to results.
        self.paper_digests: List[dict] = []
        self.gene_ledger: List[dict] = []
        self.contradiction_cards: List[dict] = []
        self._current_question: str = ""

        # Initialize components
        self.kg = MedicalKnowledgeGraph()
        self.pubmed = PubMedSearcher(api_key=PUBMED_API_KEY)
        # Load the local ClinPGx KB only in pharmgkb modes (mirrors the embeddings guard
        # below, so default runs pay no load cost).
        if (self.kb_source in ("pharmgkb", "pharmgkb+pubmed", "pharmgkb+pubmed_open",
                               "pharmgkb+pubmed_combo", "pharmgkb+pubmed_free")
                and PharmGKBSearcher is not None):
            clinvar = os.environ.get("AMG_KB_CLINVAR", "").strip() or None
            rel = os.environ.get("AMG_KB_REL", "").strip() or None
            self.pgx = PharmGKBSearcher(*( [clinvar, rel] if clinvar and rel else [] ))
            print(f"[ClinPGx] loaded {len(self.pgx.clinvar_rows)} clinicalVariants rows, "
                  f"{len(self.pgx.pair_assoc)} relationship pairs")
        else:
            self.pgx = None
        if self.use_external_sources:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            self.vector_store = Chroma(
                collection_name="medical_qa",
                embedding_function=self.embeddings
            )
        else:
            # The vector store is never queried in this pipeline; skipping it in offline
            # mode avoids downloading the embedding model.
            self.embeddings = None
            self.vector_store = None

        # Initialize chains
        self._setup_chains()

    def _pgx_enabled(self) -> bool:
        return self.pgx is not None and self.kb_source in (
            "pharmgkb", "pharmgkb+pubmed", "pharmgkb+pubmed_open", "pharmgkb+pubmed_combo",
            "pharmgkb+pubmed_free")

    def _log_evidence(self, stage: str, query: str, items: List[dict]) -> None:
        """Append retrieval provenance to the per-question evidence log (+ stdout line)."""
        if not items:
            return
        for it in items:
            entry = {
                "stage": stage,
                "query": query[:200],
                "source": it.get("source"),
                "ref": it.get("ref"),
                "snippet": (it.get("text") or "")[:300],
            }
            for k in ("title", "journal", "year", "level", "pmids", "via", "pmcid"):
                if it.get(k):
                    entry[k] = it[k]
            self.evidence_log.append(entry)
        refs = ", ".join(str(it.get("ref")) for it in items)
        print(f"[evidence] stage={stage} -> {len(items)} item(s): {refs}")

    def collect_references(self) -> List[dict]:
        """Deduplicated citation list for everything retrieved for the current question."""
        seen, refs = set(), []
        for e in self.evidence_log:
            ref = e.get("ref")
            if not ref or ref in seen:
                continue
            seen.add(ref)
            refs.append({"ref": ref, "source": e.get("source"),
                         "title": e.get("title", ""), "stages": [e["stage"]]})
        # record every stage each reference was used in
        by_ref = {r["ref"]: r for r in refs}
        for e in self.evidence_log:
            r = by_ref.get(e.get("ref"))
            if r and e["stage"] not in r["stages"]:
                r["stages"].append(e["stage"])
        return refs

    @staticmethod
    def _clean_phrase(p: str) -> str:
        """Keep phrases short and PubMed-shaped: no sentences, no boolean operators."""
        p = re.sub(r"[^\w\s\*\-]", " ", str(p or ""))
        p = re.sub(r"\b(AND|OR|NOT)\b", " ", p)
        p = " ".join(p.split())
        return " ".join(p.split()[:6])

    def _fallback_phrases(self, query: str, items: List[dict]) -> List[str]:
        """Entity-derived topics used when the LLM phrase chain fails or returns junk.

        Built from what retrieval already produced (gene/drug/phenotype), which is still far
        better than sending a whole patient-style sentence to esearch."""
        out = []
        for it in items:
            if it.get("source") != "ClinPGx":
                continue
            gene, drug = it.get("gene", ""), it.get("drug", "")
            phen = (it.get("phenotypes") or [""])[0]
            for cand in (f"{gene} {drug} {phen}", f"{gene} {drug}", f"{drug} {phen}"):
                cand = self._clean_phrase(cand)
                if len(cand.split()) >= 2 and cand not in out:
                    out.append(cand)
                    break
        if not out and self.pgx is not None:
            ents = self.pgx.extract_entities(query)
            drug = (ents.get("drugs") or [""])[0]
            phen = (ents.get("phenotypes") or [""])[0]
            gene = (ents.get("genes") or [""])[0]
            for cand in (f"{drug} {phen} pharmacogenomics", f"{gene} {drug}", f"{drug} {phen}"):
                cand = self._clean_phrase(cand)
                if len(cand.split()) >= 2 and cand not in out:
                    out.append(cand)
        return out[:self.max_search_phrases]

    def _search_topics(self, query: str, items: List[dict], stage: str) -> List[str]:
        """LLM-chosen PubMed topics for the open-search phases, aware of the graph + query.

        Cached per (stage, query) so the chain runs about twice per question rather than once
        per retrieval call. Falls back to entity-derived phrases if the model misbehaves."""
        key = f"{stage}::{query[:120]}"
        if key in self._phrase_cache:
            return self._phrase_cache[key]

        # Context = what retrieval/the graph already knows: ClinPGx rows + KG entity names.
        ctx_lines = [it["text"] for it in items if it.get("text")][:5]
        if self.kg.entities:
            ctx_lines.append("Knowledge-graph entities: "
                             + ", ".join(list(self.kg.entities.keys())[:12]))
        context = "\n".join(ctx_lines) or "No evidence retrieved yet."

        phrases = []
        try:
            res = self.search_phrase_chain.invoke({"question": query[:1200], "context": context[:2000]})
            raw = res.get("search_phrases", []) or []
            for p in raw:
                if isinstance(p, dict):
                    p = p.get("phrase") or p.get("text") or p.get("query") or ""
                p = self._clean_phrase(p)
                if len(p.split()) >= 2 and p.lower() not in [x.lower() for x in phrases]:
                    phrases.append(p)
        except Exception as e:
            print(f"Search-phrase generation error: {e}")

        if not phrases:
            phrases = self._fallback_phrases(query, items)
            if phrases:
                print(f"[topics] fallback phrases used: {phrases}")
        phrases = phrases[:self.max_search_phrases]
        if phrases:
            print(f"[topics] stage={stage} -> {phrases}")
        self._phrase_cache[key] = phrases
        return phrases

    def _open_pubmed_search(self, query: str, items: List[dict], stage: str,
                            max_results: int) -> List[dict]:
        """Free topic-driven PubMed search (phases 6/7).

        Not restricted to the PMIDs ClinPGx cites: the LLM picks the topics, each topic is
        searched SEPARATELY (short queries work; whole sentences return nothing), and hits are
        interleaved round-robin so every topic contributes."""
        if stage.startswith("entity:"):
            # The query IS a single entity name here -- already a good short PubMed query.
            # Calling the topic chain per entity would cost ~8 extra LLM calls per question
            # for no gain, so search the entity directly and reserve the LLM for the
            # question-level and reasoning-level stages.
            topics = [self._clean_phrase(query)]
        else:
            topics = self._search_topics(query, items, stage)
        if not topics:
            return []
        per_topic = []
        for ph in topics:
            hits = self.pubmed.search_detailed(ph, max_results=self.open_per_phrase)
            for d in hits:
                d["via"] = f"llm_topic:{ph}"
                d["topic"] = ph
            per_topic.append(hits)

        out, seen = [], set()
        for rank in range(max(len(h) for h in per_topic)):   # round-robin across topics
            for hits in per_topic:
                if rank < len(hits) and hits[rank]["pmid"] not in seen:
                    seen.add(hits[rank]["pmid"])
                    out.append(hits[rank])
                    if len(out) >= max_results:
                        return out
        return out

    def _graph_relation_context(self, limit: int = 12) -> str:
        """Compact view of the KG edges, so the query builder can see what is related."""
        lines = []
        for rel in self.kg.relations:
            if rel.confidence < 0.3:
                continue
            lines.append(f"{rel.source} -[{rel.relation_type}]-> {rel.target}")
            if len(lines) >= limit:
                break
        return "\n".join(dict.fromkeys(lines)) or "No relations extracted yet."

    def _question_anchors(self) -> List[str]:
        """Drug / adverse-effect terms from the CURRENT question, used to keep entity-level
        combined queries anchored to what was actually asked."""
        if self.pgx is None or not self._current_question:
            return []
        ents = self.pgx.extract_entities(self._current_question)
        out = []
        if ents.get("drugs"):
            out.append(ents["drugs"][0])
        if ents.get("phenotypes"):
            out.append(ents["phenotypes"][0])
        return out

    def _combo_groups(self, query: str, items: List[dict], stage: str) -> List[List[str]]:
        """Term groups to search together. LLM-chosen at question/reasoning stages; at entity
        stages the entity is deterministically paired with the question's drug/adverse effect
        (which is itself a graph-related pair, and keeps entity searches on topic)."""
        if stage.startswith("entity:"):
            anchors = self._question_anchors()
            terms = [self._clean_phrase(query)] + anchors[:2]
            terms = [t for t in dict.fromkeys(t for t in terms if t)]
            return [terms] if len(terms) >= 2 else ([terms] if terms else [])

        key = f"combo::{stage}::{query[:120]}"
        if key in self._phrase_cache:
            return self._phrase_cache[key]

        ctx = "\n".join(it["text"] for it in items if it.get("text"))[:1500] or "None yet."
        groups: List[List[str]] = []
        try:
            res = self.combo_query_chain.invoke({
                "question": query[:1200], "relations": self._graph_relation_context(),
                "context": ctx, "max_queries": self.combo_max_queries,
                "max_terms": self.combo_max_terms})
            for g in (res.get("combined_queries", []) or []):
                if isinstance(g, dict):
                    g = g.get("query") or g.get("terms") or g.get("group") or ""
                if isinstance(g, list):
                    parts = [str(x) for x in g]
                else:
                    parts = str(g).split("+")
                terms = [t for t in (self._clean_phrase(x) for x in parts) if t]
                terms = list(dict.fromkeys(terms))[:self.combo_max_terms]
                if len(terms) >= 2 and terms not in groups:
                    groups.append(terms)
        except Exception as e:
            print(f"Combined-query generation error: {e}")

        if not groups:   # fall back to pairing ClinPGx genes with the question's drug
            anchors = self._question_anchors()
            drug = anchors[0] if anchors else ""
            for it in items:
                if it.get("source") == "ClinPGx" and it.get("gene") and drug:
                    pair = [self._clean_phrase(it["gene"]), self._clean_phrase(drug)]
                    if pair not in groups:
                        groups.append(pair)
                if len(groups) >= self.combo_max_queries:
                    break
            if groups:
                print(f"[combo] fallback groups: {groups}")

        groups = groups[:self.combo_max_queries]
        if groups:
            print(f"[combo] stage={stage} arities={[len(g) for g in groups]} -> {groups}")
        self._phrase_cache[key] = groups
        return groups

    def _combo_pubmed_search(self, query: str, items: List[dict], stage: str,
                             max_results: int) -> List[dict]:
        """Phases 8/9: search RELATED terms together as one conjunctive PubMed query.

        A conjunction is precise but can over-constrain, so an empty result backs off by
        dropping the last term and retrying (3 terms -> 2 terms). Every issued query is
        recorded in self.combo_stats, which is what the search-shape report is built from."""
        groups = self._combo_groups(query, items, stage)
        if not groups:
            return []
        collected = []
        for terms in groups:
            arity = len(terms)
            used, hits, backoff = list(terms), [], 0
            while used:
                term = " AND ".join(used)
                hits = self.pubmed.search_detailed(term, max_results=self.open_per_phrase)
                if hits or len(used) <= 2:
                    break
                used = used[:-1]      # over-constrained: relax by one term
                backoff += 1
            self.combo_stats.append({
                "stage": stage, "requested_arity": arity, "used_arity": len(used),
                "terms": used, "backoffs": backoff, "hits": len(hits),
            })
            for d in hits:
                d["via"] = f"combo{len(used)}:{' + '.join(used)}"
                d["combo_arity"] = len(used)
            collected.append(hits)

        out, seen = [], set()
        for rank in range(max((len(h) for h in collected), default=0)):
            for hits in collected:
                if rank < len(hits) and hits[rank]["pmid"] not in seen:
                    seen.add(hits[rank]["pmid"])
                    out.append(hits[rank])
                    if len(out) >= max_results:
                        return out
        return out

    @staticmethod
    def _sanitize_query(q: str) -> str:
        """Light hygiene only -- the model's phrasing is preserved on purpose in phase 10.

        Strips control characters and over-long strings but keeps quotes, boolean operators and
        PubMed field tags intact, because authoring those is the point of this phase. The one
        repair is closing the space before a field tag (`ototoxicity [tiab]` ->
        `ototoxicity[tiab]`), which is the documented form. That is hygiene rather than the
        cure: the empty queries in the first phase-10 run were mostly caused by tags that do
        not exist as written (e.g. `pharmacogenomics[sb]`), which _relax_query handles."""
        q = " ".join(str(q or "").split())
        q = re.sub(r"[\x00-\x1f]", " ", q)
        q = re.sub(r"\s+(\[[A-Za-z]{2,10}\])", r"\1", q)
        return q[:300].strip()

    @staticmethod
    def _relax_query(q: str) -> str:
        """One step of back-off for a query that matched nothing.

        Order: drop field tags (the most common cause of a zero-hit query), then drop the last
        AND-term, then give up. Returns "" when there is nothing left to relax."""
        if re.search(r"\[[A-Za-z]{2,10}\]", q):
            return re.sub(r"\s*\[[A-Za-z]{2,10}\]", "", q).strip()
        parts = re.split(r"\s+AND\s+", q)
        if len(parts) > 1:
            return " AND ".join(parts[:-1]).strip()
        return ""

    def _free_queries(self, query: str, items: List[dict], stage: str) -> List[dict]:
        """Model-authored queries: [{'query': str, 'items': [str], 'arity': int}].

        No arity floor and no code-side query assembly -- a single-concept query is as valid as
        a five-concept one. Entity stages reuse the question-level plan rather than issuing a
        bare entity name, so the model's strategy governs the whole question."""
        key = f"free::{'entity' if stage.startswith('entity:') else stage}::{self._current_question[:120]}"
        if key in self._phrase_cache:
            return self._phrase_cache[key]

        ctx = "\n".join(it["text"] for it in items if it.get("text"))[:1500] or "None yet."
        out: List[dict] = []
        try:
            res = self.free_query_chain.invoke({
                "question": (self._current_question or query)[:1200],
                "relations": self._graph_relation_context(),
                "context": ctx, "max_queries": self.combo_max_queries})
            for g in (res.get("queries", []) or []):
                if isinstance(g, str):          # model returned a bare string
                    g = {"query": g, "items": [g]}
                if not isinstance(g, dict):
                    continue
                qs = self._sanitize_query(g.get("query") or g.get("term") or "")
                its = g.get("items") or g.get("concepts") or []
                if isinstance(its, str):
                    its = [x.strip() for x in re.split(r"[,;+]", its) if x.strip()]
                its = [str(x).strip() for x in its if str(x).strip()]
                if not qs:
                    continue
                if not its:                      # infer arity if the model omitted the list
                    its = [t for t in re.split(r"\bAND\b", qs) if t.strip()]
                if qs not in [o["query"] for o in out]:
                    out.append({"query": qs, "items": its, "arity": max(1, len(its))})
        except Exception as e:
            print(f"Free-query generation error: {e}")

        if not out:   # fall back to gene+drug pairs, same as the combo phases
            for grp in self._combo_groups(query, items, "reasoning"):
                out.append({"query": " AND ".join(grp), "items": grp, "arity": len(grp)})
            if out:
                print(f"[free] fallback queries: {[o['query'] for o in out]}")

        out = out[:self.combo_max_queries]
        if out:
            print(f"[free] stage={stage} arities={[o['arity'] for o in out]} -> "
                  f"{[o['query'] for o in out]}")
        self._phrase_cache[key] = out
        return out

    def _free_pubmed_search(self, query: str, items: List[dict], stage: str,
                            max_results: int) -> List[dict]:
        """Phase 10: run the model's own queries verbatim, whatever their arity or phrasing."""
        plans = self._free_queries(query, items, stage)
        if not plans:
            return []
        per_query = []
        for plan in plans:
            # Send the model's query verbatim; if it matches nothing, relax it step by step
            # (drop field tags, then drop the last AND-term) rather than losing the query.
            q, hits, backoff = plan["query"], [], 0
            while q:
                hits = self.pubmed.search_detailed(q, max_results=self.open_per_phrase)
                if hits:
                    break
                nxt = self._relax_query(q)
                if not nxt or nxt == q:
                    break
                q, backoff = nxt, backoff + 1
            self.combo_stats.append({
                "stage": stage, "requested_arity": plan["arity"],
                "used_arity": max(1, len(re.split(r"\s+AND\s+", q))) if q else plan["arity"],
                "terms": plan["items"], "query": plan["query"], "query_used": q,
                "backoffs": backoff, "hits": len(hits), "authored": True,
            })
            for d in hits:
                d["via"] = f"free{plan['arity']}:{q}"
                d["combo_arity"] = plan["arity"]
            per_query.append(hits)

        out, seen = [], set()
        for rank in range(max((len(h) for h in per_query), default=0)):
            for hits in per_query:
                if rank < len(hits) and hits[rank]["pmid"] not in seen:
                    seen.add(hits[rank]["pmid"])
                    out.append(hits[rank])
                    if len(out) >= max_results:
                        return out
        return out

    def _evidence_search_detailed(self, query: str, max_results: int = 3,
                                  stage: str = "general") -> List[dict]:
        """Unified external-evidence retrieval with provenance.

        Routing by AMG_KB_SOURCE:
          pharmgkb         -> local ClinPGx tables only (offline)
          pharmgkb+pubmed  -> phase 4: ClinPGx first, then PubMed -- preferring the exact
                              PMIDs relationships.tsv cites for the retrieved pairs,
                              topping up with a live esearch on the query
          pubmed (default) -> live PubMed, gated by AMG_USE_EXTERNAL
        With AMG_PUBMED_FULLTEXT=1 (phase 5), PubMed abstracts retrieved at the
        "reasoning" stage are upgraded to PMC full text when available.
        Every item is appended to self.evidence_log under `stage`.
        """
        items: List[dict] = []
        if self._pgx_enabled():
            items.extend(self.pgx.search_detailed(query, max_results=max_results))

        use_pubmed = (self.kb_source in ("pharmgkb+pubmed", "pharmgkb+pubmed_open",
                                         "pubmed_open", "pharmgkb+pubmed_combo", "pubmed_combo",
                                         "pharmgkb+pubmed_free", "pubmed_free")
                      or (self.kb_source != "pharmgkb" and self.use_external_sources))
        if use_pubmed and self.free_search:
            # Phase 10: the model authored both the arity and the query string.
            pub_items = self._free_pubmed_search(query, items, stage, max_results)
        elif use_pubmed and self.combo_search:
            # Phases 8/9: graph-related terms searched together as one conjunctive query.
            pub_items = self._combo_pubmed_search(query, items, stage, max_results)
        elif use_pubmed and self.open_search:
            # Phases 6/7: topics chosen by the LLM from question + retrieved graph evidence.
            pub_items = self._open_pubmed_search(query, items, stage, max_results)
        elif use_pubmed:
            pub_items: List[dict] = []
            cited_pmids = []
            for it in items:  # phase 4: verify ClinPGx claims via their cited literature
                for p in it.get("pmids", []):
                    if p not in cited_pmids:
                        cited_pmids.append(p)
            if cited_pmids:
                pub_items = self.pubmed.fetch_by_pmids(cited_pmids[:max_results])
                for d in pub_items:
                    d["via"] = "clinpgx_citation"
            if len(pub_items) < max_results:
                have = {d["pmid"] for d in pub_items}
                extra = self.pubmed.search_detailed(query, max_results - len(pub_items))
                pub_items += [d for d in extra if d["pmid"] not in have]

        if use_pubmed:
            # Phase 5/7: full text only at the reasoning stage -- entity enrichment truncates
            # descriptions to 500 chars anyway, so full text there would be wasted calls.
            if self.pubmed_fulltext and stage == "reasoning":
                for d in pub_items[:2]:
                    ft = self.pubmed.fetch_fulltext(d["pmid"], self.fulltext_max_chars)
                    if ft:
                        via = "+".join(v for v in (d.get("via"), ft["via"]) if v)
                        d.update({"pmcid": ft["pmcid"], "via": via,
                                  "ref": f"PMID:{d['pmid']}/{ft['pmcid']}"})
                        d["text"] = (f"[PMID {d['pmid']} | {ft['pmcid']} full text via "
                                     f"{ft['via']}] {d['title']} :: {ft['text']}")
            items.extend(pub_items)

        self._log_evidence(stage, query, items)
        return items

    def _evidence_search(self, query: str, max_results: int = 3,
                         stage: str = "general") -> List[str]:
        """List[str] wrapper over _evidence_search_detailed (legacy contract)."""
        return [d["text"] for d in
                self._evidence_search_detailed(query, max_results=max_results, stage=stage)]

    def _has_external_evidence(self) -> bool:
        """True when some evidence source is active (live PubMed or the local ClinPGx KB)."""
        return (self.use_external_sources or self._pgx_enabled()
                or self.kb_source == "pharmgkb+pubmed")

    def _seed_pgx_edges(self, question: str, options: Dict[str, str], max_records: int = 10) -> None:
        """Insert real ClinPGx gene/variant-drug-phenotype edges into the KG (pharmgkb mode).

        Edges are oriented drug/phenotype -> gene -> variant so that exploring from the
        drug/phenotype entities (which the LLM extracts from the question) reaches the curated
        biomarkers. Confidence is derived from the PharmGKB evidence level (>=0.4 so level-3/4
        edges clear the 0.3 path-exploration threshold)."""
        if not self._pgx_enabled():
            return
        text = question + " " + " ".join(options.values())
        ents = self.pgx.extract_entities(text)
        drugs = ents["drugs"] or []
        phenos = ents["phenotypes"] or [""]
        seen, added = set(), 0
        for drug in drugs:
            for pheno in phenos:
                for row in self.pgx.lookup_for_pair(drug, pheno):
                    gene = row["gene_disp"] or row["gene"].upper()
                    variant = row["variants"][0] if row["variants"] else ""
                    level = (row["level"] or "").upper()
                    key = (gene, variant, drug, pheno)
                    if not gene or key in seen:
                        continue
                    seen.add(key)
                    conf = PGX_LEVEL_CONF.get(row["level"], 0.4)
                    phen_name = row["phenotypes"][0] if row["phenotypes"] else (pheno or "adverse reaction")
                    ev = f"PharmGKB level {level or 'n/a'} evidence ({row['type'] or 'PGx'})"
                    self.kg.add_entity(MedicalEntity(gene, f"Gene ({row['type']})", "gene", conf, ["ClinPGx"]))
                    self.kg.add_entity(MedicalEntity(drug, "Drug", "drug", 0.9, ["ClinPGx"]))
                    self.kg.add_entity(MedicalEntity(phen_name, "Phenotype / adverse reaction",
                                                     "phenotype", conf, ["ClinPGx"]))
                    self.kg.add_relation(MedicalRelation(
                        phen_name, gene, f"risk_modulated_by[{level}]", conf, ev, ["ClinPGx"]))
                    self.kg.add_relation(MedicalRelation(
                        drug, gene, f"response_modulated_by[{level}]", conf, ev, ["ClinPGx"]))
                    if variant:
                        self.kg.add_entity(MedicalEntity(variant, f"Variant in {gene}",
                                                         "variant", conf, ["ClinPGx"]))
                        self.kg.add_relation(MedicalRelation(
                            gene, variant, "has_variant", conf, ev, ["ClinPGx"]))
                    added += 1
                    if added >= max_records:
                        break
                if added >= max_records:
                    break
            if added >= max_records:
                break
        if added:
            print(f"[ClinPGx] seeded {added} curated gene-drug-phenotype records into the KG")

    def _pgx_premise_note(self, question: str) -> str:
        """False-premise gating (pharmgkb mode). For each gene+drug pair named in the question,
        if ClinPGx has NO association row (or an explicit 'not associated'), return a corrective
        NOTE. 'ambiguous'/'associated' pairs are left alone. Empty string if nothing to correct."""
        if not self._pgx_enabled():
            return ""
        ents = self.pgx.extract_entities(question)
        genes, drugs = ents.get("genes", []), ents.get("drugs", [])
        notes = []
        for g in genes:
            for d in drugs:
                assoc = self.pgx.is_associated(g, d)
                if assoc is None:
                    notes.append(f"there is no established PharmGKB association between "
                                 f"{g.upper()} and {d}")
                elif assoc == "not associated":
                    notes.append(f"PharmGKB records {g.upper()} as NOT associated with {d}")
        if not notes:
            return ""
        return ("NOTE (ClinPGx gating): " + "; ".join(dict.fromkeys(notes))
                + ". Do not assert an unsupported pharmacogenomic link for these pairs.")

    def _setup_chains(self):
        """Setup LLM chains for various tasks"""
        
        # Enhanced medical entity extraction with relevance scoring
        entity_schemas = [
            ResponseSchema(
                name="entities",
                description="List of medical entities (diseases, drugs, symptoms, treatments)",
                type="array"
            ),
            ResponseSchema(
                name="scores",
                description="Relevance scores (1-10) for each entity based on importance to the question",
                type="array"
            ),
            ResponseSchema(
                name="descriptions",
                description="Brief descriptions of each entity in the context of the question",
                type="array"
            )
        ]
        entity_parser = StructuredOutputParser.from_response_schemas(entity_schemas)
        
        self.entity_extractor = PromptTemplate(
            template="""Extract all medical entities from this question and options with relevance scoring.
            Include diseases, drugs, symptoms, treatments, and medical concepts.
            
            Question: {question}
            Options: {options}
            Context: {context}
            
            For each entity, provide:
            1. Entity name
            2. Relevance score (1-10): 10=directly related to question, 7-9=moderately relevant, 4-6=weakly relevant, 1-3=minimally relevant
            3. Brief description in context of the question
            
            Return in JSON format:
            {format_instructions}""",
            input_variables=["question", "options", "context"],
            partial_variables={"format_instructions": entity_parser.get_format_instructions()}
        ) | self.llm | entity_parser
        
        # Enhanced relation extraction with bidirectional analysis
        # Single array of relationship objects -- matches the prompt's example and the
        # code below that reads entityA/entityB/relationship_type/confidence_score/evidence.
        # (The original 3-parallel-array schema disagreed with the prompt, so every
        # relation extraction failed to parse and the graph had zero edges.)
        relation_schemas = [
            ResponseSchema(
                name="relationships",
                description=("List of relationship objects. Each object has keys: "
                             "entityA, entityB, relationship_type, confidence_score (1-10), evidence."),
                type="array"
            )
        ]
        relation_parser = StructuredOutputParser.from_response_schemas(relation_schemas)
        
        self.relation_extractor = PromptTemplate(
            template="""Analyze the medical relationships between these entities based on the context.
            
            Entity 1: {entity1}
            Description 1: {desc1}
            
            Entity 2: {entity2}  
            Description 2: {desc2}
            
            Context: {context}
            
            Provide relationships in this exact JSON format:
            {{
                "relationships": [
                    {{
                        "entityA": "{entity1}",
                        "entityB": "{entity2}",
                        "relationship_type": "relationship_type_here",
                        "confidence_score": 8,
                        "evidence": "brief evidence here"
                    }},
                    {{
                        "entityA": "{entity2}",
                        "entityB": "{entity1}",
                        "relationship_type": "relationship_type_here",
                        "confidence_score": 7,
                        "evidence": "brief evidence here"
                    }}
                ]
            }}
            
            Use medical relationship types like: treats, causes, symptom_of, risk_factor_for, contraindicated_with, differential_diagnosis, etc.
            Confidence scores: 10=strong evidence, 7-9=moderate evidence, 4-6=weak evidence, 1-3=minimal evidence
            
            Return ONLY the JSON, no other text:""",
            input_variables=["entity1", "desc1", "entity2", "desc2", "context"],
            partial_variables={"format_instructions": relation_parser.get_format_instructions()}
        ) | self.llm | relation_parser
        
        # Entity summarization chain
        summary_schemas = [
            ResponseSchema(
                name="summaries",
                description="Concise summaries for each entity based on context",
                type="array"
            ),
            ResponseSchema(
                name="scores",
                description="Relevance scores (1-10) for each summary",
                type="array"
            )
        ]
        summary_parser = StructuredOutputParser.from_response_schemas(summary_schemas)
        
        self.summary_chain = PromptTemplate(
            template="""Generate concise and relevant summaries for each medical entity based on the given context.
            
            Entities: {entities}
            Context: {context}
            
            For each entity, provide:
            1. A concise summary (2-3 sentences) focusing on relevance to the medical question
            2. Relevance score (1-10): 10=directly relevant, 7-9=moderately relevant, 4-6=weakly relevant, 1-3=minimally relevant
            
            Return in JSON format:
            {format_instructions}""",
            input_variables=["entities", "context"],
            partial_variables={"format_instructions": summary_parser.get_format_instructions()}
        ) | self.llm | summary_parser
        
        # Chain of thought reasoning
        cot_schemas = [
            ResponseSchema(
                name="reasoning",
                description="Step-by-step medical reasoning",
                type="string"
            )
        ]
        cot_parser = StructuredOutputParser.from_response_schemas(cot_schemas)
        
        self.cot_chain = PromptTemplate(
            template="""Based on the medical knowledge graph information and search results,
            provide step-by-step reasoning for this medical question.
            
            Question: {question}
            
            Graph Knowledge:
            {graph_context}
            
            Search Results:
            {search_context}
            
            Provide detailed medical reasoning:
            {format_instructions}""",
            input_variables=["question", "graph_context", "search_context"],
            partial_variables={"format_instructions": cot_parser.get_format_instructions()}
        ) | self.llm | cot_parser
        
        # Final answer generation
        answer_schemas = [
            ResponseSchema(
                name="answer",
                description="Final answer (A, B, C, D, or E)",
                type="string"
            ),
            ResponseSchema(
                name="confidence",
                description="Confidence in the answer (0-1)",
                type="number"
            ),
            ResponseSchema(
                name="explanation",
                description="Brief explanation",
                type="string"
            )
        ]
        answer_parser = StructuredOutputParser.from_response_schemas(answer_schemas)
        
        self.answer_chain = PromptTemplate(
            template="""Based on the reasoning and evidence, select the best answer.
            
            Question: {question}
            Options: {options}
            
            Reasoning:
            {reasoning}
            
            Evidence:
            {evidence}
            
            Select the best answer (A, B, C, D, or E):
            {format_instructions}""",
            input_variables=["question", "options", "reasoning", "evidence"],
            partial_variables={"format_instructions": answer_parser.get_format_instructions()}
        ) | self.llm | answer_parser

        # Open-ended answer generation (no multiple-choice options).
        # Used for free-text datasets such as GenMedGPT-5k where the reference is a
        # doctor-style reply embedding a diagnosis + drug + test recommendation.
        open_answer_schemas = [
            ResponseSchema(
                name="answer",
                description="A complete, empathetic doctor-style free-text reply to the patient "
                            "(2-5 sentences) that states the most likely diagnosis, recommends a "
                            "treatment or drug, and suggests any appropriate diagnostic test.",
                type="string"
            ),
            ResponseSchema(
                name="diagnosis",
                description="The single most likely diagnosis named in the reply.",
                type="string"
            ),
            ResponseSchema(
                name="drugs",
                description="List of drug or treatment names recommended in the reply.",
                type="array"
            ),
            ResponseSchema(
                name="tests",
                description="List of diagnostic tests recommended in the reply.",
                type="array"
            )
        ]
        open_answer_parser = StructuredOutputParser.from_response_schemas(open_answer_schemas)

        self.open_answer_chain = PromptTemplate(
            template="""You are a doctor replying to a patient. Based on the reasoning and evidence
            below, write a helpful, empathetic reply to the patient's message.

            Patient message: {question}

            Reasoning:
            {reasoning}

            Evidence:
            {evidence}

            Give your reply as a single free-text doctor response, and also list the diagnosis,
            recommended drugs/treatments, and recommended tests separately.
            {format_instructions}""",
            input_variables=["question", "reasoning", "evidence"],
            partial_variables={"format_instructions": open_answer_parser.get_format_instructions()}
        ) | self.llm | open_answer_parser

        # Pharmacogenomics answer generation (AMG_ANSWER_STYLE=pgx). The PharmGKB/ADR
        # references are single factual sentences (e.g. "CYP2C9 *3 is associated with
        # decreased dose of warfarin ..."), so the reply must be a terse factual statement,
        # NOT an empathetic patient reply -- otherwise it scores poorly against the reference.
        pgx_answer_schemas = [
            ResponseSchema(
                name="answer",
                description="A concise, factual pharmacogenomic statement (1-2 sentences) naming "
                            "the gene/allele, the drug, and the direction or nature of the effect "
                            "(e.g. increased/decreased metabolism, dose requirement, drug response, "
                            "efficacy, or toxicity/side-effect risk). No patient address, no disclaimers.",
                type="string"
            )
        ]
        pgx_answer_parser = StructuredOutputParser.from_response_schemas(pgx_answer_schemas)

        self.open_pgx_answer_chain = PromptTemplate(
            template="""You are a clinical pharmacogenomics expert. Based on the reasoning and
            evidence below, state the known association between the genetic variant and the drug.

            Question: {question}

            Reasoning:
            {reasoning}

            Evidence:
            {evidence}

            Write a single concise, factual pharmacogenomic statement that names the gene/allele,
            the drug, and the direction or nature of the effect (for example: increased or decreased
            metabolism, dose requirement, drug response/efficacy, or toxicity/side-effect risk).
            Do not address a patient and do not add disclaimers.
            {format_instructions}""",
            input_variables=["question", "reasoning", "evidence"],
            partial_variables={"format_instructions": pgx_answer_parser.get_format_instructions()}
        ) | self.llm | pgx_answer_parser

        # ADR / drug-discovery assessment (AMG_ANSWER_STYLE=adr). The input is a drug ->
        # adverse-reaction pair (e.g. "cisplatin-induced ototoxicity"); there is no gold
        # answer -- we want the system's expert OPINION for a drug-discovery audience, plus
        # the context it assembled. Richer than the terse pgx statement.
        adr_answer_schemas = [
            ResponseSchema(
                name="answer",
                description="A 3-5 sentence expert assessment of this drug-induced adverse reaction "
                            "for a drug-discovery / pharmacovigilance audience: name the implicated "
                            "genes/variants, the likely biological mechanism, and the implications for "
                            "drug development and patient safety (biomarker screening, dose adjustment, "
                            "alternative agents). Specific and factual.",
                type="string"
            ),
            ResponseSchema(
                name="risk_genes",
                description="List of gene or variant names implicated in this adverse reaction.",
                type="array"
            )
        ]
        adr_answer_parser = StructuredOutputParser.from_response_schemas(adr_answer_schemas)

        self.open_adr_answer_chain = PromptTemplate(
            template="""You are a pharmacogenomics and drug-safety expert advising a drug-discovery
            team. Based on the reasoning and evidence below, give your expert assessment of this
            drug-induced adverse reaction.

            Question: {question}

            Reasoning:
            {reasoning}

            Evidence:
            {evidence}

            If a CONTRADICTION RESOLUTION block is present, report each gene with its STATUS
            (CONSISTENT / CONFLICTING / CONTEXT-DEPENDENT / CURATED-LITERATURE CONFLICT /
            INSUFFICIENT) and state the reason given for any disagreement -- e.g. that the
            studies used different populations, doses or endpoints, or that the only refuting
            evidence is mechanistic. Do not present a CONFLICTING association as established.

            If an EVIDENCE LEDGER is present, report EVERY gene in it -- do not drop the
            low-confidence ones, they are the point. For each, give its confidence label and
            cite the reference shown (e.g. PMID:12345/PMC678#p12 or ClinPGx:GENE/variant:L1A).
            Where the ledger marks a pair DISPUTED, say so explicitly and state what disagrees
            with what. Then give (1) the likely biological mechanism and (2) the implications
            for drug discovery and patient safety. Be specific; never assert a link the ledger
            marks unsupported without saying it is unsupported.
            {format_instructions}""",
            input_variables=["question", "reasoning", "evidence"],
            partial_variables={"format_instructions": adr_answer_parser.get_format_instructions()}
        ) | self.llm | adr_answer_parser

        # Search-topic generation for the open-search phases (6/7). Mirrors the paper's
        # own `search_list()` chain in Simple_AMG_RAG.py (which AMG-with-KG.py had dropped),
        # but additionally conditions on the evidence/graph retrieved so far -- so the model
        # chooses what to look up in the literature knowing what the KG already contains,
        # instead of being restricted to the PMIDs ClinPGx happens to cite.
        phrase_schemas = [
            ResponseSchema(
                name="search_phrases",
                description=("A list of at most three short search-friendly biomedical phrases "
                             "optimized for PubMed search (2-6 words each, no full sentences, "
                             "no punctuation, no boolean operators)."),
                type="array"
            )
        ]
        phrase_parser = StructuredOutputParser.from_response_schemas(phrase_schemas)

        self.search_phrase_chain = PromptTemplate(
            template="""You are choosing what to look up in the biomedical literature.

            Question: {question}

            Evidence and knowledge-graph content retrieved so far:
            {context}

            Propose at most three SHORT search phrases (2-6 words each) optimized for PubMed.
            Use the genes, variants, drugs and adverse effects that matter for this question --
            including promising leads in the retrieved evidence that are NOT yet confirmed.
            Do not copy the question. Do not write sentences. Do not use AND/OR.
            Good examples: "cisplatin ototoxicity pharmacogenomics", "ACYP2 hearing loss",
            "anthracycline cardiotoxicity SLC28A3".
            {format_instructions}""",
            input_variables=["question", "context"],
            partial_variables={"format_instructions": phrase_parser.get_format_instructions()}
        ) | self.llm | phrase_parser

        # Combined-topic query generation (phases 8/9). The model sees the knowledge-graph
        # EDGES (entity -[relation]-> entity), not just entity names, and groups terms that are
        # related there into single conjunctive PubMed queries. It also decides the arity --
        # how many terms belong in one query -- which we log as the "search shape".
        combo_schemas = [
            ResponseSchema(
                name="combined_queries",
                description=("List of search groups. Each group is ONE string of 2 to 4 related "
                             "terms joined by ' + ', e.g. 'cisplatin + ACYP2 + hearing loss'. "
                             "Group terms that are RELATED in the knowledge graph."),
                type="array"
            )
        ]
        combo_parser = StructuredOutputParser.from_response_schemas(combo_schemas)

        self.combo_query_chain = PromptTemplate(
            template="""You are searching the biomedical literature for evidence about
            RELATIONSHIPS, not single topics.

            Question: {question}

            Knowledge-graph relations found so far (entity -[relation]-> entity):
            {relations}

            Evidence retrieved so far:
            {context}

            Build up to {max_queries} search groups. Each group combines terms that are RELATED
            to each other (a drug with the gene that modulates it, a gene with the adverse
            effect it predisposes to, a drug with its toxicity) so the search finds papers about
            the LINK between them.

            Rules:
            - each group is a single string of 2 to {max_terms} terms joined by ' + '
            - use short specific terms: gene symbols, variant ids, drug names, adverse effects
            - combine terms that co-occur in the relations or evidence above
            - vary the size: some groups of 2 terms, some of 3, when the evidence supports it
            - no sentences, no AND/OR, no punctuation other than the ' + ' separators
            Example: ["cisplatin + ACYP2", "cisplatin + hearing loss + pharmacogenomics",
                      "GSTM1 + ototoxicity + children"]
            {format_instructions}""",
            input_variables=["question", "relations", "context", "max_queries", "max_terms"],
            partial_variables={"format_instructions": combo_parser.get_format_instructions()}
        ) | self.llm | combo_parser

        # Free-form query authoring (phase 10). Unlike phases 6-9 the model is NOT told how
        # many items to use and the code does NOT assemble the query string: the model decides
        # whether to look up ONE item or combine several, and writes the PubMed query itself
        # (quoted phrases, AND/OR, field tags such as [tiab] are all permitted). It also
        # reports how many distinct items it combined, which is what the arity report uses.
        free_schemas = [
            ResponseSchema(
                name="queries",
                description=("List of PubMed query objects. Each object has: 'query' (the exact "
                             "query string to send to PubMed) and 'items' (a list of the distinct "
                             "concepts that query combines -- one entry if it searches a single "
                             "concept, several if it combines them)."),
                type="array"
            )
        ]
        free_parser = StructuredOutputParser.from_response_schemas(free_schemas)

        self.free_query_chain = PromptTemplate(
            template="""You are the search strategist for a pharmacogenomics question. You have
            full control of the PubMed queries.

            Question: {question}

            Knowledge-graph relations found so far (entity -[relation]-> entity):
            {relations}

            Evidence retrieved so far:
            {context}

            Write up to {max_queries} PubMed queries. YOU decide, for each one:
            - whether to search a SINGLE concept (e.g. a gene or an adverse effect on its own,
              to survey a topic broadly) or to COMBINE two, three, or more concepts (to find
              papers about the link between them). Use whatever number fits the goal.
            - the exact wording: you may use quoted phrases, AND / OR, and PubMed field tags
              such as [tiab] or [mh]. Write the query exactly as it should be sent.

            Mix broad single-concept queries with narrow combined ones where that helps.
            Return for each query the query string and the list of concepts it covers.
            Examples:
              {{"query": "ACYP2 ototoxicity", "items": ["ACYP2", "ototoxicity"]}}
              {{"query": "\"cisplatin ototoxicity\"[tiab]", "items": ["cisplatin ototoxicity"]}}
              {{"query": "(GSTM1 OR GSTT1) AND cisplatin AND hearing loss",
                "items": ["GSTM1/GSTT1", "cisplatin", "hearing loss"]}}
            {format_instructions}""",
            input_variables=["question", "relations", "context", "max_queries"],
            partial_variables={"format_instructions": free_parser.get_format_instructions()}
        ) | self.llm | free_parser

        # Per-paper reading. The model is shown NUMBERED paragraphs of one article and must
        # say which of them bear on the question, plus what they establish. This is the "map"
        # half of the digest stage; the answer chain later reduces over the digests.
        digest_schemas = [
            ResponseSchema(
                name="relevant_paragraphs",
                description=("Numbers of the paragraphs that help answer the question, most "
                             "important first. Empty list if none of them do."),
                type="array"
            ),
            ResponseSchema(
                name="summary",
                description=("2-3 sentences stating what those paragraphs establish about the "
                             "question (genes, variants, drug, effect, direction, population). "
                             "Empty string if nothing here is relevant."),
                type="string"
            ),
            ResponseSchema(
                name="study_type",
                description=("What kind of study this text reports, exactly one of: "
                             "meta_analysis, systematic_review, gwas, human_cohort, "
                             "clinical_trial, case_report, animal, in_vitro, review, unknown."),
                type="string"
            ),
            ResponseSchema(
                name="genes_supported",
                description=("Gene symbols this text reports as ASSOCIATED with the drug effect "
                             "in question (e.g. [\"GSTM1\", \"ACYP2\"]). Empty list if none."),
                type="array"
            ),
            ResponseSchema(
                name="genes_refuted",
                description=("Gene symbols this text reports as NOT associated, not replicated, "
                             "or disputed for this drug effect. Empty list if none."),
                type="array"
            ),
            ResponseSchema(
                name="population",
                description=("Who was studied: 'children', 'adults', 'mixed', a specific "
                             "ancestry, or 'unknown'. Use 'unknown' for cell or animal work."),
                type="string"
            ),
            ResponseSchema(
                name="cancer_type",
                description=("The disease or cancer type studied (e.g. 'neuroblastoma', "
                             "'osteosarcoma', 'testicular cancer'), or 'unknown'."),
                type="string"
            ),
            ResponseSchema(
                name="endpoint",
                description=("The outcome measured (e.g. 'hearing threshold shift', "
                             "'clinically significant hearing loss', 'ejection fraction "
                             "decline'), or 'unknown'."),
                type="string"
            ),
            ResponseSchema(
                name="dose_context",
                description="Dose or regimen if stated (e.g. 'high-dose', 'standard-dose'), else 'unknown'.",
                type="string"
            ),
            ResponseSchema(
                name="direction",
                description=("Direction of the reported effect for the supported genes: "
                             "'increases', 'decreases', 'no_effect', or 'unknown'."),
                type="string"
            )
        ]
        digest_parser = StructuredOutputParser.from_response_schemas(digest_schemas)

        self.paper_digest_chain = PromptTemplate(
            template="""You are reading one section of a scientific paper to answer a question.

            Question: {question}

            Paper: {title}

            Numbered paragraphs:
            {paragraphs}

            Select ONLY the paragraph numbers that bear on the question, and summarise what they
            establish. Ignore methods boilerplate, funding, and unrelated background. If none of
            these paragraphs are relevant, return an empty list and an empty summary.

            Also report what KIND of study this is, and split the genes it mentions into those it
            SUPPORTS as associated and those it REFUTES (reports as null, not replicated, or
            disputed). A gene named only as background belongs in neither list.

            Then record the STUDY CONTEXT, which is what lets two disagreeing papers be
            reconciled: who was studied (population), the disease or cancer type, the outcome
            measured (endpoint), the dose or regimen, and the direction of the effect. Use
            'unknown' for anything the text does not state -- do not guess.
            {format_instructions}""",
            input_variables=["question", "title", "paragraphs"],
            partial_variables={"format_instructions": digest_parser.get_format_instructions()}
        ) | self.llm | digest_parser

    def build_knowledge_graph(self, question: str, options: Dict[str, str]) -> None:
        """Build a dynamic knowledge graph for the question with enhanced entity extraction"""
        
        # Prepare context for entity extraction
        options_text = "\n".join([f"{k}: {v}" for k, v in options.items()])
        full_text = question + " " + " ".join(options.values())
        
        # Search for additional context (skipped in offline mode)
        search_query = question + " " + " ".join(list(options.values())[:3])
        search_results = self._evidence_search(search_query, max_results=3,
                                               stage="question_context")
        context = "\n".join(search_results) if search_results else ""
        
        # Extract medical entities with relevance scoring
        try:
            entities_result = self.entity_extractor.invoke({
                "question": question,
                "options": options_text,
                "context": context
            })
            entities = entities_result.get("entities", [])
            scores = entities_result.get("scores", [])
            descriptions = entities_result.get("descriptions", [])
        except Exception as e:
            print(f"Entity extraction error: {e}")
            if options:
                entities = list(options.values())[:3]  # Fallback to options
            else:
                # Open-ended (no options): fall back to salient words from the question
                entities = [w.strip(".,!?;:") for w in question.split() if len(w) > 4][:5]
            scores = [5] * len(entities)  # Default moderate relevance
            descriptions = [f"Medical concept: {entity}" for entity in entities]

        # Normalize entity format. Some models (e.g. llama3.1) return a single list of
        # dicts {"name","score","description"} instead of three parallel arrays; others
        # return plain strings. Coerce everything to parallel lists of (name:str, score:num, desc:str).
        norm_entities, norm_scores, norm_descriptions = [], [], []
        for i, ent in enumerate(entities):
            if isinstance(ent, dict):
                name = ent.get("name") or ent.get("entity") or ent.get("text") or ""
                score = ent.get("score", ent.get("relevance", ent.get("relevance_score", 5)))
                desc = ent.get("description", ent.get("desc", ""))
            else:
                name = ent
                score = scores[i] if i < len(scores) else 5
                desc = descriptions[i] if i < len(descriptions) else ""
            name = str(name).strip()
            if not name:
                continue
            try:
                score = float(score)
            except (TypeError, ValueError):
                score = 5.0
            norm_entities.append(name)
            norm_scores.append(score)
            norm_descriptions.append(str(desc))
        entities, scores, descriptions = norm_entities, norm_scores, norm_descriptions

        print(f"Extracted entities: {entities}")
        print(f"Relevance scores: {scores}")
        
        # Add entities to graph with relevance-based confidence
        for i, entity in enumerate(entities[:8]):  # Limit to 8 entities
            # External enrichment -- ClinPGx table rows (pharmgkb modes) and/or PubMed
            # abstracts; nothing in pure offline mode.
            ev_items = self._evidence_search_detailed(entity, max_results=2,
                                                      stage=f"entity:{entity}")
            abstracts = [d["text"] for d in ev_items]
            wiki_content = ""
            if self.use_external_sources and not self._pgx_enabled():
                try:
                    wiki_results = wikipedia.search(entity, results=1)
                    if wiki_results:
                        wiki_content = wikipedia.summary(wiki_results[0], sentences=3)
                        self._log_evidence(f"entity:{entity}", entity, [{
                            "source": "Wikipedia",
                            "ref": f"Wikipedia:{wiki_results[0]}",
                            "title": wiki_results[0],
                            "text": wiki_content,
                        }])
                except:
                    pass

            # Combine sources with LLM-generated description
            llm_description = descriptions[i] if i < len(descriptions) else f"Medical entity: {entity}"
            external_description = " ".join(abstracts) if abstracts else wiki_content
            combined_description = f"{llm_description}. {external_description}" if external_description else llm_description

            # Calculate confidence based on relevance score and external sources
            relevance_score = scores[i] if i < len(scores) else 5
            confidence = min(1.0, (relevance_score / 10.0) + (0.2 if abstracts else 0.1))

            # Provenance: name the actual sources that contributed, not a guess.
            entity_sources = sorted({d["source"] for d in ev_items})
            if wiki_content:
                entity_sources.append("Wikipedia")

            # Add entity to graph
            med_entity = MedicalEntity(
                name=entity,
                description=combined_description[:500],  # Limit description length
                entity_type="medical_concept",
                confidence=confidence,
                sources=entity_sources or ["LLM"]
            )
            self.kg.add_entity(med_entity)

        # Capture the LLM-extracted entities BEFORE seeding. The pairwise LLM relation pass
        # below runs only over THESE -- the seeded ClinPGx entities already carry curated
        # edges, so feeding them into the O(n^2) relation loop would explode the LLM-call
        # count (e.g. ~30 entities -> ~430 calls/question) for no benefit.
        entity_list = list(self.kg.entities.keys())

        # ClinPGx grounding (pharmgkb mode): seed the REAL gene/variant-drug-phenotype edges
        # (with evidence levels) into the graph, so path reasoning traverses curated facts
        # instead of only the LLM's guessed relations.
        self._seed_pgx_edges(question, options)

        # Extract relationships between the LLM-extracted entities (seeded ones excluded).
        for i, entity1 in enumerate(entity_list):
            for entity2 in entity_list[i+1:]:
                try:
                    # Get descriptions
                    desc1 = self.kg.entities[entity1].description
                    desc2 = self.kg.entities[entity2].description
                    
                    # Enhanced context for relationship analysis
                    relationship_context = f"{question}\n\nOptions: {options_text}\n\nSearch Results: {context}"
                    
                    # Extract relationships with bidirectional analysis
                    relation_result = self.relation_extractor.invoke({
                        "entity1": entity1,
                        "desc1": desc1,
                        "entity2": entity2,
                        "desc2": desc2,
                        "context": relationship_context
                    })
                    
                    # Process relationships from the structured JSON response
                    relationships = relation_result.get("relationships", [])
                    
                    # Process each relationship in the list
                    for rel in relationships:
                        if isinstance(rel, dict):
                            rel_type = rel.get("relationship_type", "related_to")
                            try:
                                confidence = float(rel.get("confidence_score", 5)) / 10.0
                            except (TypeError, ValueError):
                                confidence = 0.5
                            evidence = rel.get("evidence", "")
                            entity_a = rel.get("entityA", "") or entity1
                            entity_b = rel.get("entityB", "") or entity2

                            # Create the relationship
                            relation = MedicalRelation(
                                source=entity_a,
                                target=entity_b,
                                relation_type=rel_type,
                                confidence=confidence,
                                evidence=evidence,
                                sources=["LLM Analysis"]
                            )
                            self.kg.add_relation(relation)
                    
                except Exception as e:
                    print(f"Relation extraction error for {entity1}-{entity2}: {e}")
        
        # Generate entity summaries for better context
        self._generate_entity_summaries(question, context)
                    
    def _generate_entity_summaries(self, question: str, context: str) -> None:
        """Generate enhanced summaries for entities in the knowledge graph"""
        if not self.kg.entities:
            return
            
        try:
            entities_list = list(self.kg.entities.keys())
            summary_result = self.summary_chain.invoke({
                "entities": entities_list,
                "context": f"Question: {question}\n\nContext: {context}"
            })
            
            summaries = summary_result.get("summaries", [])
            scores = summary_result.get("scores", [])
            
            # Update entity descriptions with enhanced summaries
            for i, entity_name in enumerate(entities_list):
                if i < len(summaries):
                    # Combine original description with enhanced summary
                    original_desc = self.kg.entities[entity_name].description
                    enhanced_summary = summaries[i]
                    # Models sometimes return summaries as dicts {"summary","score"}.
                    if isinstance(enhanced_summary, dict):
                        relevance_score = enhanced_summary.get("score", enhanced_summary.get("relevance", 5))
                        enhanced_summary = (enhanced_summary.get("summary")
                                            or enhanced_summary.get("text") or "")
                    else:
                        relevance_score = scores[i] if i < len(scores) else 5
                    try:
                        relevance_score = float(relevance_score)
                    except (TypeError, ValueError):
                        relevance_score = 5.0

                    # Update description with enhanced summary
                    updated_description = f"{original_desc}\n\nEnhanced Summary: {enhanced_summary}"

                    # Update confidence based on summary relevance
                    current_confidence = self.kg.entities[entity_name].confidence
                    summary_confidence = min(1.0, relevance_score / 10.0)
                    updated_confidence = min(1.0, (current_confidence + summary_confidence) / 2)
                    
                    # Update the entity
                    self.kg.entities[entity_name].description = updated_description[:500]
                    self.kg.entities[entity_name].confidence = updated_confidence
                    
        except Exception as e:
            print(f"Entity summarization error: {e}")
                    
    def reason_with_graph(self, question: str, options: Dict[str, str]) -> Dict[str, Any]:
        """Perform reasoning using the knowledge graph"""
        
        # Explore graph paths for each entity
        graph_context = []
        for entity in list(self.kg.entities.keys())[:3]:
            # Get connected nodes
            connections = self.kg.get_connected_nodes(entity, confidence_threshold=0.3)
            
            # Explore paths
            paths = self.kg.explore_path(entity, max_depth=2, confidence_threshold=0.3)
            
            context = f"Entity: {entity}\n"
            context += f"Description: {self.kg.entities[entity].description[:200]}\n"
            
            if connections:
                context += "Direct connections:\n"
                for conn in connections[:3]:
                    context += f"  - {conn['relation']} -> {conn['node']} (confidence: {conn['confidence']:.2f})\n"
            
            if paths:
                context += "Reasoning paths:\n"
                for path_data in paths[:2]:
                    path_str = " -> ".join([f"{p[0]} [{p[2]}]" for p in path_data['path']])
                    if path_str:
                        context += f"  - {path_str} -> {path_data['final_node']} (confidence: {path_data['confidence']:.2f})\n"
            
            graph_context.append(context)
        
        # Search for additional evidence
        search_query = question + " " + " ".join(list(self.kg.entities.keys())[:3])
        search_results = self._evidence_search(search_query, max_results=2, stage="reasoning")
        search_context = "\n".join(search_results) if search_results else (
            "No additional search results found." if self._has_external_evidence()
            else "No external sources used (offline mode).")

        # Generate chain of thought reasoning
        try:
            cot_result = self.cot_chain.invoke({
                "question": question,
                "graph_context": "\n\n".join(graph_context),
                "search_context": search_context
            })
            reasoning = cot_result.get("reasoning", "Unable to generate reasoning")
        except Exception as e:
            print(f"CoT generation error: {e}")
            reasoning = "Error in reasoning generation"
        
        # Generate final answer
        options_str = "\n".join([f"{k}: {v}" for k, v in options.items()])
        evidence = "\n".join(graph_context[:2])
        
        try:
            answer_result = self.answer_chain.invoke({
                "question": question,
                "options": options_str,
                "reasoning": reasoning,
                "evidence": evidence
            })

            # The parser can return confidence as a string; coerce so downstream :.2f works.
            try:
                _conf = float(answer_result.get("confidence", 0.0))
            except (TypeError, ValueError):
                _conf = 0.0

            return {
                "answer": answer_result.get("answer", "Unable to determine"),
                "confidence": _conf,
                "explanation": answer_result.get("explanation", ""),
                "reasoning": reasoning,
                "graph_context": graph_context,
                "search_context": search_context
            }
        except Exception as e:
            print(f"Answer generation error: {e}")
            return {
                "answer": "Error",
                "confidence": 0.0,
                "explanation": str(e),
                "reasoning": reasoning,
                "graph_context": graph_context,
                "search_context": search_context
            }

    def _papers_for_digest(self) -> List[dict]:
        """Distinct papers retrieved for this question, reasoning-stage ones first."""
        order = {"reasoning": 0, "question_context": 1}
        best: Dict[str, dict] = {}
        for e in self.evidence_log:
            if e.get("source") != "PubMed":
                continue
            pmid = (e.get("ref") or "").replace("PMID:", "").split("/")[0]
            if not pmid:
                continue
            rank = order.get(e.get("stage", ""), 2)
            if pmid not in best or rank < best[pmid]["_rank"]:
                best[pmid] = {"pmid": pmid, "title": e.get("title", ""), "ref": e.get("ref"),
                              "via": e.get("via", ""), "_rank": rank}
        return sorted(best.values(), key=lambda d: d["_rank"])[:self.digest_max_papers]

    def _digest_one_paper(self, question: str, paper: dict) -> Optional[dict]:
        """Read one paper and return the paragraphs that matter, with citable indices.

        Full text is read in batches so long articles are covered without blowing the serving
        model's context window; abstract-only papers are digested as a single batch."""
        pmid = paper["pmid"]
        ft = self.pubmed.fetch_fulltext(pmid, max_chars=10 ** 7)   # no truncation here
        if ft and ft.get("paragraphs"):
            paras, source, ref = ft["paragraphs"], ft["via"], f"PMID:{pmid}/{ft['pmcid']}"
        else:
            art = (self.pubmed.fetch_by_pmids([pmid]) or [{}])[0]
            abstract = art.get("abstract") or ""
            if not abstract:
                return None
            paras, source, ref = ([{"text": abstract, "section": "Abstract"}],
                                  "abstract", f"PMID:{pmid}")

        # Batch the paragraphs so each prompt stays small.
        batches, cur, cur_len = [], [], 0
        for i, para in enumerate(paras):
            if cur and cur_len + len(para["text"]) > self.digest_batch_chars:
                batches.append(cur); cur, cur_len = [], 0
            cur.append((i, para)); cur_len += len(para["text"])
        if cur:
            batches.append(cur)

        # A long article cannot be sent to the model in full, so the batches are ranked and the
        # most promising ones read first. Ranking by question-keyword density (the first
        # attempt) reliably picked the INTRODUCTION -- that is exactly where a paper repeats
        # its topic words -- so scoring is by FINDING signals instead: variant ids, effect
        # statistics, association language, and the section the paragraph sits in.
        q_terms = {t for t in re.findall(r"[a-z0-9\-]{4,}", question.lower())}
        if self._pgx_enabled():
            ents = self.pgx.extract_entities(question)
            q_terms |= {t.lower() for k in ("drugs", "phenotypes", "genes") for t in ents.get(k, [])}

        def _para_score(text: str, section: str) -> float:
            low, s = text.lower(), 0.0
            # concrete findings
            s += 3.0 * len(re.findall(r"\brs\d{3,}", low))              # variant ids
            s += 2.0 * len(re.findall(r"\b[A-Z][A-Z0-9]{2,}\*?\d*\b", text))  # gene symbols
            s += 3.0 * len(re.findall(r"\b(?:95%\s*ci|odds ratio|\bor\s*=|hazard ratio|"
                                      r"\bhr\s*=|p\s*[<=]\s*0?\.\d+|p-value)", low))
            s += 1.5 * sum(low.count(w) for w in
                           ("associated", "association", "genotype", "carriers", "allele",
                            "polymorphism", "significant", "risk of", "susceptibility"))
            s += 1.0 * sum(low.count(t) for t in q_terms)               # still topic-aware
            # section prior: findings live in results/discussion, not the introduction
            sec = (section or "").lower()
            if any(k in sec for k in ("result", "discussion", "conclusion", "finding")):
                s += 8.0
            elif "abstract" in sec:
                s += 4.0
            elif any(k in sec for k in ("introduction", "background")):
                s -= 6.0
            elif any(k in sec for k in ("method", "material", "statistical analysis",
                                        "study design", "patients and")):
                s -= 4.0
            # background phrasing, wherever it appears
            if any(p in low for p in ("is a widely used", "is a highly effective",
                                      "remains incompletely understood", "remains unclear",
                                      "has been widely", "is commonly used")):
                s -= 5.0
            return s

        def score(batch):
            return sum(_para_score(p["text"], p.get("section", "")) for _, p in batch)

        ranked = sorted(batches, key=score, reverse=True)
        covered = min(len(batches), self.digest_max_batches)
        if len(batches) > covered:
            top_secs = [p.get("section", "?") for _, p in ranked[0]][:2]
            print(f"[digest] {ref}: reading the {covered} most finding-dense of {len(batches)} "
                  f"batches ({len(paras)} paragraphs; top batch from {top_secs}) "
                  f"-- capped by AMG_DIGEST_MAX_BATCHES")

        picked, notes = [], []
        study_types, sup_genes, ref_genes = [], [], []
        ctx_fields: Dict[str, str] = {}      # population / cancer_type / endpoint / dose / direction
        for batch in ranked[:covered]:
            numbered = "\n".join(f"[{i}] {p['text']}" for i, p in batch)
            try:
                res = self.paper_digest_chain.invoke({
                    "question": question[:800], "title": paper.get("title", "")[:200],
                    "paragraphs": numbered})
            except Exception as e:
                print(f"[digest] {ref} batch failed: {e}")
                continue
            idxs = res.get("relevant_paragraphs") or []
            summary = (res.get("summary") or "").strip()
            valid = {i for i, _ in batch}
            for x in idxs:
                try:
                    xi = int(str(x).strip().strip("[]"))
                except (TypeError, ValueError):
                    continue
                if xi in valid and xi not in [p["idx"] for p in picked]:
                    para = dict(batch)[xi]
                    picked.append({"idx": xi, "text": para["text"],
                                   "section": para.get("section", "")})
            if summary and summary.lower() not in ("none", "n/a"):
                notes.append(summary)
            for fld in ("population", "cancer_type", "endpoint", "dose_context", "direction"):
                v = str(res.get(fld) or "").strip().lower()
                if v and v not in ("unknown", "n/a", "none", "") and fld not in ctx_fields:
                    ctx_fields[fld] = v[:60]
            st = str(res.get("study_type") or "").strip().lower().replace(" ", "_")
            if st and st != "unknown":
                study_types.append(st)
            for key, bucket in (("genes_supported", sup_genes), ("genes_refuted", ref_genes)):
                for g in (res.get(key) or []):
                    g = re.sub(r"[^A-Za-z0-9\-]", "", str(g)).upper()
                    if 2 < len(g) <= 12 and g not in bucket:
                        bucket.append(g)

        if not picked and not notes:
            return None
        return {
            "ref": ref, "pmid": pmid, "title": paper.get("title", ""),
            "source": source, "via": paper.get("via", ""),
            "n_paragraphs": len(paras), "batches_read": covered, "batches_total": len(batches),
            # Strongest study type seen wins: a meta-analysis section outranks a review section.
            "study_type": (sorted(study_types,
                                  key=lambda t: STUDY_RANK.get(t, 0), reverse=True) or ["unknown"])[0],
            "genes_supported": sup_genes[:8],
            "genes_refuted": ref_genes[:8],
            # Study context, used by the contradiction layer to tell a real disagreement from
            # two studies that simply examined different populations, doses or endpoints.
            "population": ctx_fields.get("population", ""),
            "cancer_type": ctx_fields.get("cancer_type", ""),
            "endpoint": ctx_fields.get("endpoint", ""),
            "dose_context": ctx_fields.get("dose_context", ""),
            "direction": ctx_fields.get("direction", ""),
            "paragraphs": [{"ref": f"{ref}#p{p['idx']}", "idx": p["idx"],
                            "section": p.get("section", ""),
                            "text": p["text"][:800]} for p in picked[:4]],
            "summary": " ".join(notes)[:900],
        }

    def _digest_papers(self, question: str) -> str:
        """Read every candidate paper, keep the query-relevant parts, and return the block of
        digests that the final answer reasons over. Fills self.paper_digests."""
        self.paper_digests = []
        papers = self._papers_for_digest()
        if not papers:
            return ""
        print(f"[digest] reading {len(papers)} paper(s) for this question")
        for paper in papers:
            d = self._digest_one_paper(question, paper)
            if d:
                self.paper_digests.append(d)
                print(f"[digest] {d['ref']}: {len(d['paragraphs'])} relevant paragraph(s) "
                      f"of {d['n_paragraphs']} ({d['source']})")
        if not self.paper_digests:
            return ""
        blocks = []
        for d in self.paper_digests:
            lines = [f"[{d['ref']}] {d['title']}"]
            if d["summary"]:
                lines.append(f"  Finding: {d['summary']}")
            for p in d["paragraphs"][:3]:
                lines.append(f"  ({p['ref']}) {p['text'][:400]}")
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)

    def _build_gene_ledger(self, question: str) -> str:
        """Aggregate every claim into a per-gene ledger with contradictions and confidence.

        Claims come from two places: the curated ClinPGx rows retrieved for this question, and
        the genes each digested paper reported as supported or refuted. Scoring happens in
        evidence_ledger.py -- by formula, never by the model."""
        self.gene_ledger = []
        if not self.evidence_ledger_on or Claim is None:
            return ""
        claims: List[Claim] = []

        # (a) curated claims
        if self._pgx_enabled():
            drug_hint = ""
            ents = self.pgx.extract_entities(question)
            if ents.get("drugs"):
                drug_hint = ents["drugs"][0]
            for row in self.pgx.search_detailed(question, max_results=8):
                assoc = self.pgx.is_associated(row["gene"], row["drug"] or drug_hint)
                claims.append(Claim(
                    gene=row["gene"], drug=row["drug"] or drug_hint,
                    phenotype=(row.get("phenotypes") or [""])[0], variant=row.get("variant", ""),
                    stance="refutes" if assoc == "not associated" else "supports",
                    study_type="curated", ref=row["ref"], pmid="",
                    level=row.get("level", ""), source="ClinPGx", text=row.get("text", "")))

        # (b) literature claims, one per gene the paper supported or refuted
        drug = ""
        if self._pgx_enabled():
            ents = self.pgx.extract_entities(question)
            drug = (ents.get("drugs") or [""])[0]
        for d in self.paper_digests:
            para_ref = (d["paragraphs"][0]["ref"] if d.get("paragraphs") else d["ref"])
            for gene, stance in ([(g, "supports") for g in d.get("genes_supported", [])]
                                 + [(g, "refutes") for g in d.get("genes_refuted", [])]):
                c = Claim(
                    gene=gene, drug=drug, stance=stance,
                    study_type=d.get("study_type", "unknown"),
                    ref=para_ref, pmid=d.get("pmid", ""), source="PubMed",
                    direction=d.get("direction", ""),
                    text=(d.get("summary") or "")[:200])
                # context axes travel with the claim (Claim has no slots, so attach directly)
                for fld in ("population", "cancer_type", "endpoint", "dose_context"):
                    setattr(c, fld, d.get(fld, ""))
                claims.append(c)

        if not claims:
            return ""
        self.gene_ledger = build_ledger(claims, self.pgx if self._pgx_enabled() else None)
        self._claims_by_pair = {}
        for c in claims:
            key = (c.gene.strip().upper(), " ".join(str(c.drug or "").strip().lower().split()))
            sup, ref = self._claims_by_pair.setdefault(key, ([], []))
            (sup if c.stance == "supports" else ref).append(c)
        disputed = sum(1 for e in self.gene_ledger if e["disputed"])
        print(f"[ledger] {len(self.gene_ledger)} gene-drug pairs | disputed: {disputed} | "
              f"top: " + ", ".join(f"{e['gene']}={e['confidence']:.2f}"
                                   for e in self.gene_ledger[:4]))
        return ledger_to_prompt(self.gene_ledger)

    def reason_open_with_graph(self, question: str) -> Dict[str, Any]:
        """Open-ended reasoning: produce a free-text doctor reply (no A-E options).

        Mirrors reason_with_graph but calls the open_answer_chain and returns
        structured diagnosis/drugs/tests alongside the free-text answer.
        """
        # Explore graph paths for each entity (identical to reason_with_graph)
        graph_context = []
        for entity in list(self.kg.entities.keys())[:3]:
            connections = self.kg.get_connected_nodes(entity, confidence_threshold=0.3)
            paths = self.kg.explore_path(entity, max_depth=2, confidence_threshold=0.3)

            context = f"Entity: {entity}\n"
            context += f"Description: {self.kg.entities[entity].description[:200]}\n"

            if connections:
                context += "Direct connections:\n"
                for conn in connections[:3]:
                    context += f"  - {conn['relation']} -> {conn['node']} (confidence: {conn['confidence']:.2f})\n"

            if paths:
                context += "Reasoning paths:\n"
                for path_data in paths[:2]:
                    path_str = " -> ".join([f"{p[0]} [{p[2]}]" for p in path_data['path']])
                    if path_str:
                        context += f"  - {path_str} -> {path_data['final_node']} (confidence: {path_data['confidence']:.2f})\n"

            graph_context.append(context)

        # Search for additional evidence
        search_query = question + " " + " ".join(list(self.kg.entities.keys())[:3])
        search_results = self._evidence_search(search_query, max_results=2, stage="reasoning")
        search_context = "\n".join(search_results) if search_results else (
            "No additional search results found." if self._has_external_evidence()
            else "No external sources used (offline mode).")

        # ClinPGx false-premise gating: if the question asserts a gene-drug link the tables
        # have no association for, prepend a corrective NOTE so both the CoT and the answer
        # reason about the missing link instead of confabulating one.
        premise_note = self._pgx_premise_note(question)
        if premise_note:
            search_context = premise_note + "\n" + search_context

        # Paper-digest stage: read each retrieved paper, keep the paragraphs that bear on the
        # question, and reason over those instead of raw article text.
        digest_context = self._digest_papers(question) if self.paper_digest else ""
        ledger_context = self._build_gene_ledger(question)
        cards_context = ""
        self.contradiction_cards = []
        if self.contradiction_layer_on and self.gene_ledger:
            self.contradiction_cards = build_cards(
                self.gene_ledger, getattr(self, "_claims_by_pair", {}),
                self.pgx if self._pgx_enabled() else None)
            cards_context = cards_to_prompt(self.contradiction_cards)
            from collections import Counter as _C
            print("[contradictions] " + ", ".join(
                f"{k}={v}" for k, v in _C(c["status"] for c in self.contradiction_cards).items()))
        if digest_context:
            search_context = ("Findings extracted from the retrieved papers "
                              "(each cites its paragraph):\n" + digest_context
                              + "\n\nCurated ClinPGx evidence and other retrieval:\n"
                              + search_context)

        # Chain-of-thought reasoning
        try:
            cot_result = self.cot_chain.invoke({
                "question": question,
                "graph_context": "\n\n".join(graph_context),
                "search_context": search_context
            })
            reasoning = cot_result.get("reasoning", "Unable to generate reasoning")
        except Exception as e:
            print(f"CoT generation error: {e}")
            reasoning = "Error in reasoning generation"

        # Evidence for the final decision. Historically this was graph_context alone, so the
        # literature only reached the answer through the CoT summary. With the digest stage on,
        # the decision is made from the curated ClinPGx rows PLUS the per-paper digests (which
        # carry paragraph-level citations), with the graph context as supporting structure.
        if cards_context:
            evidence = ("CONTRADICTION RESOLUTION -- each gene-drug pair resolved to a status, with "
                        "the reason sources disagree:\n" + cards_context
                        + "\n\nFull evidence ledger:\n" + ledger_context
                        + "\n\nKnowledge-graph context:\n" + "\n".join(graph_context[:1]))
        elif ledger_context:
            evidence = ("EVIDENCE LEDGER -- every candidate gene, its confidence, and any "
                        "disagreement between sources:\n" + ledger_context
                        + "\n\nSupporting findings read from the papers:\n"
                        + (digest_context or "none")
                        + "\n\nKnowledge-graph context:\n" + "\n".join(graph_context[:1]))
        elif digest_context:
            pgx_lines = [it["text"] for it in
                         (self.pgx.search_detailed(question, max_results=4) if self._pgx_enabled() else [])]
            evidence = ("Curated ClinPGx knowledge-graph evidence:\n"
                        + ("\n".join(pgx_lines) or "none")
                        + "\n\nFindings read from the papers (cite these refs):\n"
                        + digest_context
                        + "\n\nKnowledge-graph context:\n" + "\n".join(graph_context[:1]))
        else:
            evidence = "\n".join(graph_context[:2])
        if premise_note:
            evidence = premise_note + "\n" + evidence

        # Pick the answer chain by style:
        #   "pgx"    -> terse factual pharmacogenomics statement (PharmGKB QA)
        #   "adr"    -> expert drug-safety / drug-discovery assessment of an adverse reaction
        #   default  -> empathetic doctor reply (GenMedGPT-5k)
        answer_chain = {
            "pgx": getattr(self, "open_pgx_answer_chain", None),
            "adr": getattr(self, "open_adr_answer_chain", None),
        }.get(self.answer_style) or self.open_answer_chain
        try:
            answer_result = answer_chain.invoke({
                "question": question,
                "reasoning": reasoning,
                "evidence": evidence
            })
            answer_text = answer_result.get("answer", "") or ""
            return {
                "answer": answer_text,
                "diagnosis": answer_result.get("diagnosis", "") or "",
                "drugs": answer_result.get("drugs", []) or [],
                "tests": answer_result.get("tests", []) or [],
                "risk_genes": answer_result.get("risk_genes", []) or [],
                "reasoning": reasoning,
                "graph_context": graph_context,
                "search_context": search_context
            }
        except Exception as e:
            # 8B models often wrap JSON in prose; try to salvage the free-text reply.
            print(f"Open answer generation error: {e}")
            salvaged = self._salvage_open_answer(reasoning, question)
            return {
                "answer": salvaged,
                "diagnosis": "",
                "drugs": [],
                "tests": [],
                "reasoning": reasoning,
                "graph_context": graph_context,
                "search_context": search_context,
                "error": str(e)
            }

    @staticmethod
    def _salvage_open_answer(reasoning: str, question: str) -> str:
        """Best-effort fallback answer when the structured parser fails."""
        if reasoning and "Error" not in reasoning:
            return reasoning
        return "Unable to generate a reliable answer for this question."

    def answer_open_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Open-ended pipeline for free-text datasets (e.g. GenMedGPT-5k)."""
        question = question_data["question"]

        print(f"\n{'='*50}")
        print(f"[open] Question: {question[:120]}")
        print(f"{'='*50}\n")

        # Fresh provenance log + search-topic cache for this question
        self.evidence_log = []
        self._phrase_cache = {}
        self.combo_stats = []
        self.paper_digests = []
        self.gene_ledger = []
        self.contradiction_cards = []
        self._current_question = question

        # Step 1: build KG from the question alone (no options)
        self.build_knowledge_graph(question, {})
        print(f"Graph has {len(self.kg.entities)} entities and {len(self.kg.relations)} relations")

        # Step 2: reason and produce a free-text answer
        result = self.reason_open_with_graph(question)

        # Metadata
        result["id"] = question_data.get("id")
        result["question"] = question
        result["reference"] = question_data.get("reference", "")
        result["graph_stats"] = {
            "num_entities": len(self.kg.entities),
            "num_relations": len(self.kg.relations)
        }
        # Provenance: full retrieval log + deduplicated citation list
        result["references"] = self.collect_references()
        result["evidence_log"] = list(self.evidence_log)
        # Search shape (phases 8/9): one record per issued combined query.
        result["search_shape"] = list(self.combo_stats)
        result["paper_digests"] = list(self.paper_digests)
        result["gene_ledger"] = list(self.gene_ledger)
        result["contradiction_cards"] = list(self.contradiction_cards)
        return result

    def answer_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main pipeline to answer a medical question"""
        
        question = question_data["question"]
        options = question_data.get("options", {})

        print(f"\n{'='*50}")
        print(f"Question: {question}")
        print(f"Options: {options}")
        print(f"{'='*50}\n")

        # Fresh provenance log + search-topic cache for this question
        self.evidence_log = []
        self._phrase_cache = {}
        self.combo_stats = []
        self.paper_digests = []
        self.gene_ledger = []
        self.contradiction_cards = []
        self._current_question = question

        # Step 1: Build knowledge graph
        print("Step 1: Building knowledge graph...")
        self.build_knowledge_graph(question, options)
        print(f"Graph has {len(self.kg.entities)} entities and {len(self.kg.relations)} relations")
        
        # Step 2: Reason with graph
        print("\nStep 2: Reasoning with graph...")
        result = self.reason_with_graph(question, options)
        
        # Add metadata
        result["question"] = question
        result["options"] = options
        result["expected_answer"] = question_data.get("answer", "Unknown")
        result["graph_stats"] = {
            "num_entities": len(self.kg.entities),
            "num_relations": len(self.kg.relations)
        }
        result["references"] = self.collect_references()
        result["evidence_log"] = list(self.evidence_log)
        result["search_shape"] = list(self.combo_stats)

        return result

def load_medqa_sample():
    """Load a sample from MEDQA dataset"""
    # Sample MEDQA question
    sample = {
        "question": "A 45-year-old man presents to the emergency department with severe chest pain that started 2 hours ago. The pain is substernal, crushing in nature, and radiates to his left arm. He has a history of hypertension and diabetes mellitus. His father died of a myocardial infarction at age 50. On examination, he is diaphoretic and in distress. His blood pressure is 150/90 mmHg, pulse is 110/min, and respirations are 22/min. An ECG shows ST-segment elevation in leads II, III, and aVF. Which of the following is the most likely diagnosis?",
        "options": {
            "A": "Unstable angina",
            "B": "Acute inferior wall myocardial infarction",
            "C": "Acute anterior wall myocardial infarction", 
            "D": "Aortic dissection",
            "E": "Pulmonary embolism"
        },
        "answer": "B",
        "answer_idx": 1,
        "meta_info": "This is a cardiology question testing knowledge of myocardial infarction presentation and ECG findings."
    }
    return sample

def main():
    """Main execution function"""
    
    print("AMG-RAG Medical QA System")
    print("="*50)
    
    # Initialize system
    print("Initializing AMG-RAG system...")
    
    # Set to True and provide key to use OpenAI, False for Ollama
    USE_OPENAI = True  # Set to False to use Ollama instead
    
    if USE_OPENAI:
        if OPENAI_API_KEY == "your-openai-api-key":
            print("Warning: Please set your OpenAI API key in the code")
            print("Falling back to Ollama (make sure Ollama is running)")
            USE_OPENAI = False
    
    system = AMG_RAG_System(use_openai=USE_OPENAI, openai_key=OPENAI_API_KEY if USE_OPENAI else None)
    
    # Load sample question
    print("\nLoading MEDQA sample question...")
    question_data = load_medqa_sample()
    
 
    
    result = system.answer_question(question_data)
    
  
    
    # Display results
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"Question: {result['question'][:100]}...")
    print(f"\nOptions:")
    for k, v in result['options'].items():
        print(f"  {k}: {v}")
    
    print(f"\nExpected Answer: {result['expected_answer']}")
    print(f"Model Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nExplanation: {result['explanation']}")
    
    print(f"\nGraph Statistics:")
    print(f"  - Entities: {result['graph_stats']['num_entities']}")
    print(f"  - Relations: {result['graph_stats']['num_relations']}")
    
    print(f"\nReasoning Chain:")
    print(result['reasoning'][:500] + "..." if len(result['reasoning']) > 500 else result['reasoning'])
    

    
    # Visualize graph structure (text-based)
    print("\n" + "="*50)
    print("KNOWLEDGE GRAPH STRUCTURE")
    print("="*50)
    
    for entity_name, entity in list(system.kg.entities.items())[:5]:
        print(f"\n📌 {entity_name}")
        print(f"   Type: {entity.entity_type}")
        print(f"   Description: {entity.description[:100]}...")
        
        connections = system.kg.get_connected_nodes(entity_name)
        if connections:
            print("   Connections:")
            for conn in connections[:3]:
                print(f"     → {conn['relation']} → {conn['node']} (conf: {conn['confidence']:.2f})")

if __name__ == "__main__":
    main()