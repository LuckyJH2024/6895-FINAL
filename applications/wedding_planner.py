#!/usr/bin/env python3
"""
SagaLLM Wedding Planning Example
This script is specifically designed to run the wedding planning agent template and provide detailed debugging output
"""

import sys
import os
import io
import traceback
from dotenv import load_dotenv
load_dotenv()

# Save original stdout and stderr streams to prevent garbage collection
original_stdout = sys.stdout
original_stderr = sys.stderr

# Set stdout and stderr encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Get project root directory path
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

# Print Python path for verification
print("🔍 Python Path:")
for path in sys.path:
    print(path)

# Try to import necessary modules
try:
    from src.multi_agent.saga import Saga
    from src.multi_agent.agent import Agent
    from agent_templates import get_template
    print("✅ Successfully imported Saga and Agent classes")
except ModuleNotFoundError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def create_wedding_agents():
    """Create wedding planning agents"""
    print("🏗️ Creating wedding planning agents...")
    
    # Get wedding planning agent configuration from template
    template_data = get_template("Wedding Plan")
    if not template_data:
        print("❌ Wedding plan template not found")
        return None, None
    
    # Create agents
    agents = []
    agent_dict = {}
    
    for agent_data in template_data["agents"]:
        print(f"📝 Creating agent: {agent_data['name']}")
        try:
            agent = Agent(
                name=agent_data["name"],
                backstory=agent_data["backstory"],
                task_description=agent_data["task_description"],
                task_expected_output=agent_data["task_expected_output"]
            )
            agents.append(agent)
            agent_dict[agent_data["name"]] = agent
        except Exception as e:
            print(f"❌ Failed to create agent {agent_data['name']}: {e}")
            traceback.print_exc()
    
    # Establish dependencies
    for dep in template_data["dependencies"]:
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
    print("🚀 Starting wedding planning agent system")
    print("==================================================\n")
    
    # Create agents
    agents, agent_dict = create_wedding_agents()
    if not agents:
        print("❌ Failed to create agents, program exiting")
        return
    
    # Create Saga instance
    print("\n🏗️ Initializing Saga coordinator...")
    saga = Saga()
    
    # Register agents and execute
    try:
        print("\n🔄 Registering agents to Saga coordinator...")
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