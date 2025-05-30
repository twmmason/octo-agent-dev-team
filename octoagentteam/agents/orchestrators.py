
"""Stub orchestrator classes – extend as needed."""
from google.adk.agents import LlmAgent, SequentialAgent # Import LlmAgent

class HeadOrchestrator(LlmAgent): ... # Changed to LlmAgent

class CoderAgent(LlmAgent): ... # New CoderAgent

class UberOrchestrator(SequentialAgent): ...
