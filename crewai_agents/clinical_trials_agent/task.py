import yaml
from crewai import Task

def load_task(agent):
    # Load task config
    with open("/workspaces/PHARMA_AI_AGENTS/crewai_agents/clinical_trials_agent/config/task.yaml", "r") as f:
        task_config = yaml.safe_load(f)

    task = Task(
        description=task_config["description"],
        agent=agent,
        expected_output=task_config["expected_output"]
    )

    return task
