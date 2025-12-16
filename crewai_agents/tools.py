# tools.py
import requests
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from crewai.tools import tool
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime
import json
from functools import lru_cache
import os
import time
from typing import Any

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DB = "pubmed"


@tool("pubmed_search_pmids")
def pubmed_search_pmids(query: str, retmax: int = 10) -> List[str]:
    """
    Search PubMed and return a list of PMIDs for a given query.
    Example query: "roflumilast COPD 2023:2025[pdat]"
    """
    url = f"{EUTILS_BASE}/esearch.fcgi"
    params = {
        "db": DB,
        "term": query,
        "retmode": "xml",
        "retmax": str(retmax),
        "sort": "pub+date",
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    pmids = [id_node.text for id_node in root.findall(".//IdList/Id") if id_node.text]
    return pmids


@tool("pubmed_fetch_summaries")
def pubmed_fetch_summaries(pmids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch PubMed summaries (title, journal, pubdate) for a list of PMIDs.
    Returns a list of dicts suitable to map into your publications[] schema.
    """
    if not pmids:
        return []

    url = f"{EUTILS_BASE}/esummary.fcgi"
    params = {
        "db": DB,
        "id": ",".join(pmids),
        "retmode": "xml",
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    results: List[Dict[str, Any]] = []

    for docsum in root.findall(".//DocSum"):
        pmid = None
        title = None
        journal = None
        pubdate = None

        # DocSum has <Id>PMID</Id>
        id_node = docsum.find("Id")
        if id_node is not None:
            pmid = id_node.text

        # Items like <Item Name="Title">...</Item>
        for item in docsum.findall("Item"):
            name = item.attrib.get("Name")
            if name == "Title":
                title = item.text
            elif name == "FullJournalName":
                journal = item.text
            elif name == "PubDate":
                pubdate = item.text

        results.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "pubdate": pubdate,
            }
        )

    return results






@tool("news_rss_search")
def news_rss_search(query: str, max_items: int = 5) -> list[dict]:
    """
    Fetch recent news articles using Google News RSS (no API key).
    Returns [{headline, publisher, date, takeaway, url}]
    """
    rss_url = "https://news.google.com/rss/search"
    params = {
        "q": query,
        "hl": "en-IN",
        "gl": "IN",
        "ceid": "IN:en",
    }

    r = requests.get(rss_url, params=params, timeout=20)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    items = root.findall(".//item")

    results = []
    for item in items[:max_items]:
        title = item.findtext("title")
        link = item.findtext("link")
        pub_date = item.findtext("pubDate")
        source = item.find("source")

        results.append({
            "headline": title,
            "publisher": source.text if source is not None else "Google News",
            "date": pub_date[:16] if pub_date else None,
            "takeaway": title,  # MVP: reuse headline as takeaway
            "url": link,
        })

    return results


from crewai.tools import tool

@tool("get_guideline_sources")
def get_guideline_sources(indication: str) -> list[dict]:
    """
    Return curated, authoritative guideline sources.
    MVP:
    - Disease-specific guidelines when known
    - Generic authoritative sources as fallback
    """
    ind = (indication or "").strip().lower()

    # Disease-specific guidelines
    if ind in ["copd", "chronic obstructive pulmonary disease"]:
        return [
            {
                "source": "GOLD 2024 Pocket Guide",
                "publisher": "Global Initiative for Chronic Obstructive Lung Disease",
                "date": "2024-01-11",
                "recommendation": "Official guideline source (content extraction not implemented in MVP).",
                "url": "https://goldcopd.org/wp-content/uploads/2024/02/POCKET-GUIDE-GOLD-2024-ver-1.2-11Jan2024_WMV.pdf"
            },
            {
                "source": "NICE NG115",
                "publisher": "National Institute for Health and Care Excellence (NICE)",
                "date": "2018-12-05",
                "recommendation": "Official guideline source (content extraction not implemented in MVP).",
                "url": "https://www.nice.org.uk/guidance/ng115"
            }
        ]

    # Generic fallback (applies to ALL indications)
    return [
        {
            "source": "WHO Guidelines",
            "publisher": "World Health Organization",
            "date": None,
            "recommendation": "Generic authoritative health guideline source (disease-specific guideline not mapped in MVP).",
            "url": "https://www.who.int/publications/guidelines"
        },
        {
            "source": "NICE Guidelines",
            "publisher": "National Institute for Health and Care Excellence (NICE)",
            "date": None,
            "recommendation": "Generic authoritative guideline repository (disease-specific guidance not mapped in MVP).",
            "url": "https://www.nice.org.uk/guidance"
        }
    ]



DEFAULT_TIMEOUT = 20

# IMPORTANT: Wikimedia blocks requests without a real User-Agent
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "PHARMA_AI_AGENTS/0.1 (+https://github.com/yourname/PHARMA_AI_AGENTS; contact: youremail@example.com)",
}

WIKIDATA_HEADERS = {
    **DEFAULT_HEADERS,
    "Accept": "application/json",
}

# cooldown to avoid hammering Wikidata after a 403/429
_WIKIDATA_BLOCKED_UNTIL_TS = 0.0


# -----------------------
# HTTP helpers (robust)
# -----------------------
def _merge_headers(headers: dict | None) -> dict:
    """Merge default headers with optional per-call headers."""
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    return h


def _sleep_backoff(attempt: int) -> None:
    """Exponential backoff sleep to reduce retries hammering servers."""
    time.sleep(min(6.0, 0.8 * (2 ** attempt)))


def _http_get_json(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    """HTTP GET returning JSON with retries for transient/block statuses."""
    h = _merge_headers(headers)
    last_err: Exception | None = None

    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers=h, timeout=DEFAULT_TIMEOUT)

            if r.status_code in (403, 429, 500, 502, 503, 504):
                last_err = requests.HTTPError(f"{r.status_code} for {r.url}", response=r)
                if attempt < 3:
                    _sleep_backoff(attempt)
                    continue

            r.raise_for_status()
            return r.json()

        except Exception as e:
            last_err = e
            if attempt < 3:
                _sleep_backoff(attempt)
                continue
            raise last_err


def _http_post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    """HTTP POST returning JSON with retries for transient statuses."""
    h = _merge_headers(headers)
    last_err: Exception | None = None

    for attempt in range(4):
        try:
            r = requests.post(url, json=payload, headers=h, timeout=DEFAULT_TIMEOUT)

            if r.status_code in (429, 500, 502, 503, 504):
                last_err = requests.HTTPError(f"{r.status_code} for {r.url}", response=r)
                if attempt < 3:
                    _sleep_backoff(attempt)
                    continue

            r.raise_for_status()
            return r.json()

        except Exception as e:
            last_err = e
            if attempt < 3:
                _sleep_backoff(attempt)
                continue
            raise last_err


def _safe_json_load(s: str) -> dict:
    """Safely extract JSON from LLM output (handles ```json blocks)."""
    s = (s or "").strip()
    s = re.sub(r"^```json\s*", "", s)
    s = re.sub(r"^```\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    m = re.search(r"\{.*\}", s, re.DOTALL)
    return json.loads(m.group(0) if m else s)


# -----------------------
# Safe coercion
# fixes: 'dict' has no strip
# -----------------------
def _as_text(x: Any) -> str:
    """Coerce weird slot values (dict/list/etc.) into a usable string."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        for k in ("name", "inn", "value", "text", "label"):
            v = x.get(k)
            if isinstance(v, str) and v.strip():
                return v
        return json.dumps(x, ensure_ascii=False)
    if isinstance(x, list):
        parts = []
        for i in x:
            t = _as_text(i).strip()
            if t:
                parts.append(t)
            if len(parts) >= 10:
                break
        return " ".join(parts)
    return str(x)


# -----------------------
# Year range
# -----------------------
def _parse_year_range(text: str) -> dict:
    """Parse a year range from text. Returns {'year_range':[a,b]} or {'year_range':None}."""
    now = datetime.now().year

    m = re.search(r"(20\d{2})\s*[-–to]+\s*(20\d{2})", text or "", re.IGNORECASE)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return {"year_range": [min(a, b), max(a, b)]}

    m = re.search(r"last\s+(\d+)\s+years", text or "", re.IGNORECASE)
    if m:
        n = int(m.group(1))
        return {"year_range": [now - n, now]}

    return {"year_range": None}


@tool("parse_year_range")
def parse_year_range(text: str) -> dict:
    """
    Extract explicit year ranges from free text.

    Supports:
    - "2020-2025"
    - "2020 to 2025"
    - "last 3 years"

    Returns:
      {"year_range": [start_year, end_year]} or {"year_range": None}
    """
    return _parse_year_range(text)


# -----------------------
# NL -> slots (OpenAI)
# -----------------------
def _nl_to_slots(user_query: str) -> dict:
    """Internal: use OpenAI chat completions to extract slots from a user query."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("SLOTS_OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        # Never crash the crew; return empty-but-valid slots
        return {
            "intent": "repurposing_analysis",
            "drug": "",
            "indication": "",
            "region": "",
            "year_range": None,
            "constraints": {"need_fto": True, "need_supply_view": True, "mvp_mode": True},
        }

    yr_hint = _parse_year_range(user_query).get("year_range")

    system = "You are a strict information extractor. Return ONLY valid JSON. No markdown. No extra text."

    instruction = {
        "task": "Extract slots from the user's query for a pharma repurposing analysis request.",
        "output_schema": {
            "intent": "repurposing_analysis|other",
            "drug": "string",
            "indication": "string",
            "region": "string",
            "year_range": "null or [startYear,endYear]",
            "constraints": {
                "need_fto": "boolean",
                "need_supply_view": "boolean",
                "mvp_mode": "boolean",
            },
        },
        "rules": [
            "Infer intent=repurposing_analysis if query asks repurposing/repositioning options.",
            "If year range not specified, output null (do not guess).",
            "Set constraints booleans to true unless user disables them.",
            "If unknown, keep empty string but keep keys.",
        ],
    }

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **DEFAULT_HEADERS,
    }
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(
                    {"instruction": instruction, "user_query": user_query, "year_range_hint": yr_hint}
                ),
            },
        ],
    }

    data = _http_post_json(url, payload, headers=headers)
    content = data["choices"][0]["message"]["content"]

    try:
        slots = _safe_json_load(content)
    except Exception:
        # last-resort repair
        repair_payload = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Fix the following into valid JSON only. Output JSON only."},
                {"role": "user", "content": content},
            ],
        }
        repaired = _http_post_json(url, repair_payload, headers=headers)
        slots = _safe_json_load(repaired["choices"][0]["message"]["content"])

    # normalize + defaults
    if slots.get("year_range") in ("", [], {}):
        slots["year_range"] = None

    slots.setdefault("constraints", {})
    slots["constraints"].setdefault("need_fto", True)
    slots["constraints"].setdefault("need_supply_view", True)
    slots["constraints"].setdefault("mvp_mode", True)

    slots.setdefault("intent", "repurposing_analysis")
    slots.setdefault("drug", "")
    slots.setdefault("indication", "")
    slots.setdefault("region", "")
    return slots


