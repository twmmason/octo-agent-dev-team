
# OCTOAgentTeam

Minimal reference implementation of a **multi‑agent“OCTOAgentTeam”** on the Google Agent Development Kit (ADK).  

Agents coordinate through a shared JSON "meme" store—now called **Meme**—and follow workflow rules in **WorkflowDynamics**.

## Quick start

1. **Set up Python 3.10+ and ADK**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .          # installs octoagentteam plus google‑adk



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


## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python examples/simple_init_workflow.py
```

See `docs/` for further details.
