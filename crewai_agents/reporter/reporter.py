from datetime import datetime
import uuid


def generate_report_content(payload: dict) -> dict:
    context = payload.get("context", {})
    inputs = payload.get("inputs", {})
    request = payload.get("report_request", {})

    molecule = context.get("molecule", {}).get("primary", {}).get("inn", "unknown")
    indication = context.get("indication", {}).get("name", "unknown")
    region = context.get("region", "unknown")

    report_id = f"REP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

    report = {
        "report": {
            "report_id": report_id,
            "title": f"{molecule.title()} – {indication} – {region} (Repurposing Scan)",
            "generated_at": datetime.now().isoformat(),
            "format": request.get("format", "pdf"),
            "sections": build_sections(inputs, region),
            "warnings": build_warnings(context),
            "file": {
                "type": "pdf",
                "path": f"reports/{molecule}_{indication}_{region}.pdf".lower()
            }
        }
    }

    return report


def build_sections(inputs: dict, region: str) -> dict:
    sections = {}

    web = inputs.get("web", {}).get("web", {})
    clinical = inputs.get("clinical", {}).get("trials", {})

    # Executive Summary
    sections["executive_summary"] = [
        web.get("summary", "No web summary available.")
    ]

    # Clinical Trials
    trial_summary = clinical.get("summary", {})
    phase_dist = trial_summary.get("phase_distribution", {})

    sections["clinical_trials"] = {
        "summary": trial_summary,
        "highlights": [
            f"No Phase III trials identified in {region}"
            if phase_dist.get("III", 0) == 0
            else f"Phase III trials present in {region}"
        ],
        "top_trials": clinical.get("details", [])
    }

    # Guidelines & Literature
    sections["guidelines_and_literature"] = {
        "guideline_points": web.get("guidelines", []),
        "publication_points": web.get("publications", []),
        "news_signals": web.get("news", [])
    }

    # Repurposing Options (derived only from inputs)
    if web.get("summary"):
        sections["repurposing_options"] = [
            {
                "option": "Targeted subgroup usage",
                "rationale": web.get("summary"),
                "evidence": [
                    g.get("source")
                    for g in web.get("guidelines", [])
                    if g.get("source")
                ]
            }
        ]
    else:
        sections["repurposing_options"] = []

    # Risks & Gaps (non-speculative, structural)
    sections["risks_and_gaps"] = [
        "Limited late-stage clinical evidence",
        f"Geography-specific data gaps for {region}"
    ]

    # References
    sections["references"] = build_references(inputs)

    return sections


def build_references(inputs: dict):
    refs = []

    web = inputs.get("web", {}).get("web", {})
    clinical = inputs.get("clinical", {}).get("trials", {})

    for g in web.get("guidelines", []):
        refs.append({
            "type": "guideline",
            "label": g.get("source"),
            "url": g.get("url")
        })

    for p in web.get("publications", []):
        pmid = p.get("pmid")
        if pmid:
            refs.append({
                "type": "publication",
                "label": f"PMID:{pmid}",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })

    for t in clinical.get("details", []):
        trial_id = t.get("trial_id")
        if trial_id:
            refs.append({
                "type": "trial",
                "label": trial_id,
                "url": f"https://clinicaltrials.gov/study/{trial_id}"
            })

    return refs


def build_warnings(context: dict):
    warnings = []
    constraints = context.get("constraints", {})

    if constraints.get("need_fto"):
        warnings.append("FTO requested but not executed in MVP")

    if constraints.get("need_supply_view"):
        warnings.append("Supply view requested but not executed in MVP")

    return warnings
