# tools.py
import requests
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from crewai.tools import tool
import urllib.parse
from email.utils import parsedate_to_datetime
from datetime import datetime

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
