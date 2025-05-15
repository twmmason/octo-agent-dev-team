# OCTO - Agent Dev Team

# Knowledge is not memory alone! 

*Meme - an element of a culture or system of behaviour passed from one individual to another by imitation or other non-genetic means."

This is a cconside reference implementation of a multi‑agent dev team in the Google Agent Development Kit (ADK).  

There are several novel and bbetreraproaches here to memroy any orchestration, notabily re-introduction of the "meme" concept to overay semantic mmeory and provide shareabl;e common ceonepts ta=hat the state of the sytste, and ccontext at any given time.Knwo. Agents coordinate through a shared JSON "meme" store — and follow workflow rules in **WorkflowDynamics**.

**Next Steps**
Integrate vector backend for meme values.

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
