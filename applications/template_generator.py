#!/usr/bin/env python3
"""
SagaLLM Template Generator
Automatically generates and executes custom agent templates based on user's natural language input
"""

import sys
import os
import io
import json
import traceback
from dotenv import load_dotenv
load_dotenv()

# Set environment variables instead of directly modifying stdout/stderr
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

# Get project root directory path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"📂 Project Root: {project_root}")

# Add src directory to Python path
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)
sys.path.append(project_root)

try:
    from src.multi_agent.saga import Saga
    from src.multi_agent.agent import Agent
    from src.planning_agent.react_agent import ReactAgent
    from src.tool_agent.tool import Tool
    from openai import OpenAI
    print("✅ Successfully imported necessary modules")
    
    # Conditionally import streamlit
    try:
        import streamlit as st
    except ImportError:
        st = None
        
except ModuleNotFoundError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Create OpenAI client
client = OpenAI()

def generate_template(scenario_description):
    """
    Generate agent template based on user's natural language description
    
    Args:
        scenario_description: User's input describing the scenario, background, and constraints
        
    Returns:
        generated_template: Generated template definition, including agents and dependencies
    """
    print("🧠 Analyzing scenario description and generating agent template...")
    
    # Design prompt
    prompt = f"""
You are a multi-agent system design expert, and you need to convert the user's natural language problem into a set of appropriate agents and their dependencies.

User scenario description:
{scenario_description}

Please analyze the above scenario and create a multi-agent system following these rules:
1. Determine the types of agents needed and their roles
2. Define clear tasks and responsibilities for each agent
3. Determine dependencies between agents
4. Ensure the system as a whole can solve the user's problem

Please return your design in the following JSON format:

```json
{{
  "template_name": "Template Name",
  "description": "Template Description",
  "agents": [
    {{
      "name": "Agent 1 Name",
      "backstory": "Agent 1 backstory and role definition",
      "task_description": "Specific task description for Agent 1",
      "task_expected_output": "<response>\n  <task>Task Name</task>\n  <people>Relevant People</people>\n  <time>Relevant Time Schedule</time>\n</response>"
    }},
    {{
      "name": "Agent 2 Name",
      "backstory": "Agent 2 backstory and role definition",
      "task_description": "Specific task description for Agent 2",
      "task_expected_output": "<response>\n  <task>Task Name</task>\n  <people>Relevant People</people>\n  <time>Relevant Time Schedule</time>\n</response>"
    }}
    // More agents...
  ],
  "dependencies": [
    {{"from": "Upstream Agent Name", "to": "Downstream Agent Name"}},
    {{"from": "Upstream Agent Name", "to": "Downstream Agent Name"}}
    // More dependencies...
  ]
}}
```

Ensure your design is reasonable, with clear agent responsibilities and dependencies, and without circular dependencies.
"""
    
    # Call OpenAI API to generate template
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    # Extract JSON template
    result = response.choices[0].message.content
    try:
        # Extract JSON portion from the reply
        json_str = result.split("```json")[1].split("```")[0].strip() if "```json" in result else result
        template = json.loads(json_str)
        print("✅ Template generated successfully")
        return template
    except Exception as e:
        print(f"❌ Failed to parse template JSON: {e}")
        print(f"Original return content: {result}")
        return None

def create_agents_from_template(template):
    """
    Create agents and their dependencies based on the generated template
    
    Args:
        template: Template containing agent definitions and dependencies
        
    Returns:
        agents: List of created agents
        agent_dict: Mapping from agent names to objects
    """
    print("🏗️ Creating agents based on the generated template...")
    
    agents = []
    agent_dict = {}
    
    # Create agents
    for agent_data in template["agents"]:
        print(f"📝 Creating agent: {agent_data['name']}")
        try:
            agent = Agent(
                name=agent_data["name"],
                backstory=agent_data["backstory"],
                task_description=agent_data["task_description"],
                task_expected_output=agent_data.get("task_expected_output", "")
            )
            agents.append(agent)
            agent_dict[agent_data["name"]] = agent
        except Exception as e:
            print(f"❌ Failed to create agent {agent_data['name']}: {e}")
            traceback.print_exc()
    
    # Establish dependencies
    for dep in template["dependencies"]:
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

