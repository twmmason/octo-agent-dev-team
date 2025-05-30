
"""Meme helper – load/save and apply dynamics."""
from __future__ import annotations
import json, time, uuid, pathlib
from typing import Any, Dict, List

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
STATE_PATH = BASE_DIR / ".memes"
DYNAMICS_PATH = BASE_DIR / "workflow_dynamics.json"

def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def load() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {"signals": [], "documentation_registry": []}
    return json.loads(STATE_PATH.read_text())

def save(data: Dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(data, indent=2))

def _decay(strength: float, rate: float) -> float:
    return max(strength * (1 - rate), 0.0)

def apply_dynamics(state: Dict[str, Any],
                   config: Dict[str, Any]) -> Dict[str, Any]:
    cfg = config["evaporationRates"]
    amp_cfg = config["signalAmplification"]
    seen: Dict[tuple, int] = {}
    for sig in state["signals"]:
        cat = sig.get("category", "default")
        sig["strength"] = _decay(sig["strength"], cfg.get(cat, cfg["default"]))
        sig_id = (sig["signalType"], sig["target"])
        seen[sig_id] = seen.get(sig_id, 0) + 1
    # amplification
    for sig in state["signals"]:
        key = (sig["signalType"], sig["target"])
        if seen[key] > 1:
            sig["strength"] = min(sig["strength"] *
                                   amp_cfg["repeatedSignalBoost"],
                                   amp_cfg["maxAmplification"])
    # prune
    state["signals"] = [s for s in state["signals"]
                        if s["strength"] >= config["signalPruneThreshold"]]
    return state
