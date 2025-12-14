# tasks.py
import json
from crewai import Task

def web_intelligence_task(context: dict, agent):
    """
    Create the Web Intelligence task.
    """

    input_json = json.dumps(context, indent=2)

    return Task(
    description=(
        "You are the Web Intelligence Agent.\n\n"
        "INPUT JSON (use this as the only source of requirements):\n"
        f"{input_json}\n\n"

        "Your job:\n"
        "1) Use ONLY sources allowed in source_whitelist.\n"
        "2) Focus on the molecule + indication. Prefer authoritative/medical sources.\n"
        "3) Keep results within the requested recency/year_range.\n"
        "4) Produce an output that strictly matches the required JSON schema.\n\n"

        "TOOL USAGE (MANDATORY for publications):\n"
        "- You MUST use the PubMed tools to populate web.publications[].\n"
        "- Build a strict PubMed boolean query using Title/Abstract fields:\n"
        '  (<inn>[Title/Abstract] OR <synonym1>[Title/Abstract] OR <synonym2>[Title/Abstract]) '
        'AND (<indication>[Title/Abstract])\n'
        "- Apply year_range using [pdat] exactly like: 2020:2025[pdat]\n"
        "- Prefer clinically relevant results (COPD management, safety, efficacy, trials, reviews).\n"
        "- If many results are off-topic, refine the query by adding terms like:\n"
        "  (COPD OR 'chronic obstructive pulmonary disease')\n"
        "- Call tool pubmed_search_pmids(query, retmax=10) to get PMIDs.\n"
        "- Then call tool pubmed_fetch_summaries(pmids) to get title/journal/pubdate.\n"
        "- Populate web.publications[] ONLY from tool results. Do NOT invent PMIDs.\n\n"

        "KEY_FINDING RULE (IMPORTANT):\n"
        "- You only have metadata (title/journal/pubdate). You do NOT have abstracts.\n"
        '- Therefore key_finding MUST be conservative and title-based, e.g., "Title suggests ...".\n'
        "- Do NOT claim numerical outcomes, statistical significance, or detailed results.\n\n"

        "GUIDELINES (MVP):\n"
        "- Call tool get_guideline_sources(indication.name).\n"
        "- Populate web.guidelines[] from the returned list.\n"
        "- Do NOT invent guideline quotes. Use the returned recommendation placeholder.\n\n"

        "NEWS:\n"
        "- Build a query using molecule.primary.inn + indication.name + region (if present).\n"
        '- Example: "roflumilast COPD India"\n'
        "- Call tool news_rss_search(query, max_items=5).\n"
        "- Populate web.news[] ONLY from tool output.\n"
        "- Do NOT invent headlines or URLs.\n\n"

        "OUTPUT RULES (VERY IMPORTANT):\n"
        "- Return ONLY valid JSON (no markdown, no backticks, no commentary).\n"
        "- Do not invent PMIDs, URLs, dates, or quotes.\n"
        "- If PubMed returns zero results, publications must be an empty array.\n\n"

        "Required output schema:\n"
        "{\n"
        '  "web": {\n'
        '    "guidelines": [\n'
        "      {\n"
        '        "source": "string",\n'
        '        "publisher": "string",\n'
        '        "date": "YYYY-MM-DD",\n'
        '        "recommendation": "string",\n'
        '        "url": "string"\n'
        "      }\n"
        "    ],\n"
        '    "publications": [\n'
        "      {\n"
        '        "pmid": "string",\n'
        '        "title": "string",\n'
        '        "journal": "string",\n'
        '        "year": 2024,\n'
        '        "key_finding": "string"\n'
        "      }\n"
        "    ],\n"
        '    "news": [\n'
        "      {\n"
        '        "headline": "string",\n'
        '        "publisher": "string",\n'
        '        "date": "YYYY-MM-DD",\n'
        '        "takeaway": "string",\n'
        '        "url": "string"\n'
        "      }\n"
        "    ],\n"
        '    "summary": "string",\n'
        '    "confidence_level": "low|moderate|high"\n'
        "  }\n"
        "}\n"
    ),
    expected_output=(
        "A single valid JSON object matching the schema exactly. "
        "No extra text outside JSON."
    ),
    agent=agent,
)
