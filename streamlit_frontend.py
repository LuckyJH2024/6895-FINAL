import os
import sys
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Set correct import path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import necessary modules
from src.multi_agent.saga import Saga
from src.multi_agent.agent import Agent
from agent_templates import get_templates, get_template_description, get_template

load_dotenv()

# Initialize session_state
if 'saga' not in st.session_state:
    st.session_state.saga = Saga()
if 'agents' not in st.session_state:
    st.session_state.agents = []
if 'agent_names' not in st.session_state:
    st.session_state.agent_names = []
if 'execution_log' not in st.session_state:
    st.session_state.execution_log = []
if 'current_status' not in st.session_state:
    st.session_state.current_status = "Ready"
if 'context' not in st.session_state:
    st.session_state.context = {}

# Page title
st.title("SagaLLM Multi-Agent System")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation", 
    ["Create Agent", "Create from Template", "Configure Dependencies", "Visualization", "Execute", "Check Results"]
)

def add_agent(name, backstory, task_description, expected_output):
    """Add a new Agent"""
    if name in st.session_state.agent_names:
        return f"❌ Agent '{name}' already exists"
    
    try:
        new_agent = Agent(
            name=name,
            backstory=backstory,
            task_description=task_description,
            task_expected_output=expected_output
        )
        st.session_state.agents.append(new_agent)
        st.session_state.agent_names.append(name)
        return f"✅ Agent '{name}' created successfully"
    except Exception as e:
        return f"❌ Failed to create agent: {str(e)}"

def add_dependency(agent_name, dependency_name):
    """Add dependency between agents"""
    if agent_name not in st.session_state.agent_names or dependency_name not in st.session_state.agent_names:
        return f"❌ Agent name does not exist"
    
    agent = next((a for a in st.session_state.agents if a.name == agent_name), None)
    dependency = next((a for a in st.session_state.agents if a.name == dependency_name), None)
    
    try:
        agent.add_dependency(dependency)
        return f"✅ Dependency added: {dependency_name} → {agent_name}"
    except Exception as e:
        return f"❌ Failed to add dependency: {str(e)}"

def create_from_template(template_name):
    """Create agents and dependencies from template"""
    template_data = get_template(template_name)
    if not template_data:
        return f"❌ Template '{template_name}' not found"
    
    # Clear existing agents
    st.session_state.agents = []
    st.session_state.agent_names = []
    
    for agent_data in template_data["agents"]:
        add_agent(
            agent_data["name"],
            agent_data["backstory"],
            agent_data["task_description"],
            agent_data["task_expected_output"]
        )
    
    for dep in template_data["dependencies"]:
        add_dependency(dep["to"], dep["from"])
    
    return f"✅ Successfully created {len(template_data['agents'])} agents from template '{template_name}'"

def visualize_agents():
    """Create and plot agent dependency graph"""
    if not st.session_state.agents:
        st.warning("No agents to visualize. Please create agents first.")
        return
    
    G = nx.DiGraph()
    for agent in st.session_state.agents:
        G.add_node(agent.name)
    for agent in st.session_state.agents:
        for dep in agent.dependencies:
            G.add_edge(dep.name, agent.name)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, arrowsize=20, font_size=10,
            font_weight='bold', arrows=True, ax=ax)
    
    return fig

def run_saga(with_rollback=True):
    """Execute the saga coordinator and return logs"""
    if not st.session_state.agents:
        return "❌ No agents to execute. Please create agents first."
    
    try:
        st.session_state.execution_log = []
        st.session_state.current_status = "Running"
        
        st.session_state.saga.transaction_manager(st.session_state.agents)
        st.session_state.saga.saga_coordinator(with_rollback=with_rollback)
        
        st.session_state.context = st.session_state.saga.context
        st.session_state.current_status = "Completed"
        
        log = []
        for agent in st.session_state.agents:
            if agent.name in st.session_state.context:
                log.append(f"✅ {agent.name}: Success")
            else:
                log.append(f"❌ {agent.name}: Not executed or failed")
        
        return "\n".join(log)
    except Exception as e:
        st.session_state.current_status = "Error"
        return f"❌ Error during execution: {str(e)}"

def view_context(agent_name):
    """View context of a specific agent"""
    if agent_name not in st.session_state.agent_names:
        return "Agent not found"
    
    try:
        if agent_name in st.session_state.context:
            return st.session_state.context[agent_name]
        else:
            return f"Agent '{agent_name}' has no execution context"
    except Exception as e:
        return f"Error retrieving context: {str(e)}"

