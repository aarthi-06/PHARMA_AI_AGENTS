# main.py
from crewai import Crew, Process

from agents import web_intelligence_agent
from tasks import web_intelligence_task


def main():
    # 🔹 INPUT JSON (what Master would later send)

    input_payload = {
    "context": {
        "intent": "repurposing_analysis",
        "molecule": {
            "primary": {
                "inn": "ensifentrine",
                "synonyms": ["RPL554"]
            }
        },
        "indication": {
            "name": "COPD"
        },
        "region": "India",
        "year_range": [2020, 2025],
        "recency": "last_24_months",
        "source_whitelist": ["PubMed"]
    }
}


    # 🔹 Create agent
    web_agent = web_intelligence_agent()

    # 🔹 Create task
    task = web_intelligence_task(context=input_payload, agent=web_agent)

    # 🔹 Create crew
    crew = Crew(
        agents=[web_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    # 🔹 Run crew
    result = crew.kickoff()

    print("\n===== FINAL OUTPUT =====\n")
    print(result)


if __name__ == "__main__":
    main()
