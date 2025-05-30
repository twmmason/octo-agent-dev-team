
"""Factory that builds ADK agents from agent_roles.json."""
import json, pathlib
from typing import Dict, Any
from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent

AGENT_ROLES_PATH = pathlib.Path(__file__).resolve().parent.parent / "agent_roles.json"

def make_agent(slug: str, model: str = "gemini-2.5-flash") -> BaseAgent:
    data = json.loads(AGENT_ROLES_PATH.read_text())
    mode = next((m for m in data["customModes"] if m["slug"] == slug), None)
    if not mode:
        raise ValueError(f"Mode {slug} not found")
    # Simple mapping: orchestrators -> SequentialAgent, others -> LlmAgent
    if "orchestrator" in slug:
        return SequentialAgent(
            name=mode["name"],
            model=model,
            instruction=mode["roleDefinition"] + "\n" + mode["customInstructions"],
            sub_agents=[]
        )
    else:
        return LlmAgent(
            name=mode["name"],
            model=model,
            instruction=mode["roleDefinition"] + "\n" + mode["customInstructions"]
        )
