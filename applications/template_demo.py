#!/usr/bin/env python3
"""
SagaLLM Template Demo Application
This application uses a predefined template to run a multi-agent system regardless of user input.
"""

# Set environment variables without directly modifying stdout/stderr
# ...

# 📂 Project root path
print(f"📂 Project Root: {project_root}")

# ✅ Successfully imported required modules
# ❌ Failed to import module: {e}

# Predefined demo template
# ...

# Status update function
def update_template():
    """Update template state"""
    st.session_state.template = DEMO_TEMPLATE
    st.session_state.has_template = True
    print(f"📝 Preset template loaded, status: {st.session_state.has_template}")

def execute_agents():
    """Execute the template function"""
    st.session_state.execute_clicked = True
    print("🚀 Execute button clicked")

def main():
    """Main entry point for Streamlit app"""
    # Initialize session state for template and execution status
    # ...

    # Debug info
    print(f"Session state: template exists={st.session_state.template is not None}, has_template={st.session_state.has_template}")

    # Page title and description
    st.title("🧠 SagaLLM Multi-Agent")
    st.write("Enter your scenario, and the AI will create and execute a multi-agent system to solve it")

    # Sidebar system status
    st.sidebar.title("System Status")
    st.sidebar.write(f"Template loaded: {'✅' if st.session_state.has_template else '❌'}")
    st.sidebar.write(f"Execution completed: {'✅' if st.session_state.executed else '❌'}")

    if st.sidebar.button("Force Reset"):
        st.session_state.template = DEMO_TEMPLATE
        st.session_state.has_template = True
        st.success("Template has been reset")
        st.rerun()

    # How to use expander
    with st.expander("🔍 How to Use"):
        st.markdown("""
        **Usage**:
        1. Enter your scenario description in the text area
        2. Click "Generate Template" to analyze and design a multi-agent system
        3. Click "Execute Template" to run agents and display results

        **Suitable Scenarios**:
        - Travel planning
        - Event organization
        - Task scheduling
        - Resource allocation
        - Multi-step decision making

        **Tips**:
        - Provide detailed descriptions
        - State constraints clearly
        - Realistic scenarios work best
        """)

    # User input area
    scenario = st.text_area(
        "Describe your scenario, tasks, and constraints", 
        height=200,
        placeholder="Example: I need to plan a family gathering with 10 relatives..."
    )

    # Example selector
    st.subheader("Or choose an example:")
    example_scenarios = {
        # same keys and content, no change needed
    }

    # Generate + Execute buttons
    col1, col2 = st.columns(2)
    with col1:
        generate_button = st.button("1. Generate Agent Template", key="generate_template_button", use_container_width=True)
    with col2:
        execute_button = st.button("2. Execute Agent Template", key="execute_template_button", 
                                  use_container_width=True, 
                                  disabled=(not st.session_state.has_template))

    # Template generation logic
    if generate_button:
        if not scenario:
            st.error("Please enter a scenario description")
        else:
            with st.spinner("Analyzing scenario and generating agent template..."):
                import time
                time.sleep(15)  # Simulate processing time
                update_template()
            st.success("✅ Agent template generated successfully! You can now click 'Execute Agent Template'")
            st.rerun()

    # Display generated template
    if st.session_state.has_template and st.session_state.template is not None:
        template = st.session_state.template
        st.subheader("📋 Generated Template")
        # Agent and dependency details
        # ...

    # Template execution
    if execute_button:
        if not st.session_state.has_template or st.session_state.template is None:
            with st.spinner("Loading template first..."):
                update_template()
                st.success("Template loaded automatically")
        template = st.session_state.template
        with st.spinner("Creating and executing agents..."):
            try:
                agents, agent_dict = create_agents_from_template(template)
                results, saga = execute_template(agents)
                st.session_state.execution_results = (results, saga, agents)
                st.session_state.executed = True
                st.rerun()
            except Exception as e:
                st.error(f"Error during execution: {str(e)}")
                st.code(traceback.format_exc())

    # Display execution results
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
                    st.warning("This agent did not execute or failed")

        st.subheader("📊 Overall Analysis")
        # Construct GPT summary prompt and display result
        # ...

if __name__ == "__main__":
    main()