def rollback_agent(agent_name):
    """Rollback a specific agent"""
    if agent_name not in st.session_state.agent_names:
        return "Agent not found"
    
    try:
        st.session_state.saga.restore_context(agent_name)
        st.session_state.context = st.session_state.saga.context
        return f"Successfully rolled back Agent '{agent_name}'"
    except Exception as e:
        return f"Error during rollback: {str(e)}"

def clear_all_agents():
    """Clear all agents"""
    st.session_state.agents = []
    st.session_state.agent_names = []
    st.session_state.context = {}
    st.session_state.execution_log = []
    return "All agents cleared"

# Display content based on selected page
if page == "Create Agent":
    st.header("Create New Agent")
    
    col1, col2 = st.columns(2)
    
    with col1:
        agent_name = st.text_input("Agent Name")
        agent_backstory = st.text_area("Backstory", height=100)
        agent_task = st.text_area("Task Description", height=100)
        agent_output = st.text_area("Expected Output", height=100)
        
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("Add Agent"):
                result = add_agent(agent_name, agent_backstory, agent_task, agent_output)
                st.success(result) if "✅" in result else st.error(result)
        
        with col1b:
            if st.button("Clear All Agents"):
                result = clear_all_agents()
                st.success(result)
    
    with col2:
        st.subheader("Created Agents")
        if st.session_state.agents:
            for agent in st.session_state.agents:
                with st.expander(agent.name):
                    st.write(f"**Backstory:** {agent.backstory}")
                    st.write(f"**Task:** {agent.task_description}")
                    st.write(f"**Expected Output:** {agent.task_expected_output}")
        else:
            st.info("No agents created yet")

elif page == "Create from Template":
    st.header("Create Agents from Template")
    
    templates = get_templates()
    selected_template = st.selectbox("Select Template", templates)
    
    with st.expander("Template Description"):
        st.write(get_template_description(selected_template))
    
    if st.button("Use this Template"):
        result = create_from_template(selected_template)
        st.success(result) if "✅" in result else st.error(result)
    
    if st.session_state.agents:
        st.subheader(f"{len(st.session_state.agents)} Agents Created")
        for agent in st.session_state.agents:
            with st.expander(agent.name):
                st.write(f"**Backstory:** {agent.backstory}")
                st.write(f"**Task:** {agent.task_description}")

elif page == "Configure Dependencies":
    st.header("Configure Agent Dependencies")
    
    if not st.session_state.agent_names:
        st.warning("Please create agents first")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            source_agent = st.selectbox("Source Agent (upstream)", st.session_state.agent_names)
            target_agent = st.selectbox("Target Agent (downstream)", st.session_state.agent_names)
            
            if st.button("Add Dependency"):
                result = add_dependency(target_agent, source_agent)
                st.success(result) if "✅" in result else st.error(result)
        
        with col2:
            st.subheader("Current Dependencies")
            for agent in st.session_state.agents:
                deps = [dep.name for dep in agent.dependencies]
                if deps:
                    st.write(f"**{agent.name}** depends on: {', '.join(deps)}")

elif page == "Visualization":
    st.header("Agent Dependency Graph")
    
    fig = visualize_agents()
    if fig:
        st.pyplot(fig)

elif page == "Execute":
    st.header("Execute Saga Workflow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with_rollback = st.checkbox("Enable Rollback", value=True)
        st.write(f"**Current Status:** {st.session_state.current_status}")
        
        if st.button("Run Execution"):
            with st.spinner("Running..."):
                result = run_saga(with_rollback)
                st.code(result)
    
    with col2:
        if st.session_state.current_status == "Completed":
            st.subheader("Execution Summary")
            st.write(f"Agents executed: {len(st.session_state.context)}")
            st.progress(len(st.session_state.context) / len(st.session_state.agents))

elif page == "Check Results":
    st.header("Check and Manage Execution Results")
    
    if not st.session_state.context:
        st.warning("No execution results yet. Please run the execution first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            context_agent = st.selectbox("Select Agent", st.session_state.agent_names)
            col1a, col1b = st.columns(2)
            
            with col1a:
                if st.button("View Context"):
                    result = view_context(context_agent)
                    st.session_state.selected_context = result
            
            with col1b:
                if st.button("Rollback Agent"):
                    result = rollback_agent(context_agent)
                    st.success(result) if "Successfully" in result else st.error(result)
        
        with col2:
            st.subheader("Context Content")
            if 'selected_context' in st.session_state:
                st.code(st.session_state.selected_context)

# Sidebar status and version
st.sidebar.markdown("---")
st.sidebar.info(f"Current Status: {st.session_state.current_status}")
st.sidebar.info(f"Number of Agents: {len(st.session_state.agents)}")
st.sidebar.info("SagaLLM Demo Version")
