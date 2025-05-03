import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Setup project root and src path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

# Import core modules
from multi_agent.saga import Saga
from multi_agent.agent import Agent
from reflection_agent.reflection_agent import ReflectionAgent


print("🔍 Updated sys.path:")
for path in sys.path:
    print(path)

try:
    from multi_agent.saga import Saga
    from multi_agent.agent import Agent
    print("✅ Saga imported successfully!")
    print("✅ Agent imported successfully!")
except ModuleNotFoundError as e:
    print("❌ Import failed:", e)

# Initialize saga and reflection agent
saga = Saga()
reflector = ReflectionAgent()

# Define agents
LT_Agent = Agent(
    name="Locations and Time Setup Agent",
    backstory="You define locations, travel times, and guest arrival schedules for the wedding.",
    task_description=(
        "Define four key locations: B (Boston Airport), G (Gift shop), T (Tailor shop), W (Wedding venue). "
        "List all pairwise travel times in minutes. Then list guest arrivals, including location, time, origin city, and whether they need transport. "
        "Your output will be used by downstream agents to schedule and assign resources."
    ),
    task_expected_output="""
<response>
  <task>Set up locations and arrival schedules</task>
  <locations>B, G, T, W</locations>
  <travel_times>
    B-G: 45, B-T: 30, B-W: 40, G-T: 20, G-W: 25, T-W: 15
  </travel_times>
  <time>Alex: 11:00 AM, Jamie: 12:30 PM, Pat: 12:00 PM</time>
  <people>Alex, Jamie, Pat</people>
</response>
"""
)

TS_Agent = Agent(
    name="Task Setup Agent",
    backstory="You manage the scheduling of gift pickup, clothes preparation, and photography based on arrival times and travel constraints.",
    task_description=(
        "Schedule three tasks: Gift collection (after 12:00 PM), Clothes pickup (before 2:00 PM), and Photo session (at 3:00 PM sharp). "
        "Use context from location and arrival information to ensure feasibility. "
        "Avoid overlapping tasks and respect travel durations."
    ),
    task_expected_output="""
<response>
  <task>Schedule wedding preparation tasks</task>
  <time>Gift: 12:30 PM, Clothes: 11:00 AM, Photo: 3:00 PM</time>
  <people>Emily, Chris, Jordan, Photographer</people>
</response>
"""
)

RM_Agent = Agent(
    name="Resource Management Agent",
    backstory="You assign guests and tasks to available vehicles, ensuring arrival timing and car capacity are respected.",
    task_description=(
        "There are 5 cars available, including Pat's (5-seater, available after he arrives), and Chris (local friend, 5-seater, available after 1:30 PM at W). "
        "Using guest arrival times and task schedules, assign vehicles for pickups and deliveries. Avoid double-booking and ensure everyone arrives on time."
    ),
    task_expected_output="""
<response>
  <task>Assign vehicles to guests and tasks</task>
  <time>Pat: after 12:00 PM, Chris: after 1:30 PM</time>
  <people>Pat, Chris, Alex, Jamie</people>
</response>
"""
)

CV_Agent = Agent(
    name="Constraint Validation Agent",
    backstory="You validate that all task schedules and vehicle assignments comply with time and capacity constraints.",
    task_description=(
        "Ensure the following constraints are respected: Gift visit is between 12:00–12:30 PM, Tailor visit before 2:00 PM, Photo session at or before 3:00 PM. "
        "Vehicle assignments must avoid conflicts (e.g., no car used for two rides at the same time). "
        "Output your confirmation in structured format."
    ),
    task_expected_output="""
<response>
  <task>Validate all timing and vehicle constraints</task>
  <time>Gift: 12–12:30 PM, Tailor: before 2:00 PM, Photo: before 3:00 PM</time>
  <people>Gift clerk, Tailor, Photographer</people>
</response>
"""
)

WEO_Agent = Agent(
    name="Wedding Event Oversight Agent",
    backstory="You oversee execution and respond to disruptions in the wedding logistics plan.",
    task_description=(
        "Monitor completion of all tasks by 3:00 PM. If unexpected events occur (e.g. vehicle breakdown), reassign responsibilities and adjust plans. "
        "Use context from all previous agents to generate a summary and final schedule."
        "Handle last-minute disruption: Chris’s car broke down at 11:00 AM."
    ),
    task_expected_output="""
<response>
  <task>Finalize and confirm all event logistics. 
  <time>All events completed by 3:00 PM</time>
  <people>All guests and staff. Reassign Pat to pick up Jamie as backup.</people>
</response>
"""
)

# Define dependency chain
LT_Agent >> TS_Agent >> RM_Agent >> CV_Agent >> WEO_Agent

# Run reflection loop to revise agent prompts
for agent in [LT_Agent, TS_Agent, RM_Agent, CV_Agent, WEO_Agent]:
    refined_output = reflector.run(
        user_msg=agent.task_description,
        generation_system_prompt="You are a wedding planning agent.",
        reflection_system_prompt="Critique the plan for feasibility and completeness.",
        n_steps=2
    )
    agent.task_description = refined_output

# Execute Saga
saga.transaction_manager([LT_Agent, TS_Agent, RM_Agent, CV_Agent, WEO_Agent])
saga.saga_coordinator(with_rollback=True)
saga.intra_agent()
saga.inter_agent()
saga.select_context("Resource Management Agent")
saga.restore_context("Resource Management Agent")