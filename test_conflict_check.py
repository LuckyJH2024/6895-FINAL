import sys
import os


project_root = os.path.abspath(os.path.join(os.getcwd(), 'src'))
sys.path.append(project_root)

from utils.validation import detect_conflict_across_agents

outputs = {
    "Agent A": """
    <response>
      <task>Pick up Grandma</task>
      <time>2:00 PM</time>
      <people>James</people>
    </response>
    """,
    "Agent B": """
    <response>
      <task>James cooks turkey</task>
      <time>2:00 PM</time>
      <people>James</people>
    </response>
    """,
}

# test conflict check
conflict_report = detect_conflict_across_agents(outputs)
print("⚠️ Conflict Report:", conflict_report)
