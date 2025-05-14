import sys
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ 1. Set the project root and forcefully change the working directory
project_root = os.path.abspath(os.path.dirname(__file__))  # If this script is located at the root
os.chdir(project_root)  # Force switch to project root
print(f"📂 Project Root: {project_root}")

# ✅ 2. Add 'src' directory to sys.path
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# ✅ 3. Print sys.path and contents of src for debugging
print("🔍 Updated sys.path:")
for path in sys.path:
    print(path)
print("📁 Contents in src:", os.listdir(src_path))

# ✅ 4. Try importing Saga and Agent modules
try:
    from multi_agent.saga import Saga
    from multi_agent.agent import Agent
    print("✅ Saga imported successfully!")
    print("✅ Agent imported successfully!")
except ModuleNotFoundError as e:
    print("❌ Import failed:", e)
    sys.exit(1)

# ✅ 5. Initialize the Saga instance
saga = Saga()

# ✅ 6. Create two conflicting agents (same time + same person)
Agent_A = Agent(
    name="Agent A",
    backstory="Schedule tasks for Alex.",
    task_description="Schedule a task for Alex at 10:00 AM.",
    task_expected_output="""
    <response>
        <task>Task A</task>
        <time>10:00 AM</time>
        <people>Alex</people>
    </response>
    """
)

Agent_B = Agent(
    name="Agent B",
    backstory="Schedule a second task for Alex.",
    task_description="Schedule another task for Alex at 10:00 AM.",
    task_expected_output="""
    <response>
        <task>Task B</task>
        <time>10:00 AM</time>
        <people>Alex</people>
    </response>
    """
)

# ✅ 7. Register and execute the Saga to trigger rollback due to conflict
saga.transaction_manager([Agent_A, Agent_B])
saga.saga_coordinator(with_rollback=True)
