# main.py
# from crewai import Crew, Process

# from agents import web_intelligence_agent, master_agent
# from tasks import web_intelligence_task, master_normalize_task

# # def main():
#     # 🔹 INPUT JSON (what Master would later send)

#     input_payload={
#     "context": {
#         "intent": "repurposing_analysis",
#         "molecule": {
#             "primary": {
#                 "inn": "celecoxib",
#                 "synonyms": ["Celebrex", "SC-58635"]
#             }
#         },
#         "indication": {
#             "name": "Alzheimer's Disease"
#         },
#         "region": "India",
#         "year_range": [
#             2020,
#             2025
#         ],
#         "recency": "last_24_months",
#         "source_whitelist": [
#             "PubMed"
#         ]
#     }
# }


#     # 🔹 Create agent
#     web_agent = web_intelligence_agent()

#     # 🔹 Create task
#     task = web_intelligence_task(context=input_payload, agent=web_agent)

#     # 🔹 Create crew
#     crew = Crew(
#         agents=[web_agent],
#         tasks=[task],
#         process=Process.sequential,
#         verbose=True,
#     )

#     # 🔹 Run crew
#     result = crew.kickoff()

#     print("\n===== FINAL OUTPUT =====\n")
#     print(result)


# if __name__ == "__main__":
#     main()






# def main():
#     user_query = "Evaluate repurposing potential of metformin for Alzheimer’s disease in India from 2019 to 2024."


#     # 1) Create Master agent
#     master = master_agent()

#     # 2) Create Master task
#     t1 = master_normalize_task(user_query=user_query, agent=master)

#     # 3) Run crew (only master)
#     crew = Crew(
#         agents=[master],
#         tasks=[t1],
#         process=Process.sequential,
#         verbose=True
#     )

#     result = crew.kickoff()

#     print("\n===== MASTER OUTPUT (NORMALIZED CONTEXT) =====\n")
#     print(result)

# if __name__ == "__main__":
#     main()


# from crewai import Crew, Process

# from agents import master_agent, web_intelligence_agent
# from tasks import master_normalize_task, web_intelligence_task, master_compile_task


# def main():
#     user_query = "Evaluate repurposing potential of atorvastatin for non-alcoholic fatty liver disease (NAFLD) in India from 2020 to 2025."

#     # 1) Agents
#     master = master_agent()
#     web_agent = web_intelligence_agent()

#     # 2) Tasks
#     t1 = master_normalize_task(user_query=user_query, agent=master)
#     t2 = web_intelligence_task(agent=web_agent, normalize_task=t1)
#     t3 = master_compile_task(agent=master, normalize_task=t1, web_task=t2)

#     # 3) Crew
#     crew = Crew(
#         agents=[master, web_agent],
#         tasks=[t1, t2, t3],
#         process=Process.sequential,
#         verbose=True,
#     )

#     result = crew.kickoff()

#     print("\n===== FINAL OUTPUT (CONTEXT + WEB) =====\n")
#     print(result)


# if __name__ == "__main__":
#     main()





import json
import os
from crewai import Crew, Process
from agents import master_agent, web_intelligence_agent
from tasks import master_normalize_task, web_intelligence_task, master_compile_task
from reporter.reporter import generate_report_content
from report_engine.pdf_renderer import render_pdf
from clinical_trials_agent.agent_runner import agent_runner_function
from clinical_trials_agent.tools import fetch_clinical_trials
from crewai import Agent, Task, Crew, LLM
import yaml
from clinical_trials_agent.utils.file_writer import write_output
from clinical_trials_agent.utils.clinical_trials_parser import parse_clinical_trials
from dotenv import load_dotenv

def task_to_dict(task):
    from crewai import Task
    if not isinstance(task, Task):
        raise TypeError("Expected Task object")
    return task.model_dump()


def input_parser_for_clinical_trials_agent(inp: dict) -> dict:
    if "context" not in inp:
      inp = {"context":inp}
    
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


def _to_dict(x):
    """CrewAI sometimes returns JSON string. This makes it a dict safely."""
    if isinstance(x, dict):
        return x
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {"raw": x}
    return {"raw": str(x)}



def main():
    user_query = "Evaluate repurposing potential of remdesivir for COVID-19 in India from 2019 to 2024"

    # 1) Agents
    master = master_agent()
    web_agent = web_intelligence_agent()

    # 2) Tasks
    t1 = master_normalize_task(user_query=user_query, agent=master)
    t2 = web_intelligence_task(agent=web_agent, normalize_task=t1)
    

    

    # 3) Crew
    crew = Crew(
        agents=[master,web_agent],
        tasks=[t1,t2],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()

    
    # print("hi", t1.output,type(t1.output))

    it1 = _to_dict(getattr(t1.output, "raw", t1.output))

    if "context" not in it1:
        it1 = {"context": it1}

    print("hi",it1)
    
    # it1 = {'context': {'intent': 'repurposing_analysis', 'molecule': {'primary': {'inn': 'remdesivir', 'synonyms': ['GS-5734', '2-ethylbutyl (2S)-2-({[(2R,3S,4R,5R)-5-(4-aminopyrrolo[2,1-f][1,2,4]triazin-7-yl)-5-cyano-3,4-dihydroxyoxolan-2-yl]methoxy-phenoxyphosphoryl}amino)propanoate', 'Veklury']}, 'comparators': []}, 'indication': {'name': 'COVID-19', 'codes': {'ICD10': 'U07.1', 'MESH': 'D000086382', 'SNOMED': '840539006', 'ATC': 'J05AB16'}}, 'region': 'India', 'year_range': [2019, 2024], 'dosage_form_hint': None, 'constraints': {'need_fto': True, 'need_supply_view': True, 'mvp_mode': True}}}
    

    input_payload = input_parser_for_clinical_trials_agent(it1)
    clinical_result = agent_runner_function(input_payload)
    clinical_result = crew_output_to_dict(clinical_result)

    # input_payload = input_parser_for_clinical_trials_agent(it1)
    # clinical_result = agent_runner_function(input_payload)
    # clinical_result = crew_output_to_dict(clinical_result)



    # t3 = master_compile_task(
    #     agent=master,
    #     normalize_task=t1,
    #     web_task=t2,
    #     clinical_result=clinical_result  # passed as raw JSON
    # )   

    # compile_crew = Crew(
    #     agents=[master],
    #     tasks=[t3],
    #     process=Process.sequential,
    #     verbose=True,
    # )

    # compile_crew.kickoff()


    context_out = _to_dict(getattr(t1.output, "raw", t1.output))
    web_out = _to_dict(getattr(t2.output, "raw", t2.output))

    ctx = context_out.get("context") if isinstance(context_out, dict) else None
    payload_context = ctx if isinstance(ctx, dict) else context_out

    payload = {
    "context": payload_context,
    "inputs": {
        "web": web_out,
        "clinical": clinical_result
    },
    "report_request": {"format": "pdf"}}


    report = generate_report_content(payload)
    os.makedirs("examples", exist_ok=True)

    with open("examples/output.json", "w") as f:
        json.dump(report, f, indent=2)

    # # 🔹 Generate PDF
    pdf_path = report["report"]["file"]["path"]
    render_pdf(report, pdf_path)

    print("\n✅ Report JSON saved to: examples/output.json")
    print("✅ PDF generated at:", pdf_path)
    print("✅ Report JSON saved to: examples/output.json")



if __name__ == "__main__":
    main()






