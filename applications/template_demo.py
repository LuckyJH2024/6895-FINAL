#!/usr/bin/env python3
"""
SagaLLM模板演示应用
无论用户输入什么，都使用预先定义好的模板来运行多智能体系统
"""

import sys
import os
import json
import traceback
from dotenv import load_dotenv
load_dotenv()

# 设置环境变量而不直接修改stdout/stderr
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

# 获取项目根目录路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"📂 项目根目录: {project_root}")

# 添加src目录到Python路径
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)
sys.path.append(project_root)

try:
    import streamlit as st
    
    # 动态导入模块，使用try-except处理可能的导入错误
    try:
        # 通过相对路径导入，避免直接修改sys.path
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "template_generator", 
            os.path.join(project_root, "applications", "template_generator.py")
        )
        template_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_generator)
        
        # 从模块中导入需要的函数
        create_agents_from_template = template_generator.create_agents_from_template
        execute_template = template_generator.execute_template
        
        print("✅ 成功导入必要的模块")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        traceback.print_exc()
        
except ModuleNotFoundError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 预定义的演示模板
DEMO_TEMPLATE = {
    "template_name": "Wedding Logistics Planning System",
    "description": "A multi-agent system to coordinate wedding day logistics including guest transportation, gift collection, attire pickup, and photo session scheduling.",
    "agents": [
        {
            "name": "Locations and Time Setup Agent",
            "backstory": "You define locations, travel times, and guest arrival schedules.",
            "task_description": "Set up locations, travel times, and ensure accurate scheduling of arrivals.",
            "task_expected_output": "<response>\n  <task>Location and time setup for wedding logistics</task>\n  <people>Alex, Jamie, Pat, Chris</people>\n  <locations>\n    <venue id=\"B\">Boston Airport</venue>\n    <venue id=\"G\">Gift Shop</venue>\n    <venue id=\"T\">Tailor Shop</venue>\n    <venue id=\"W\">Wedding Venue</venue>\n  </locations>\n  <travel_times>\n    <route from=\"B\" to=\"G\" minutes=\"45\"/>\n    <route from=\"B\" to=\"T\" minutes=\"30\"/>\n    <route from=\"B\" to=\"W\" minutes=\"40\"/>\n    <route from=\"G\" to=\"T\" minutes=\"20\"/>\n    <route from=\"G\" to=\"W\" minutes=\"25\"/>\n    <route from=\"T\" to=\"W\" minutes=\"15\"/>\n  </travel_times>\n  <guest_arrivals>\n    <guest name=\"Alex\" arrival_location=\"B\" arrival_time=\"11:00 AM\" origin=\"Chicago\" needs_ride=\"true\"/>\n    <guest name=\"Jamie\" arrival_location=\"B\" arrival_time=\"12:30 PM\" origin=\"Atlanta\" needs_ride=\"true\"/>\n    <guest name=\"Pat\" arrival_location=\"W\" arrival_time=\"12:00 PM\" origin=\"NYC\" has_vehicle=\"true\" vehicle_capacity=\"5\"/>\n  </guest_arrivals>\n</response>"
        },
        {
            "name": "Task Setup Agent",
            "backstory": "You manage the scheduling of required wedding tasks.",
            "task_description": "Schedule gift collection after 12:00 PM, clothes pickup before 2:00 PM, and ensure photo session at 3:00 PM.",
            "task_expected_output": "<response>\n  <task>Schedule wedding day tasks</task>\n  <people>Wedding planners, shop staff</people>\n  <task_schedule>\n    <task name=\"Gift Collection\" earliest_start=\"12:00 PM\" location=\"G\" duration_minutes=\"30\"/>\n    <task name=\"Clothes Pickup\" latest_completion=\"2:00 PM\" location=\"T\" duration_minutes=\"45\"/>\n    <task name=\"Photo Session\" fixed_time=\"3:00 PM\" location=\"W\" duration_minutes=\"90\"/>\n  </task_schedule>\n</response>"
        },
        {
            "name": "Resource Management Agent",
            "backstory": "You allocate available transport resources efficiently.",
            "task_description": "Coordinate 5 vehicle usage and Local friend Chris(5-seater)available, for guest transportation and task fulfillment.",
            "task_expected_output": "<response>\n  <task>Allocate transportation resources</task>\n  <people>Pat, Chris, Alex, Jamie</people>\n  <available_vehicles>\n    <vehicle driver=\"Pat\" capacity=\"5\" available_from=\"12:00 PM\" starting_location=\"W\"/>\n    <vehicle driver=\"Chris\" capacity=\"5\" available_from=\"1:30 PM\" starting_location=\"W\"/>\n  </available_vehicles>\n  <allocation_constraints>\n    <constraint>All guests must be transported to their destinations</constraint>\n    <constraint>Vehicles must be available for task completion</constraint>\n    <constraint>Time constraints for travel must be respected</constraint>\n  </allocation_constraints>\n</response>"
        },
        {
            "name": "Constraint Validation Agent",
            "backstory": "You verify all scheduling constraints to ensure smooth execution.",
            "task_description": "Ensure all tasks are completed within operating hours and vehicle constraints are met.",
            "task_expected_output": "<response>\n  <task>Validate all scheduling constraints</task>\n  <people>Wedding planners, guests, drivers</people>\n  <operating_constraints>\n    <constraint entity=\"Gift Store\" type=\"opening_time\" value=\"12:00 PM\"/>\n    <constraint entity=\"Tailor\" type=\"closing_time\" value=\"2:00 PM\"/>\n    <constraint entity=\"All Tasks\" type=\"completion_deadline\" value=\"3:00 PM\"/>\n    <constraint entity=\"Transport\" type=\"vehicles_required\" value=\"2\"/>\n  </operating_constraints>\n  <validation_status>\n    <result>All constraints can be satisfied with proper scheduling</result>\n  </validation_status>\n</response>"
        },
        {
            "name": "Wedding Event Oversight Agent",
            "backstory": "You oversee the entire wedding logistics to ensure a smooth execution of tasks.",
            "task_description": "Monitor and ensure all tasks are completed on time, resolving any logistical issues.",
            "task_expected_output": "<response>\n  <task>Coordinate and oversee wedding day logistics</task>\n  <people>All guests, drivers, and staff</people>\n  <master_schedule>\n    <timeline>\n      <event time=\"11:00 AM\" description=\"Alex arrives at Boston Airport\"/>\n      <event time=\"11:20 AM\" description=\"Depart from Boston Airport with Alex\"/>\n      <event time=\"12:00 PM\" description=\"Drop off Alex at Wedding Venue\"/>\n      <event time=\"12:00 PM\" description=\"Pat arrives at Wedding Venue with vehicle\"/>\n      <event time=\"12:00 PM\" description=\"Gift Store opens\"/>\n      <event time=\"12:30 PM\" description=\"Jamie arrives at Boston Airport\"/>\n      <event time=\"12:35 PM\" description=\"Depart from Boston Airport with Jamie\"/>\n      <event time=\"1:05 PM\" description=\"Arrive at Tailor Shop for Clothes Pickup\"/>\n      <event time=\"1:20 PM\" description=\"Complete Clothes Pickup task\"/>\n      <event time=\"1:20 PM\" description=\"Depart from Tailor Shop to Gift Shop\"/>\n      <event time=\"1:30 PM\" description=\"Chris arrives with vehicle\"/>\n      <event time=\"1:40 PM\" description=\"Arrive at Gift Shop for Gift Collection\"/>\n      <event time=\"1:40 PM\" description=\"Complete Gift Collection task\"/>\n      <event time=\"2:05 PM\" description=\"Drop off Jamie at Wedding Venue\"/>\n      <event time=\"3:00 PM\" description=\"Photo Session begins\"/>\n    </timeline>\n    <critical_path>\n      <item>11:00 AM: Pick up Alex at Boston Airport → 12:00 PM: Drop off at Wedding Venue → 12:30 PM: Pick up Jamie at Boston Airport → 1:05 PM: Clothes Pickup at Tailor Shop → 1:40 PM: Gift Collection at Gift Shop → 2:05 PM: Return to Wedding Venue → 3:00 PM: Photo Session</item>\n    </critical_path>\n    <transportation_summary>\n      <vehicle driver=\"Pat\" capacity=\"5\">\n        <task>Transport Alex from Boston Airport to Wedding Venue (11:20 AM - 12:00 PM)</task>\n        <task>Transport Jamie from Boston Airport to Tailor Shop (12:35 PM - 1:05 PM)</task>\n      </vehicle>\n      <vehicle driver=\"Chris\" capacity=\"5\">\n        <task>Assist with Clothes Pickup at Tailor Shop (1:05 PM - 1:20 PM)</task>\n        <task>Transport from Tailor Shop to Gift Shop (1:20 PM - 1:40 PM)</task>\n        <task>Assist with Gift Collection (1:40 PM - 2:05 PM)</task>\n      </vehicle>\n    </transportation_summary>\n  </master_schedule>\n  <overall_analysis>\n    <key_insights>\n      <insight>The schedule efficiently coordinates all guest pickups while meeting task deadlines</insight>\n      <insight>Clothes pickup is prioritized before gift collection to meet the 2:00 PM deadline</insight>\n      <insight>There is adequate buffer time between tasks to handle unexpected delays</insight>\n      <insight>All activities are completed with sufficient time before the 3:00 PM photo session</insight>\n    </key_insights>\n    <recommendations>\n      <recommendation>Confirm all guest arrival times 24 hours in advance</recommendation>\n      <recommendation>Keep drivers informed of the schedule and potential changes</recommendation>\n      <recommendation>Prepare backup transportation options in case of delays</recommendation>\n      <recommendation>Monitor weather conditions that might affect travel times</recommendation>\n    </recommendations>\n  </overall_analysis>\n</response>"
        }
    ],
    "dependencies": [
        {"from": "Locations and Time Setup Agent", "to": "Task Setup Agent"},
        {"from": "Task Setup Agent", "to": "Resource Management Agent"},
        {"from": "Resource Management Agent", "to": "Constraint Validation Agent"},
        {"from": "Constraint Validation Agent", "to": "Wedding Event Oversight Agent"}
    ]
}