def execute_template(agents):
    """
    Execute the created agent template
    
    Args:
        agents: List of agents
        
    Returns:
        results: Execution results
    """
    print("\n🚀 Executing agent tasks...")
    
    # Create Saga instance
    saga = Saga()
    results = {"success": False, "context": {}, "error": None}
    
    try:
        # Register agents and execute
        saga.transaction_manager(agents)
        saga.saga_coordinator(with_rollback=True)
        
        # Collect results
        results["success"] = True
        results["context"] = saga.context
    except Exception as e:
        results["error"] = str(e)
        traceback.print_exc()
    
    return results, saga

def create_streamlit_app():
    """Create Streamlit application interface"""
    if st is None:
        print("❌ Streamlit is not installed, cannot create Web interface")
        return
        
    st.set_page_config(page_title="SagaLLM Template Generator", page_icon="🧠", layout="wide")
    
    st.title("🧠 SagaLLM Intelligent Template Generator")
    st.write("Enter your problem scenario, and AI will automatically create and execute a multi-agent system to solve it")
    
    # User input
    scenario = st.text_area(
        "Describe your scenario, tasks, and constraints", 
        height=200,
        placeholder="Example: I need to plan a family gathering with 10 relatives, some of whom need transportation. Activities include preparing food, games, and accommodation arrangements. Some people are vegetarians, some have peanut allergies..."
    )
    
    # Generate template section
    if st.button("Generate and Execute"):
        if not scenario:
            st.error("Please enter a scenario description")
            return
        
        # Generate template
        with st.spinner("Analyzing scenario and generating agent template..."):
            template = generate_template(scenario)
            
        if not template:
            st.error("Failed to generate template, please try again or modify your input")
            return
        
        # Display generated template
        st.success("✅ Agent template generated successfully!")
        st.subheader("📋 Generated Template")
        
        # Display template details
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name**: {template.get('template_name', 'Custom Template')}")
            st.write(f"**Description**: {template.get('description', 'Template generated based on user input')}")
            
            st.write("**Agents**:")
            for idx, agent in enumerate(template["agents"]):
                with st.expander(f"{idx+1}. {agent['name']}"):
                    st.write(f"**Background**: {agent['backstory']}")
                    st.write(f"**Task**: {agent['task_description']}")
                    st.write("**Expected Output**:")
                    st.code(agent.get('task_expected_output', ''), language="xml")
        
        with col2:
            st.write("**Dependencies**:")
            for dep in template["dependencies"]:
                st.write(f"- {dep['from']} → {dep['to']}")
            
            # Visualize dependencies
            try:
                import networkx as nx
                import matplotlib.pyplot as plt
                
                G = nx.DiGraph()
                for agent in template["agents"]:
                    G.add_node(agent["name"])
                
                for dep in template["dependencies"]:
                    G.add_edge(dep["from"], dep["to"])
                
                fig, ax = plt.subplots(figsize=(10, 6))
                pos = nx.spring_layout(G, seed=42)
                nx.draw(G, pos, with_labels=True, node_color='skyblue', 
                        node_size=2000, arrowsize=20, font_size=10,
                        font_weight='bold', arrows=True, ax=ax)
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"Cannot draw dependency graph: {e}")
        
        # Create and execute agents
        with st.spinner("Creating and executing agents..."):
            try:
                agents, agent_dict = create_agents_from_template(template)
                results, saga = execute_template(agents)
            except Exception as e:
                st.error(f"Error during execution: {str(e)}")
                st.code(traceback.format_exc())
                return
        
        # Display execution results
        if results["success"]:
            st.success("✅ Agents executed successfully!")
        else:
            st.error(f"❌ Execution error: {results['error']}")
        
        # Display output from each agent
        st.subheader("🔍 Execution Results")
        
        for agent in agents:
            with st.expander(f"{agent.name} Output"):
                if agent.name in saga.context:
                    st.code(saga.context[agent.name], language="xml")
                else:
                    st.warning("This agent did not execute or execution failed")
        
        # Display overall analysis
        st.subheader("📊 Overall Analysis")
        
        # Extract key information from results to generate summary
        agent_outputs = []
        for agent in agents:
            if agent.name in saga.context:
                agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")
        
        summary_prompt = f"""
Based on the following multi-agent system execution results, provide a concise summary for the user. The original problem was:

{scenario}

Agent outputs:
{agent_outputs}

Please provide a concise summary explaining how the system addressed the user's problem, along with key insights and recommendations.
"""
        
        with st.spinner("Generating summary..."):
            summary_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.7,
            )
            summary = summary_response.choices[0].message.content
        
        st.write(summary)

