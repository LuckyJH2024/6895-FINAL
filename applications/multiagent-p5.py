import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Setup project root and src path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

# Print sys.path to verify
print("\U0001F50D Updated sys.path:")
for path in sys.path:
    print(path)

# Try importing core modules
try:
    from multi_agent.saga import Saga
    from multi_agent.agent import Agent
    print("✅ Saga imported successfully!")
    print("✅ Agent imported successfully!")
except ModuleNotFoundError as e:
    print("❌ Import failed:", e)

# Initialize Saga
saga = Saga()

# Define Agents with unified format (aligned with document 6 structure)

MT_Agent = Agent(
    name="Member & Time Setup Agent",
    backstory="You track family members' arrivals and ensure accurate scheduling.",
    task_description="Set up arrival times, locations, and travel durations for all family members.",
    task_expected_output="""
<response>
  <task>Set up arrival schedules and travel plans for family members.</task>
  <people>Sarah (Mom), James (Dad), Emily (Sister), Michael (Brother), Grandma</people>
  <time>
    - James: Lands at BOS at 1:00 PM from SF
    - Emily: Lands at BOS at 2:30 PM from Chicago
    - Michael: Driving from NY, arrives 3:00 PM
    - Grandma: Needs pickup from suburban Boston
    - Sarah: Host, at home all day
  </time>
</response>
"""
)

# ---- Requirement Setup Agent ---- #
RS_Agent = Agent(
    name="Requirement Setup Agent",
    backstory="You manage cooking schedules and key logistical needs.",
    task_description="Schedule turkey and side dish preparation while ensuring someone stays home for supervision.",
    task_expected_output="""
<response>
  <task>Plan cooking tasks to align with dinner time.</task>
  <people>Home cook (TBD)</people>
  <time>
    - Turkey cooking: 4 hours
    - Side dishes prep: 2 hours
    - Supervision: Someone must stay home during cooking
  </time>
</response>
"""
)

# ---- Constraint Validation Agent ---- #
CV_Agent = Agent(
    name="Constraint Validation Agent",
    backstory="You verify all scheduling constraints and ensure compliance.",
    task_description="Validate that all pickups, cooking timelines, and supervision requirements are met.",
    task_expected_output="""
<response>
  <task>Validate pickups, supervision, and task feasibility.</task>
  <people>James, Emily, Grandma, Home cook</people>
  <time>
    - Travel times:
      - Home to BOS Airport: 60 min
      - BOS to Grandma’s: 60 min
      - Home to Grandma’s: 30 min
    - James must rent car after landing
    - Emily requires airport pickup
  </time>
</response>
"""
)

# ---- Supervisor Agent ---- #
SA_Agent = Agent(
    name="Supervisor Agent",
    backstory="You oversee all logistical elements and generate the final dinner preparation report.",
    task_description="Monitor and report on key tasks, including cooking start time, Emily's pickup, and Grandma's pickup.",
    task_expected_output="""
<response>
  <task>Oversee dinner prep and confirm all logistics are satisfied.</task>
  <people>All family members, including Emily and Grandma</people>
  <time>
    - Dinner time: 6:00 PM
    - Cooking (turkey and sides) must finish by 6:00 PM
    - All pickups must be completed before then
  </time>
</response>
"""
)

# Define dependencies
#MT_Agent >> RS_Agent >> CV_Agent >> SA_Agent

# Register Agents and execute
saga.transaction_manager([MT_Agent, RS_Agent, CV_Agent, SA_Agent])
saga.saga_coordinator(with_rollback=True)
saga.intra_agent()
saga.inter_agent()
saga.select_context("Member & Time Setup Agent")
saga.restore_context("Member & Time Setup Agent")
