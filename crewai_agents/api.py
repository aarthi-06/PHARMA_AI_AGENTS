from fastapi import FastAPI
from pydantic import BaseModel
from main import run_agents

app = FastAPI()

class RunRequest(BaseModel):
    user_query: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(req: RunRequest):
    return run_agents(req.user_query)
