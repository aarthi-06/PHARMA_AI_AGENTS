# agents.py
from crewai import Agent
from crewai.llm import LLM
from tools import pubmed_search_pmids, pubmed_fetch_summaries, get_guideline_sources, news_rss_search

llm = LLM(
    model="gpt-4o-mini",
    provider="openai",
)

def web_intelligence_agent():
    """
    Web Intelligence Agent (MVP)

    Expected INPUT (passed via task description):
    {
      "context": {
        "intent": "repurposing_analysis",
        "molecule": { "primary": { "inn": "...", "synonyms": [...] } },
        "indication": { "name": "..." },
        "region": "India",
        "year_range": [2020, 2025],
        "recency": "last_24_months",
        "source_whitelist": ["GOLD","NICE","WHO","PubMed","ReputableNews"]
      }
    }

    Expected OUTPUT (must be valid JSON only):
    {
      "web": {
        "guidelines": [{...}],
        "publications": [{...}],
        "news": [{...}],
        "summary": "...",
        "confidence_level": "low|moderate|high"
      }
    }
    """

    return Agent(
        role="Web Intelligence Agent",
        goal=(
            "Collect and summarize high-quality web evidence (guidelines, publications, and reputable news) "
            "for the given molecule + indication + region and return a structured JSON response."
        ),
        backstory=(
            "You are a careful medical/web research analyst. You only use sources allowed in "
            "`source_whitelist`, prefer authoritative guidelines and indexed literature, and produce "
            "structured, citation-friendly outputs."
        ),
        # No tools yet (we'll attach in tools.py later)
        tools=[pubmed_search_pmids, pubmed_fetch_summaries, get_guideline_sources, news_rss_search],

        allow_delegation=False,
        verbose=True,
    )
