#!/usr/bin/env python3
"""
Web interface for SagaLLM Template Generator
A simple Streamlit-based UI to create and execute custom multi-agent systems.
"""

import sys
import os
import io
import json
import traceback
from dotenv import load_dotenv
load_dotenv()

# Set environment variables without directly modifying stdout/stderr
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

# Get project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"📂 Project Root: {project_root}")

# Add 'src' directory to Python path
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)
sys.path.append(project_root)

try:
    import streamlit as st

    # Dynamically import template module
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "template_generator", 
            os.path.join(project_root, "applications", "template_generator.py")
        )
        template_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_generator)

        # Import required functions
        generate_template = template_generator.generate_template
        create_agents_from_template = template_generator.create_agents_from_template
        execute_template = template_generator.execute_template

        print("✅ Successfully imported required modules")
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        traceback.print_exc()

except ModuleNotFoundError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Update template state
def update_template(template):
    """Update template status"""
    st.session_state.template = template
    st.session_state.has_template = True
    print(f"📝 Template updated. Status: {st.session_state.has_template}")

def execute_agents():
    """Trigger template execution"""
    st.session_state.execute_clicked = True
    print("🚀 Execute button clicked")

def main():
    """Main entry point for the Streamlit app"""
    st.set_page_config(page_title="SagaLLM Template Generator", page_icon="🧠", layout="wide")

    # Initialize session state
    if 'template' not in st.session_state:
        st.session_state.template = None
    if 'has_template' not in st.session_state:
        st.session_state.has_template = False
    if 'executed' not in st.session_state:
        st.session_state.executed = False
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = None
    if 'execute_clicked' not in st.session_state:
        st.session_state.execute_clicked = False

    st.title("🧠 SagaLLM Template Generator")
    st.write("Describe your scenario and the AI will automatically generate and execute a multi-agent system to solve it.")

    # Sidebar status display (for debugging)
    st.sidebar.subheader("Debug Info")
    st.sidebar.write(f"Template status: {'Generated' if st.session_state.has_template else 'Not generated'}")
    if st.session_state.has_template:
        st.sidebar.write("Template name:", st.session_state.template.get('template_name', 'Unnamed'))
    st.sidebar.write(f"Execution status: {'Executed' if st.session_state.executed else 'Not executed'}")

    # Usage instructions
    with st.expander("🔍 How to Use"):
        st.markdown("""
        **Steps**:
        1. Enter your problem scenario in the text box, including background, constraints, etc.
        2. Click "Generate Template". The system will:
           - Analyze your input
           - Design a multi-agent solution
        3. Click "Execute Template". The system will:
           - Instantiate and run the agents
           - Display results and insights

        **Recommended Use Cases**:
        - Travel planning
        - Event organization
        - Task scheduling
        - Resource allocation
        - Multi-step decision making

        **Tips**:
        - Detailed descriptions yield better results
        - State constraints and factors clearly
        - Real-world scenarios perform better than abstract ones
        """)

    # User input
    scenario = st.text_area(
        "Describe your scenario, tasks, and constraints", 
        height=200,
        placeholder="Example: I need to plan a family gathering with 10 relatives, some require transportation..."
    )

    # Example scenario selector
    st.subheader("Or select an example:")
    example_scenarios = {
        "Family Gathering": """
        I need to plan a family gathering with 12 people including 4 kids and 2 elderly members. Three are vegetarians and two have nut allergies.
        The event is at my home, with a small kitchen and living room for up to 15 people.
        Some members live far away and require transportation. The event will last 6 hours starting at 2 PM.
        I need to buy groceries, prepare meals, organize activities, and ensure everyone can enjoy.
        """,

        "Project Team Collaboration": """
        Our team needs to complete a website development project in 3 weeks. The team includes 2 frontend devs, 1 backend, 1 UI designer, and 1 PM.
        The client requires responsive design, authentication, CMS, and payment integration.
        We use React and Node.js, follow agile methodology, and iterate weekly.
        Team members are in different time zones; some work part-time. We must coordinate task assignment, progress tracking, and QA.
        """,

        "Travel Planning": """
        I’m planning a 7-day Europe trip with friends to Paris, Amsterdam, and Berlin. There are 5 people and a €2000 per person budget.
        We want to see major attractions, try local food, and enjoy some nightlife and shopping.
        One person has mobility issues and needs accessibility support. Another is vegetarian.
        We need to plan transport, lodging, daily itinerary, and budget. It should be comprehensive yet relaxed with free time.
        """
    }

    example = st.selectbox("Select an example scenario", ["None"] + list(example_scenarios.keys()))
    if example != "None":
        scenario = example_scenarios[example]
        st.text_area("Example Scenario", value=scenario, height=200, disabled=True)

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        generate_button = st.button("1. Generate Agent Template", key="generate_template_button", use_container_width=True)

    with col2:
        st.button("2. Execute Agent Template", key="execute_template_button", 
                  use_container_width=True, 
                  on_click=execute_agents)

    # Handle generation
    if generate_button:
        if not scenario:
            st.error("Please enter a scenario description")
        else:
            with st.spinner("Analyzing and generating agent template..."):
                template = generate_template(scenario)

            if not template:
                st.error("Template generation failed. Try again with different input.")
            else:
                update_template(template)
                st.session_state.executed = False
                st.success("✅ Agent template generated! You can now click 'Execute Agent Template'.")

    # Show template details
    if st.session_state.has_template and st.session_state.template is not None:
        template = st.session_state.template

        st.subheader("📋 Generated Template")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name**: {template.get('template_name', 'Custom Template')}")
            st.write(f"**Description**: {template.get('description', 'Generated based on user input')}")
            st.write("**Agents**:")
            for idx, agent in enumerate(template["agents"]):
                with st.expander(f"{idx+1}. {agent['name']}"):
                    st.write(f"**Backstory**: {agent['backstory']}")
                    st.write(f"**Task**: {agent['task_description']}")
                    st.write("**Expected Output**:")
                    st.code(agent.get('task_expected_output', ''), language="xml")

        with col2:
            st.write("**Dependencies**:")
            for dep in template["dependencies"]:
                st.write(f"- {dep['from']} → {dep['to']}")
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
                st.warning(f"Could not draw dependency graph: {e}")

    # Handle execution
    if st.session_state.execute_clicked:
        st.session_state.execute_clicked = False

        if not st.session_state.has_template or st.session_state.template is None:
            st.error("Please generate a template first")
        else:
            template = st.session_state.template

            with st.spinner("Creating and executing agents..."):
                try:
                    agents, agent_dict = create_agents_from_template(template)
                    results, saga = execute_template(agents)

                    st.session_state.execution_results = (results, saga, agents)
                    st.session_state.executed = True
                    st.experimental_rerun()

                except Exception as e:
                    st.error(f"Error during execution: {str(e)}")
                    st.code(traceback.format_exc())

    # Display results
    if st.session_state.executed and st.session_state.execution_results is not None:
        results, saga, agents = st.session_state.execution_results

        st.subheader("🔍 Execution Results")

        if results["success"]:
            st.success("✅ Agent execution completed successfully!")
        else:
            st.error(f"❌ Execution error: {results.get('error', 'Unknown error')}")

        for agent in agents:
            with st.expander(f"{agent.name} Output", expanded=True):
                if agent.name in saga.context:
                    st.code(saga.context[agent.name], language="xml")
                else:
                    st.warning("This agent did not run or failed.")

        st.subheader("📊 Summary Analysis")

        agent_outputs = []
        for agent in agents:
            if agent.name in saga.context:
                agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")

        if agent_outputs:
            from openai import OpenAI
            client = OpenAI()

            summary_prompt = f"""
Based on the following multi-agent system results, summarize how the agents addressed the user's original problem:

{scenario}

Agent Outputs:
{agent_outputs}

Provide a concise summary highlighting how the system solved the problem, key insights, and any actionable recommendations.
"""
            with st.spinner("Generating summary..."):
                summary_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=0.7,
                )
                summary = summary_response.choices[0].message.content

            st.write(summary)
        else:
            st.warning("All agents failed to execute, unable to generate summary.")

if __name__ == "__main__":
    main()