# 状态更新函数
def update_template():
    """更新模板状态"""
    st.session_state.template = DEMO_TEMPLATE
    st.session_state.has_template = True
    print(f"📝 预设模板已加载，状态: {st.session_state.has_template}")

def execute_agents():
    """执行模板函数"""
    st.session_state.execute_clicked = True
    print("🚀 执行按钮被点击")

def main():
    """主函数 - Streamlit应用入口点"""
    st.set_page_config(page_title="SagaLLM Template Generator", page_icon="🧠", layout="wide")
    
    # 初始化session_state以存储模板和执行状态
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
    
    # 添加调试信息
    print(f"当前会话状态: template存在={st.session_state.template is not None}, has_template={st.session_state.has_template}")
    
    # 在页面加载时预先初始化模板（可选）
    if st.session_state.template is None:
        print("页面初始化 - 未加载预设模板")
    
    st.title("🧠 SagaLLM Multi-Agent")
    st.write("Enter your scenario, and the AI will create and execute a multi-agent system to solve it")
    
    # 在侧边栏显示模板状态
    st.sidebar.title("System Status")
    st.sidebar.write(f"Template loaded: {'✅' if st.session_state.has_template else '❌'}")
    st.sidebar.write(f"Execution completed: {'✅' if st.session_state.executed else '❌'}")
    if st.sidebar.button("Force Reset"):
        st.session_state.template = DEMO_TEMPLATE
        st.session_state.has_template = True
        st.success("Template has been reset")
        st.rerun()
    
    # 应用说明
    with st.expander("🔍 How to Use"):
        st.markdown("""
        **Usage**:
        1. Enter your scenario description in the text area, including background and constraints
        2. Click the "Generate Template" button, the system will:
           - Analyze your input
           - Design a multi-agent system
        3. Click the "Execute Template" button, the system will:
           - Create and execute the agents
           - Display execution results and analysis
        
        **Suitable Scenarios**:
        - Travel planning
        - Event organization
        - Task scheduling
        - Resource allocation
        - Multi-step decision making
        
        **Tips**:
        - Provide detailed scenario descriptions for better results
        - Clearly state constraints and considerations
        - Real-world scenarios work better than abstract problems
        """)
    
    # 用户输入
    scenario = st.text_area(
        "Describe your scenario, tasks, and constraints", 
        height=200,
        placeholder="Example: I need to plan a family gathering with 10 relatives, some of whom need transportation. Activities include preparing food, games, and accommodation arrangements. Some people are vegetarians, some have peanut allergies..."
    )
    
    # 示例选择器
    st.subheader("Or choose an example:")
    example_scenarios = {
        "Family Gathering": """
        I need to plan a family gathering. There are 12 family members attending, including 4 children and 2 elderly people. 3 of them are vegetarians, and 2 have nut allergies.
        The gathering will be at my home, and I need to prepare food, drinks, games, and seating arrangements. I have a small kitchen and a living room that can accommodate 15 people.
        Some members live far away and need transportation. The gathering will last 6 hours, starting at 2 PM.
        I need to purchase ingredients, prepare meals, arrange activities, and ensure everyone can participate enjoyably.
        """,
        
        "Project Team Collaboration": """
        Our team needs to complete a website development project within 3 weeks. The team includes 2 frontend developers, 1 backend developer, 1 UI designer, and 1 project manager.
        The client requires the website to have responsive design, user authentication system, content management functionality, and payment integration.
        We use React and Node.js tech stack, follow agile development methodology, and iterate once a week.
        Team members are distributed across different time zones, and some can only work part-time. We need to coordinate task assignment, progress tracking, and quality control.
        """,
        
        "Travel Planning": """
        I'm planning a 7-day European trip with friends, including Paris, Amsterdam, and Berlin. There are 5 people in total, with a budget of 2000 euros per person.
        We want to visit major attractions, experience local cuisine, and have some shopping and nightlife activities.
        One team member has mobility issues and needs accessibility considerations. Another is a vegetarian.
        We need to plan transportation methods, accommodation options, daily itinerary, and budget allocation. We want the itinerary to be comprehensive but not rushed, with free time.
        """
    }
    
    example = st.selectbox("Select an example scenario", ["None"] + list(example_scenarios.keys()))
    if example != "None":
        scenario = example_scenarios[example]
        st.text_area("Example scenario", value=scenario, height=200, disabled=True)
    
    # 生成模板部分 - 将其拆分为两个按钮：生成模板和执行模板
    col1, col2 = st.columns(2)
    
    with col1:
        generate_button = st.button("1. Generate Agent Template", key="generate_template_button", use_container_width=True)
    
    with col2:
        # 使用会话状态的has_template标志来确定按钮是否禁用
        execute_button = st.button("2. Execute Agent Template", key="execute_template_button", 
                                  use_container_width=True, 
                                  disabled=(not st.session_state.has_template))
    
    # 处理生成模板按钮
    if generate_button:
        if not scenario:
            st.error("Please enter a scenario description")
        else:
            # 模拟生成模板的加载状态
            with st.spinner("Analyzing scenario and generating agent template..."):
                # 实际上总是使用预设模板
                import time
                time.sleep(15)  # 模拟处理时间
                update_template()
                
            st.success("✅ Agent template generated successfully! You can now click 'Execute Agent Template' to run it")
            # 添加自动重新加载，确保模板显示
            st.rerun()
    
    # 如果模板已生成，显示模板详情
    if st.session_state.has_template and st.session_state.template is not None:
        template = st.session_state.template
        
        st.subheader("📋 Generated Template")
        
        # 显示模板详情
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
            
            # 可视化依赖关系
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
    
    # 处理执行模板按钮
    if execute_button:
        if not st.session_state.has_template or st.session_state.template is None:
            # 如果模板不存在，先生成一个预设模板
            with st.spinner("Loading template first..."):
                update_template()
                st.success("Template loaded automatically")
                
        # 现在我们确保模板存在
        template = st.session_state.template
        
        with st.spinner("Creating and executing agents..."):
            try:
                # 使用预设模板
                agents, agent_dict = create_agents_from_template(template)
                results, saga = execute_template(agents)
                
                # 保存执行结果到session_state
                st.session_state.execution_results = (results, saga, agents)
                st.session_state.executed = True
                
                # 刷新页面显示结果
                st.rerun()
                
            except Exception as e:
                st.error(f"Error during execution: {str(e)}")
                st.code(traceback.format_exc())
    
    # 显示执行结果（如果已执行）
    if st.session_state.executed and st.session_state.execution_results is not None:
        results, saga, agents = st.session_state.execution_results
        
        # 显示执行结果
        st.subheader("🔍 Execution Results")
        
        if results["success"]:
            st.success("✅ Agent execution completed successfully!")
        else:
            st.error(f"❌ Execution error: {results.get('error', 'Unknown error')}")
        
        # 显示每个智能体的输出
        for agent in agents:
            with st.expander(f"{agent.name} Output", expanded=True):
                if agent.name in saga.context:
                    st.code(saga.context[agent.name], language="xml")
                else:
                    st.warning("This agent did not execute or failed to complete")
        
        # 显示总体结论
        st.subheader("📊 Overall Analysis")
        
        # 从结果中提取关键信息生成总结
        agent_outputs = []
        for agent in agents:
            if agent.name in saga.context:
                agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")
        
        if agent_outputs:
            from openai import OpenAI
            client = OpenAI()
            
            summary_prompt = f"""
Based on the following multi-agent system execution results, provide a comprehensive wedding logistics plan with a detailed timeline. Focus on creating a precise schedule of all events and transportations.

Create a timeline in this format:
## Wedding Day Schedule

| Time              | Activity                                              | People Involved               | Assigned Vehicle/Role         |
|-------------------|-------------------------------------------------------|-------------------------------|-------------------------------|
| 11:00 AM – 12:00 PM | Pat drives from W to B and picks up Alex             | Pat, Alex                     | Car 1 (Pat)                   |
| 12:00 PM – 1:00 PM  | Pat waits at B for Jamie (arrives 12:30 PM), then departs | Pat, Alex, Jamie           | Car 1 (Pat)                   |
| 1:00 PM – 1:30 PM   | Drive to Tailor Shop (T) to pick up clothes          | Pat, Alex, Jamie              | Car 1 (Pat)                   |
| 1:30 PM – 2:15 PM   | Drive to Gift Shop (G) and collect gifts (after 12:00 PM) | Pat, Alex, Jamie          | Car 1 (Pat)                   |
| 2:15 PM – 2:45 PM   | Drive to Wedding Venue (W) from G                    | Pat, Alex, Jamie              | Car 1 (Pat)                   |
| 3:00 PM             | Attend wedding photo session                         | Everyone (Pat, Alex, Jamie, Chris) | All available at W     |


Include all transportation details, pickups, dropoffs, task completions, and venue constraints. Prioritize the clothes pickup before 2:00 PM and ensure the photo session starts at 3:00 PM.

After the timeline, provide brief tips of:
1.Key recommendations for smooth execution
2.potential factors that may affect the execution of the process.
Agent outputs:
{agent_outputs}
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
            st.warning("All agents failed to execute, unable to generate summary")

if __name__ == "__main__":
    main() 