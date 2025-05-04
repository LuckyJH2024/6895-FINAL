#!/usr/bin/env python3
"""
SagaLLM Wedding Planning Example
This script is specifically designed to run the wedding planning agents template with English names
"""

import sys
import os
import io
import traceback
from dotenv import load_dotenv
load_dotenv()

# Save original stdout and stderr to prevent garbage collection
original_stdout = sys.stdout
original_stderr = sys.stderr

# Set stdout and stderr encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Get project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"📂 Project Root: {project_root}")

# Add src directory to Python path
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)
sys.path.append(project_root)

# Set environment variables
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

# Print Python path to verify
print("🔍 Python Path:")
for path in sys.path:
    print(path)

# Try to import necessary modules
try:
    from src.multi_agent.saga import Saga
    from src.multi_agent.agent import Agent
    print("✅ Successfully imported Saga and Agent classes")
except ModuleNotFoundError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def create_wedding_agents():
    """Create wedding planning agents with English names"""
    print("🏗️ Creating wedding planning agents...")
    
    # Create agents
    agents = []
    agent_dict = {}
    
    # Location and Time Setup Agent
    print("📝 Creating agent: Location and Time Setup Agent")
    try:
        location_time_agent = Agent(
            name="Location and Time Setup Agent",
            backstory="You are responsible for defining locations, travel times, and guest arrival schedules.",
            task_description="Set up locations, travel times, and ensure accurate scheduling of arrivals.",
            task_expected_output="""
<response>
  <task>Set up location and time plan</task>
  <people>All guests</people>
  <time>Travel times between locations and expected arrival times for guests</time>
</response>
"""
        )
        agents.append(location_time_agent)
        agent_dict["Location and Time Setup Agent"] = location_time_agent
    except Exception as e:
        print(f"❌ Failed to create Location and Time Setup Agent: {e}")
        traceback.print_exc()
    
    # Task Scheduling Agent
    print("📝 Creating agent: Task Scheduling Agent")
    try:
        task_agent = Agent(
            name="Task Scheduling Agent",
            backstory="You are responsible for managing the scheduling of required wedding tasks.",
            task_description="Schedule gift collection after 12:00 PM, clothes pickup before 2:00 PM, and ensure photo session at 3:00 PM.",
            task_expected_output="""
<response>
  <task>Optimize task schedule</task>
  <people>Staff and participants</people>
  <time>Detailed time schedule for all tasks</time>
</response>
"""
        )
        agents.append(task_agent)
        agent_dict["Task Scheduling Agent"] = task_agent
    except Exception as e:
        print(f"❌ Failed to create Task Scheduling Agent: {e}")
        traceback.print_exc()
    
    # Resource Management Agent
    print("📝 Creating agent: Resource Management Agent")
    try:
        resource_agent = Agent(
            name="Resource Management Agent",
            backstory="You efficiently allocate available transportation resources.",
            task_description="Coordinate the use of 5-seat vehicles and available friends to help, ensuring guest transportation and task completion.",
            task_expected_output="""
<response>
  <task>Vehicle and resource allocation</task>
  <people>Drivers and responsible persons</people>
  <time>Schedule for various resources</time>
</response>
"""
        )
        agents.append(resource_agent)
        agent_dict["Resource Management Agent"] = resource_agent
    except Exception as e:
        print(f"❌ Failed to create Resource Management Agent: {e}")
        traceback.print_exc()
    
    # Constraint Validation Agent
    print("📝 Creating agent: Constraint Validation Agent")
    try:
        constraint_agent = Agent(
            name="Constraint Validation Agent",
            backstory="You validate all scheduling constraints to ensure smooth execution.",
            task_description="Ensure all tasks are completed within business hours and vehicle constraints are met.",
            task_expected_output="""
<response>
  <task>Validate all plans for compliance</task>
  <people>All involved personnel</people>
  <time>Time windows for various constraints</time>
</response>
"""
        )
        agents.append(constraint_agent)
        agent_dict["Constraint Validation Agent"] = constraint_agent
    except Exception as e:
        print(f"❌ Failed to create Constraint Validation Agent: {e}")
        traceback.print_exc()
    
    # Wedding Supervision Agent
    print("📝 Creating agent: Wedding Supervision Agent")
    try:
        supervision_agent = Agent(
            name="Wedding Supervision Agent",
            backstory="You supervise the entire wedding logistics to ensure tasks are executed smoothly.",
            task_description="Monitor and ensure all tasks are completed on time, resolving any logistical issues.",
            task_expected_output="""
<response>
  <task>Global wedding plan coordination</task>
  <people>All relevant personnel</people>
  <time>Complete event schedule</time>
</response>
"""
        )
        agents.append(supervision_agent)
        agent_dict["Wedding Supervision Agent"] = supervision_agent
    except Exception as e:
        print(f"❌ Failed to create Wedding Supervision Agent: {e}")
        traceback.print_exc()
    
    # Establish dependencies
    dependencies = [
        {"from": "Location and Time Setup Agent", "to": "Task Scheduling Agent"},
        {"from": "Location and Time Setup Agent", "to": "Resource Management Agent"},
        {"from": "Task Scheduling Agent", "to": "Constraint Validation Agent"},
        {"from": "Resource Management Agent", "to": "Constraint Validation Agent"},
        {"from": "Constraint Validation Agent", "to": "Wedding Supervision Agent"}
    ]
    
    for dep in dependencies:
        from_agent = agent_dict.get(dep["from"])
        to_agent = agent_dict.get(dep["to"])
        if from_agent and to_agent:
            print(f"🔗 Establishing dependency: {dep['from']} → {dep['to']}")
            try:
                from_agent.add_dependent(to_agent)
            except Exception as e:
                print(f"❌ Failed to establish dependency: {e}")
                traceback.print_exc()
    
    return agents, agent_dict

def main():
    """Main function"""
    print("\n==================================================")
    print("🚀 Starting Wedding Planning Agent System")
    print("==================================================\n")
    
    # Create agents
    agents, agent_dict = create_wedding_agents()
    if not agents:
        print("❌ Failed to create agents, exiting")
        return
    
    # Create Saga instance
    print("\n🏗️ Initializing Saga Coordinator...")
    saga = Saga()
    
    # Register agents and execute
    try:
        print("\n🔄 Registering agents with Saga Coordinator...")
        saga.transaction_manager(agents)
        
        print("\n🚀 Executing agent tasks...")
        saga.saga_coordinator(with_rollback=True)
        
        # Print execution results
        print("\n==================================================")
        print("📊 Execution Results:")
        print("==================================================\n")
        
        for agent in agents:
            if agent.name in saga.context:
                print(f"✅ {agent.name}: Execution successful")
                print(f"📄 Result: {saga.context[agent.name][:200]}...\n")
            else:
                print(f"❌ {agent.name}: Not executed or execution failed\n")
        
        # Print internal and external relationships
        saga.intra_agent()
        saga.inter_agent()
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 