def cli_interface():
    """Command line interface"""
    print("\n==================================================")
    print("🧠 SagaLLM Intelligent Template Generator")
    print("==================================================\n")
    
    # Get user input
    print("Please describe your scenario, tasks, and constraints (press Ctrl+D or Ctrl+Z+Enter when done):")
    scenario_lines = []
    try:
        while True:
            line = input()
            scenario_lines.append(line)
    except EOFError:
        pass
    
    scenario_description = "\n".join(scenario_lines)
    
    if not scenario_description.strip():
        print("❌ No scenario description entered, program exiting")
        return
    
    # Generate template
    template = generate_template(scenario_description)
    if not template:
        print("❌ Failed to generate template, program exiting")
        return
    
    # Print template details
    print("\n==================================================")
    print(f"📋 Generated Template: {template.get('template_name', 'Custom Template')}")
    print(f"📝 Description: {template.get('description', 'Template generated based on user input')}")
    print("==================================================\n")
    
    print("📑 Agents:")
    for idx, agent in enumerate(template["agents"]):
        print(f"  {idx+1}. {agent['name']}")
        print(f"     Background: {agent['backstory'][:100]}...")
        print(f"     Task: {agent['task_description'][:100]}...")
    
    print("\n🔗 Dependencies:")
    for dep in template["dependencies"]:
        print(f"  - {dep['from']} → {dep['to']}")
    
    # Confirm execution
    confirm = input("\nCreate and execute this template? (y/n): ")
    if confirm.lower() != 'y':
        print("User cancelled execution, program exiting")
        return
    
    # Create and execute agents
    agents, agent_dict = create_agents_from_template(template)
    results, saga = execute_template(agents)
    
    # Print execution results
    print("\n==================================================")
    print("📊 Execution Results:")
    print("==================================================\n")
    
    if not results["success"]:
        print(f"❌ Execution error: {results['error']}")
    
    for agent in agents:
        if agent.name in saga.context:
            print(f"✅ {agent.name}: Execution successful")
            print(f"📄 Result: {saga.context[agent.name][:200]}...\n")
        else:
            print(f"❌ {agent.name}: Not executed or execution failed\n")
    
    # Generate summary
    print("\n==================================================")
    print("📊 Overall Analysis:")
    print("==================================================\n")
    
    agent_outputs = []
    for agent in agents:
        if agent.name in saga.context:
            agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")
    
    summary_prompt = f"""
Based on the following multi-agent system execution results, provide a concise summary for the user. The original problem was:

{scenario_description}

Agent outputs:
{agent_outputs}

Please provide a concise summary explaining how the system addressed the user's problem, along with key insights and recommendations.
"""
    
    summary_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.7,
    )
    summary = summary_response.choices[0].message.content
    
    print(summary)

if __name__ == "__main__":
    # Check if started from command line
    if len(sys.argv) > 1 and sys.argv[1] == "--streamlit":
        create_streamlit_app()
    else:
        cli_interface() 