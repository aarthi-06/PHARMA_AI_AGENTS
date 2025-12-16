# agents.py
from crewai import Agent
from crewai.llm import LLM
from tools import pubmed_search_pmids, pubmed_fetch_summaries, get_guideline_sources, news_rss_search, nl_to_slots,assemble_context, validate_context_schema


llm = LLM(
    model="gpt-4o-mini",
    provider="openai",
)



def master_agent():
    """
    Master Agent = Normalizer only.
    Input: user one-liner string
    Output: normalized context JSON (validated)
    """
    return Agent(
        role="Master Agent (Normalizer)",
        goal=(
            "Transform user one-liner requests into a normalized context JSON that matches the schema, "
            "by calling tools for extraction, enrichment, and schema validation."
        ),
        backstory=(
            "You are a strict normalizer. You do not perform web research. "
            "You only produce schema-valid JSON for downstream agents."
        ),
        tools=[ assemble_context, validate_context_schema,nl_to_slots],
        allow_delegation=False,
        verbose=True,
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
