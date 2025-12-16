from clinical_trials_agent.agent_runner import agent_runner_function
from clinical_trials_agent.tools import fetch_clinical_trials
from crewai import Agent, Task, Crew, LLM
import yaml
import json
from clinical_trials_agent.utils.file_writer import write_output
from clinical_trials_agent.utils.clinical_trials_parser import parse_clinical_trials
from dotenv import load_dotenv

# context={
#             "molecule": {"inn": "remdesivir"},
#             "indication": {"name": "COVID-19"},
#             "region": "Global",
#             "phase": ["I", "II", "III"]
#         }


input_payload={'context': {'intent': 'repurposing_analysis', 'molecule': {'primary': {'inn': 'remdesivir', 'synonyms': ['GS-5734', '2-ethylbutyl (2S)-2-({[(2R,3S,4R,5R)-5-(4-aminopyrrolo[2,1-f][1,2,4]triazin-7-yl)-5-cyano-3,4-dihydroxyoxolan-2-yl]methoxy-phenoxyphosphoryl}amino)propanoate', 'Veklury']}, 'comparators': []}, 'indication': {'name': 'COVID-19', 'codes': {'ICD10': 'U07.1', 'MESH': 'D000086382', 'SNOMED': '840539006', 'ATC': 'J05AB16'}}, 'region': 'India', 'year_range': [2019, 2024], 'dosage_form_hint': None, 'constraints': {'need_fto': True, 'need_supply_view': True, 'mvp_mode': True}}}
def input_parser_for_clinical_trials_agent(inp: dict) -> dict:
    # inp = {"context":inp}
    return {
        "molecule": {
            "inn": inp["context"]["molecule"]["primary"]["inn"]
        },
        "indication": {
            "name": inp["context"]["indication"]["name"]
        },
        "region": inp["context"]["region"],
        "phase": ["I", "II", "III"]
    }





def crew_output_to_dict(crew_output):
    if crew_output.json_dict:
        return crew_output.json_dict
    try:
        return json.loads(crew_output.raw)
    except Exception as e:
        raise ValueError("CrewOutput cannot be converted to dict") from e


input_payload = input_parser_for_clinical_trials_agent(input_payload)
result = agent_runner_function(input_payload)
result = crew_output_to_dict(result)

print(result)
print(type(result))