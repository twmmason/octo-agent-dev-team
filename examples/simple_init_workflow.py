"""Run a toy workflow locally with a simple agent team for a coding task."""
import sys
import os # Import os to access environment variables
import asyncio
import google.generativeai as genai # Import for configure
from dotenv import load_dotenv # Import for loading .env file
from typing import AsyncGenerator, Optional # For AsyncGenerator and Optional

from octoagentteam.agents.orchestrators import HeadOrchestrator, CoderAgent
from google.adk.runners import InMemoryRunner
# Removed BaseLlm, LlmRequest, LlmResponse as they are for custom LLMs
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types # Retained for potential ADK interaction with FunctionCall/Response
# No longer importing GenerativeModel or GoogleGenaiLlm directly here,
# as LlmAgent might handle model string resolution.

# Load environment variables from .env file
# This should be one of the first things the script does.
load_dotenv()

# Configure the Gemini API key
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("FATAL: GOOGLE_API_KEY environment variable not set.")
    sys.exit(1)
except Exception as e_configure:
    print(f"FATAL: Error configuring Google Generative AI: {e_configure}")
    sys.exit(1)


# --- Agent Definitions ---
coder_agent_name = "Python_Coder_Agent" # This name will be used for the tool call
head_orchestrator_name = "Head_Orchestrator_Coding"

# --- Define LLMs ---
# Use actual Gemini models
# Ensure GOOGLE_API_KEY is set in your environment for this to work.
# You might need to install google-generativeai: pip install google-generativeai
gemini_model_name = "gemini-2.5-flash-preview-05-20" # Changed to specific preview model

# --- End LLM Definitions --- (Section removed as model string is passed directly)

# Coder Agent
coder_agent = CoderAgent(
    name=coder_agent_name,
    model=gemini_model_name, # Pass the model name string directly
    instruction=f"You are an expert Python Coder Agent. You will be called as a tool with a 'request' argument containing a specific coding task from a user. Your primary function is to write Python code based on this 'request'. Provide only the Python code block itself, correctly formatted with triple backticks (e.g., ```python\\n# your code here\\n```). Do not include any other explanatory text, conversation, or markdown formatting before or after the code block. Your response must be ONLY the code block."
)

# Head Orchestrator Agent
head_orchestrator = HeadOrchestrator(
    name=head_orchestrator_name,
    model=gemini_model_name, # Pass the model name string directly
    instruction=f"You are a Head Orchestrator. You have one tool: '{coder_agent_name}'. Your ONLY task is to take the user's input and immediately call the '{coder_agent_name}' tool. Populate the tool's 'request' argument with the user's entire input. Do not respond to the user directly otherwise. After the '{coder_agent_name}' tool returns code, your final response to the user MUST be only that code block.",
    # sub_agents=[coder_agent], # Removed to prioritize tool usage
    tools=[AgentTool(agent=coder_agent)] # Removed description kwarg
)
# --- End Agent Definitions ---

# Initial user message for the coding task
initial_user_message = "Please write a Python function called 'add_two_numbers' that takes two integers, 'a' and 'b', as input and returns their sum."

app_name = "CodingWorkflowApp"
runner = InMemoryRunner(agent=head_orchestrator, app_name=app_name) # Root agent is head_orchestrator

user_id = "test_user_coding_e2e"
session_id = "test_session_coding_e2e"

try:
    print(f"Attempting to create session: App='{app_name}', User='{user_id}', Session='{session_id}'")
    created_session = runner.session_service.create_session_sync(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    print(f"Session '{created_session.id}' created successfully for user '{created_session.user_id}'.")
except Exception as e_session_create:
    print(f"FATAL: Failed to create session: {e_session_create}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

new_message = genai_types.Content(parts=[genai_types.Part(text=initial_user_message)])

print(f"\nRunning coding workflow with agent: {head_orchestrator.name} using {type(head_orchestrator.model).__name__}")
print(f"User ID: {user_id}, Session ID: {session_id}")
print(f"Initial user message to agent: '{initial_user_message}'")

event_count = 0
error_in_workflow = False
try:
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=new_message):
        event_count += 1
        print(f"\n--- Event {event_count} ---")
        print(f"  ID: {event.id}")
        print(f"  Author: {event.author}")
        print(f"  Invocation ID: {event.invocation_id}")
        print(f"  Timestamp: {event.timestamp}")
        print(f"  Partial: {event.partial}")

        if hasattr(event, 'content') and event.content and event.content.parts:
            print(f"  Content Parts ({len(event.content.parts)}):")
            for i, part in enumerate(event.content.parts):
                print(f"    Part {i+1}:")
                if hasattr(part, 'text') and part.text is not None:
                    text_to_print = part.text[:200] + ('...' if len(part.text) > 200 else '')
                    print(f"      Text: \"{text_to_print}\"")
                if hasattr(part, 'function_call') and part.function_call:
                    print(f"      Function Call: {part.function_call.name}, Args: {part.function_call.args}")
                if hasattr(part, 'function_response') and part.function_response:
                     print(f"      Function Response: {part.function_response.name}, Response: {part.function_response.response}")
                if hasattr(part, 'inline_data') and part.inline_data: # Should be after text/func
                    print(f"      Inline Data MimeType: {part.inline_data.mime_type}, Size: {len(part.inline_data.data)} bytes")

        elif hasattr(event, 'type'):
             print(f"  Type: {event.type}")
        if hasattr(event, 'error_details') and event.error_details:
            print(f"  Error Details: {event.error_details}")
            error_in_workflow = True

    if event_count == 0 and not error_in_workflow:
        print("\nCRITICAL: No events were generated by the workflow. This might indicate an issue.")
        error_in_workflow = True
except Exception as e_run:
    print(f"\nAn error occurred during workflow execution (runner.run call): {e_run}")
    import traceback
    traceback.print_exc()
    error_in_workflow = True
finally:
    try:
        print("\nAttempting runner cleanup...")
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                 print("Skipping async runner.close() in sync script due to active event loop.")
            else: asyncio.run(runner.close())
        except RuntimeError: asyncio.run(runner.close())
        print("Runner cleanup attempted.")
    except Exception as e_close: print(f"Error during runner.close(): {e_close}")

if error_in_workflow:
    print("\nScript completed with errors.")
    sys.exit(1)
else:
    print("\nScript completed successfully.")
    sys.exit(0)