@tool("nl_to_slots")
def nl_to_slots(user_query: str) -> dict:
    """
    Extract structured slots from a natural-language user query.

    Returns keys:
      - intent
      - drug
      - indication
      - region
      - year_range
      - constraints (need_fto, need_supply_view, mvp_mode)
    """
    return _nl_to_slots(user_query)


# -----------------------
# Wikidata helpers (safe + cooldown)
# -----------------------
@lru_cache(maxsize=512)
def _wikidata_search_qid(term: str) -> str | None:
    """Search Wikidata for a term and return the best QID, with cooldown safety."""
    global _WIKIDATA_BLOCKED_UNTIL_TS
    if time.time() < _WIKIDATA_BLOCKED_UNTIL_TS:
        return None

    term = (term or "").strip()
    if not term:
        return None

    try:
        data = _http_get_json(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": term,
                "language": "en",
                "format": "json",
                "limit": 1,
            },
            headers=WIKIDATA_HEADERS,
        )
        hits = data.get("search", [])
        return hits[0].get("id") if hits else None

    except requests.HTTPError as e:
        resp = getattr(e, "response", None)
        if resp is not None and resp.status_code in (403, 429):
            _WIKIDATA_BLOCKED_UNTIL_TS = time.time() + 600
        return None
    except Exception:
        return None


