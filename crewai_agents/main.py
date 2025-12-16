
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




def run_agents(user_query: str):
    # (optional but recommended)
    load_dotenv()

    # 1) Agents
    master = master_agent()
    web_agent = web_intelligence_agent()

    # 2) Tasks
    t1 = master_normalize_task(user_query=user_query, agent=master)
    t2 = web_intelligence_task(agent=web_agent, normalize_task=t1)

    # 3) Crew
    crew = Crew(
        agents=[master, web_agent],
        tasks=[t1, t2],
        process=Process.sequential,
        verbose=True,
    )
    crew.kickoff()

    it1 = _to_dict(getattr(t1.output, "raw", t1.output))
    if "context" not in it1:
        it1 = {"context": it1}

    input_payload = input_parser_for_clinical_trials_agent(it1)
    clinical_result = agent_runner_function(input_payload)
    clinical_result = crew_output_to_dict(clinical_result)

    context_out = _to_dict(getattr(t1.output, "raw", t1.output))
    web_out = _to_dict(getattr(t2.output, "raw", t2.output))

    ctx = context_out.get("context") if isinstance(context_out, dict) else None
    payload_context = ctx if isinstance(ctx, dict) else context_out

    payload = {
        "context": payload_context,
        "inputs": {"web": web_out, "clinical": clinical_result},
        "report_request": {"format": "pdf"},
    }

    report = generate_report_content(payload)
    os.makedirs("examples", exist_ok=True)

    with open("examples/output.json", "w") as f:
        json.dump(report, f, indent=2)

    pdf_path = report["report"]["file"]["path"]
    render_pdf(report, pdf_path)

    return {
        "output_json_path": "examples/output.json",
        "pdf_path": pdf_path,
        "report": report,
    }




# if __name__ == "__main__":
#     result = run_agents(user_query: str)
#     print(result["pdf_path"])





