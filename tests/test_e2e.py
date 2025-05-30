import subprocess
import sys
import os
import pytest # Import pytest to use skip functionality
from dotenv import load_dotenv # Import for loading .env file

# Load environment variables from .env file at the module level
# This ensures that os.environ is populated before the test function runs.
load_dotenv()

def test_simple_workflow_execution():
    """
    Runs the simple_init_workflow.py script and checks for successful execution.
    Skips the test if GOOGLE_API_KEY is not set in the environment.
    """
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY environment variable not set. Skipping e2e test.")

    # Project root is one directory up from the 'tests' directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Path to the script to be tested
    script_to_test = os.path.join(project_root, "examples", "simple_init_workflow.py")
    
    absolute_script_path = os.path.abspath(script_to_test)

    if not os.path.exists(absolute_script_path):
        # Pytest will show this FileNotFoundError if the script is not found
        raise FileNotFoundError(f"Test script not found: {absolute_script_path}")

    # Prepare environment for the subprocess
    env = os.environ.copy()
    # Ensure the project root is in PYTHONPATH so 'octoagentteam' can be imported,
    # and its dependencies like 'google-adk' are resolved correctly.
    # Prepending ensures local project code is prioritized.
    current_pythonpath = env.get("PYTHONPATH", "")
    if current_pythonpath:
        env["PYTHONPATH"] = f"{project_root}{os.pathsep}{current_pythonpath}"
    else:
        env["PYTHONPATH"] = project_root
    
    try:
        # Run the script using the same Python interpreter that's running pytest
        # Set cwd to project_root for consistent relative path resolution within the script if any.
        process = subprocess.run(
            [sys.executable, absolute_script_path],
            capture_output=True,
            text=True,
            check=False,  # We'll check the returncode manually
            timeout=120,  # Increased timeout
            env=env,
            cwd=project_root 
        )
        
        # Print stdout and stderr for debugging, especially useful on CI or if tests fail
        # These will be captured by pytest and shown on failure, or if -s is used.
        print(f"\n--- Script STDOUT for examples/simple_init_workflow.py ---")
        print(process.stdout)
        print(f"--- End Script STDOUT ---\n")
        
        if process.stderr:
            print(f"--- Script STDERR for examples/simple_init_workflow.py ---")
            print(process.stderr)
            print(f"--- End Script STDERR ---\n")

        if process.returncode == 0:
            print("SUCCESS: Script examples/simple_init_workflow.py executed successfully with return code 0.")
        
        assert process.returncode == 0, (
            f"Script execution failed with return code {process.returncode}.\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )
        
    except subprocess.TimeoutExpired:
        # This specific exception is worth catching and reporting clearly
        assert False, "Script execution timed out."
    # Other exceptions from subprocess.run (like if sys.executable is bad)
    # will be caught by pytest and reported.