@lru_cache(maxsize=512)
def _wikidata_entity(qid: str) -> dict:
    """Fetch Wikidata entity JSON for a QID, with cooldown safety."""
    global _WIKIDATA_BLOCKED_UNTIL_TS
    if time.time() < _WIKIDATA_BLOCKED_UNTIL_TS:
        return {}

    qid = (qid or "").strip()
    if not qid:
        return {}

    try:
        return _http_get_json(
            f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
            headers=WIKIDATA_HEADERS,
        )
    except requests.HTTPError as e:
        resp = getattr(e, "response", None)
        if resp is not None and resp.status_code in (403, 429):
            _WIKIDATA_BLOCKED_UNTIL_TS = time.time() + 600
        return {}
    except Exception:
        return {}


def _wd_claim_first_string(entity: dict, prop: str) -> str | None:
    """Extract first claim value for a Wikidata property as a string (or id)."""
    try:
        claims = entity["entities"][next(iter(entity["entities"]))]["claims"]
        for c in claims.get(prop, []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(v, str):
                return v
            if isinstance(v, dict) and "id" in v:
                return v["id"]
    except Exception:
        return None
    return None

def _wikidata_aliases(entity: dict, lang: str = "en") -> list[str]:
    """Get up to ~25 aliases from Wikidata entity JSON."""
    try:
        ent = entity["entities"][next(iter(entity["entities"]))]
        aliases = ent.get("aliases", {}).get(lang, [])
        out = []
        for a in aliases:
            v = a.get("value")
            if v and isinstance(v, str):
                out.append(v)
        # de-dup, keep order
        seen = set()
        uniq = []
        for s in out:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        return uniq[:25]
    except Exception:
        return []


def _resolve_indication_codes(indication: str) -> dict:
    """Resolve disease name -> ICD10 (P494), MeSH (P486), SNOMED (P5806). Never throws."""
    indication = (indication or "").strip()
    if not indication:
        return {}

    qid = _wikidata_search_qid(indication)
    if not qid:
        return {}

    ent = _wikidata_entity(qid)
    if not ent:
        return {}

    out = {}
    icd10 = _wd_claim_first_string(ent, "P494")
    mesh = _wd_claim_first_string(ent, "P486")
    snomed = _wd_claim_first_string(ent, "P5806")
    if icd10:
        out["ICD10"] = icd10
    if mesh:
        out["MESH"] = mesh
    if snomed:
        out["SNOMED"] = snomed
    return out


def _resolve_drug_atc(drug: str) -> dict:
    """Resolve ATC code for a drug via Wikidata P267. Never throws."""
    drug = (drug or "").strip()
    if not drug:
        return {}

    qid = _wikidata_search_qid(drug)
    if not qid:
        return {}

    ent = _wikidata_entity(qid)
    if not ent:
        return {}

    atc = _wd_claim_first_string(ent, "P267")
    return {"ATC": atc} if atc else {}


# -----------------------
# Region normalization
# -----------------------
def _normalize_region(region: str) -> dict:
    """Normalize region/country string into canonical name + ISO codes (best effort)."""
    region = (region or "").strip()
    if not region:
        return {"name": None, "iso2": None, "iso3": None}
    try:
        import pycountry
        c = pycountry.countries.search_fuzzy(region)[0]
        return {"name": c.name, "iso2": getattr(c, "alpha_2", None), "iso3": getattr(c, "alpha_3", None)}
    except Exception:
        return {"name": region, "iso2": None, "iso3": None}


@tool("normalize_region")
def normalize_region(region_text: str) -> dict:
    """
    Normalize a region/country string.

    Returns:
      {"name": <canonical_name>, "iso2": <alpha_2|None>, "iso3": <alpha_3|None>}
    """
    return _normalize_region(region_text)


# -----------------------
# Policy defaults
# -----------------------
def _apply_policy_defaults(ctx: dict) -> dict:
    """Apply policy defaults (year_range, constraints, optional DEFAULT_REGION)."""
    now = datetime.now().year
    c = ctx.get("context", {})

    if not c.get("year_range"):
        c["year_range"] = [now - 5, now]

    default_region = os.getenv("DEFAULT_REGION", "")
    if not c.get("region") and default_region:
        c["region"] = default_region

    c.setdefault("constraints", {})
    c["constraints"].setdefault("need_fto", True)
    c["constraints"].setdefault("need_supply_view", True)
    c["constraints"].setdefault("mvp_mode", True)

    c.setdefault("dosage_form_hint", None)
    ctx["context"] = c
    return ctx


@tool("apply_policy_defaults")
def apply_policy_defaults(partial_context: dict) -> dict:
    """
    Apply policy-driven defaults to a partial context JSON.

    Defaults:
      - year_range => last 5 years
      - constraints flags => True
      - dosage_form_hint => None
      - region => DEFAULT_REGION env if missing
    """
    return _apply_policy_defaults(partial_context)


# -----------------------
# Schema validator
# -----------------------

@lru_cache(maxsize=1)
def _get_context_schema():
    path = os.getenv("CONTEXT_SCHEMA_PATH", "schemas/context.schema.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache(maxsize=1)
def _get_context_validator():
    """
    Build the validator once. Reusing it avoids repeated heavy work
    and reduces the chance of crashes in repeated retries.
    """
    from jsonschema import Draft202012Validator
    schema = _get_context_schema()
    return Draft202012Validator(schema)

@tool("validate_context_schema")
def validate_context_schema(context: dict) -> dict:
    """
    Validate the normalized context against schemas/context.schema.json.

    Input:
      context: dict (your normalized context JSON)

    Returns:
      {"ok": True, "errors": []} OR {"ok": False, "errors": [...]}
    """
    try:
        v = _get_context_validator()
        errors = sorted(v.iter_errors(context), key=lambda e: e.path)
        if not errors:
            return {"ok": True, "errors": []}

        out = []
        for e in errors[:10]:
            loc = ".".join([str(p) for p in e.path]) if e.path else "(root)"
            out.append(f"{loc}: {e.message}")
        return {"ok": False, "errors": out}
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}


# -----------------------
# Final assembly
# -----------------------
def _assemble_context(slots: dict) -> dict:
    """Assemble final normalized context JSON matching your schema. Never throws."""
    slots = slots or {}

    intent = _as_text(slots.get("intent")).strip() or "repurposing_analysis"
    drug = _as_text(slots.get("drug")).strip()
    indication = _as_text(slots.get("indication")).strip()
    region = _as_text(slots.get("region")).strip()

    reg = _normalize_region(region)
    region_name = reg.get("name") or region or ""

    drug_info = {"inn": drug, "synonyms": []}
    qid = _wikidata_search_qid(drug)
    if qid:
        ent = _wikidata_entity(qid)
        syns = _wikidata_aliases(ent)
        if syns:
            drug_info["synonyms"] = syns


    codes = _resolve_indication_codes(indication)
    atc = _resolve_drug_atc(drug)
    if atc:
        codes = dict(codes or {})
        codes.update(atc)

    comparators = slots.get("comparators")
    if not isinstance(comparators, list):
        comparators = []

    constraints = slots.get("constraints")
    if not isinstance(constraints, dict):
        constraints = {}

    ctx = {
        "context": {
            "intent": intent,
            "molecule": {"primary": drug_info, "comparators": comparators},
            "indication": {"name": indication, "codes": codes or {}},
            "region": region_name,
            "year_range": slots.get("year_range"),
            "dosage_form_hint": None,
            "constraints": constraints,
        }
    }

    return _apply_policy_defaults(ctx)


@tool("assemble_context")
def assemble_context(slots: dict) -> dict:
    """
    Assemble normalized context JSON from slots.

    Input:
      slots dict from nl_to_slots (or user provided)

    Output:
      {"context": {...}} matching your schema keys.
    """
    return _assemble_context(slots)


# -----------------------
# Optional: Pretty JSON for readability
# -----------------------
@tool("pretty_json")
def pretty_json(data: Any) -> str:
    """
    Pretty-print any python object as a readable JSON string.
    Useful for showing context output cleanly in logs/UI.
    """
    return json.dumps(data, indent=2, ensure_ascii=False)



