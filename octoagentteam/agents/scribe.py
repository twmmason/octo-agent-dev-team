
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.tools import AgentTool
import json, pathlib, uuid, time
from octoagentteam.utils import meme

CONFIG_PATH = pathlib.Path(__file__).resolve().parent.parent / "workflow_dynamics.json"

class MemeScribe(BaseAgent):
    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        summary = ctx.session.state.get("task_orchestrator_summary", "")
        reason  = ctx.session.state.get("handoff_reason", "")
        state   = meme.load()
        cfg     = json.loads(CONFIG_PATH.read_text())

        # Example: very naive rule – production code should use cfg['interpretationLogic']
        if "initialization complete" in summary.lower():
            state["signals"].append({
                "id": str(uuid.uuid4()),
                "signalType": "project_initialization_complete",
                "target": ctx.session.state.get("project_id", "unknown"),
                "category": "state",
                "strength": cfg["defaultSignalStrength"]["state"],
                "message": summary[:256],
                "data": {"handoff_reason": reason},
                "timestamp_created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "last_updated_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })

        state = meme.apply_dynamics(state, cfg)
        meme.save(state)

        yield Event(
            author=self.name,
            content="Meme updated. Activating HeadOrchestrator.",
            actions=EventActions(transfer_to_agent="head-orchestrator")
        )
