from crewai import Agent, Task, Crew, LLM
import yaml
from tools import fetch_clinical_trials
from utils.file_writer import write_output
from utils.clinical_trials_parser import parse_clinical_trials
from dotenv import load_dotenv

load_dotenv(override=True)

# Load configs
agent_cfg = yaml.safe_load(open("/workspaces/PHARMA_AI_AGENTS/crewai_agents/clinical_trials_agent/config/agent.yaml"))
task_cfg = yaml.safe_load(open("/workspaces/PHARMA_AI_AGENTS/crewai_agents/clinical_trials_agent/config/task.yaml"))

# Initialize LLM
llm = LLM(model="gpt-4o-mini", temperature=0.1)

# Create agent (NO TOOLS)
agent = Agent(
    role=agent_cfg["role"],
    goal=agent_cfg["goal"],
    backstory=agent_cfg["backstory"],
    llm=llm,
    verbose=True
)

# ------------------------------
# DETERMINISTIC TOOL CALL
# ------------------------------
clinical_trials_data = fetch_clinical_trials(
    context={
        "molecule": {"inn": "remdesivir"},
        "indication": {"name": "COVID-19"},
        "region": "Global",
        "phase": ["I", "II", "III"]
    }
)


clinical_trials_data = parse_clinical_trials(clinical_trials_data)
print(clinical_trials_data)


# Store raw data
write_output(
    clinical_trials_data,
    "/workspaces/PHARMA_AI_AGENTS/crewai_agents/clinical_trials_agent/storage/raw_clinical_trials.json"
)

# Create task
task = Task(
    description="""
    You are given clinical trial data from ClinicalTrials.gov.

    Use ONLY the data provided below.
    DO NOT invent any information.
    If a field is missing in the data, say "Not available".

    Clinical trial data:
    {{clinical_trials_data}}
    """,
    agent=agent,
    expected_output=task_cfg["expected_output"]
)

# Crew
crew = Crew(agents=[agent], tasks=[task])

# Summarization only
result = crew.kickoff(
    inputs={"clinical_trials_data": clinical_trials_data}
)

print(type(result))

# Store final output
# write_output(
#     result,
#     "crewai_agents/clinical_trials_agent/storage/clinical_trials_summary.json"
# )

print("✅ Clinical trials fetched deterministically and summarized successfully.")
