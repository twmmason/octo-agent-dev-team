
"""Run a toy workflow locally."""
from octoagentteam.agents.orchestrators import HeadOrchestrator
from google.adk.runtime import run

root = HeadOrchestrator(
    name="Head-Orchestrator",
    model="gemini-pro",
    instruction="Bootstrap project from blueprint docs/blueprint.md",
    sub_agents=[]
)
run(root)
