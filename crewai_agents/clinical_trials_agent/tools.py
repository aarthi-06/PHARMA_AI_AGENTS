# import requests
# from crewai.tools import tool
# import yaml

# @tool("fetch_clinical_trials")
# def fetch_clinical_trials(context: dict) -> dict:
#     """
#     Fetch clinical trials from ClinicalTrials.gov for a given drug and disease.

#     Args: 
#         context (dict): A dictionary containing: 
#         - molecule.inn: Drug name (string) 
#         - indication.name: Disease/indication name (string)

#     Returns:
#         dict: JSON response containing clinical trial information.
#     """
#     # Print for debugging
#     print(context)

#     drug = context["molecule"]["inn"]
#     disease = context["indication"]["name"]

#     print(drug)
#     print(disease)

#     # Load API config
#     config = yaml.safe_load(
#         open("crewai_agents/clinical_trials_agent/config/api.yaml")
#     )

#     url = config["clinical_trials"]["base_url"]

#     params = {
#         "query.term": f"{drug} {disease}",
#         "pageSize": 5,
#         "format": "json"
#     }

#     response = requests.get(url, params=params, timeout=10)
#     response.raise_for_status()

#     return response.json()


import requests
import yaml

def fetch_clinical_trials(context: dict) -> dict:
    """
    Deterministic clinical trials fetcher.
    """
    print(context)
    
    # ---- Defensive normalization ----
    if "molecule.inn" in context:
        context["molecule"] = {"inn": context.pop("molecule.inn")}

    if "indication.name" in context:
        context["indication"] = {"name": context.pop("indication.name")}

    # ---- Validation ----
    if "molecule" not in context or "inn" not in context["molecule"]:
        raise ValueError("Missing molecule.inn")

    if "indication" not in context or "name" not in context["indication"]:
        raise ValueError("Missing indication.name")

    drug = context["molecule"]["inn"]
    disease = context["indication"]["name"]

    # Load API config
    config = yaml.safe_load(
        open("/workspaces/PHARMA_AI_AGENTS/crewai_agents/clinical_trials_agent/config/api.yaml")
    )

    url = config["clinical_trials"]["base_url"]

    params = {
        "query.term": f"{drug} {disease}",
        "pageSize": 5,
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()
