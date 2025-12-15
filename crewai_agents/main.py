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


from crewai import Crew, Process

from agents import master_agent, web_intelligence_agent
from tasks import master_normalize_task, web_intelligence_task, master_compile_task


def main():
    user_query = "Evaluate repurposing potential of atorvastatin for non-alcoholic fatty liver disease (NAFLD) in India from 2020 to 2025."

    # 1) Agents
    master = master_agent()
    web_agent = web_intelligence_agent()

    # 2) Tasks
    t1 = master_normalize_task(user_query=user_query, agent=master)
    t2 = web_intelligence_task(agent=web_agent, normalize_task=t1)
    t3 = master_compile_task(agent=master, normalize_task=t1, web_task=t2)

    # 3) Crew
    crew = Crew(
        agents=[master, web_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    print("\n===== FINAL OUTPUT (CONTEXT + WEB) =====\n")
    print(result)


if __name__ == "__main__":
    main()
