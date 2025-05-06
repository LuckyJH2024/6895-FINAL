#!/usr/bin/env python3
"""
SagaLLM模板生成器
根据用户的自然语言输入，自动生成并执行自定义的智能体模板
"""

import sys
import os
import io
import json
import traceback
from dotenv import load_dotenv
load_dotenv()

# 设置环境变量而不是直接修改stdout/stderr
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
    from src.multi_agent.saga import Saga
    from src.multi_agent.agent import Agent
    from src.planning_agent.react_agent import ReactAgent
    from src.tool_agent.tool import Tool
    from openai import OpenAI
    print("✅ 成功导入必要的模块")
    
    # 有条件导入streamlit
    try:
        import streamlit as st
    except ImportError:
        st = None
        
except ModuleNotFoundError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 创建OpenAI客户端
client = OpenAI()

def generate_template(scenario_description):
    """
    根据用户的自然语言描述生成智能体模板
    
    Args:
        scenario_description: 用户输入的场景描述、背景和约束条件
        
    Returns:
        generated_template: 生成的模板定义，包含智能体和依赖关系
    """
    print("🧠 分析场景描述并生成智能体模板...")
    
    # 设计提示
    prompt = f"""
你是一个多智能体系统设计专家，你需要将用户的自然语言问题转换为一组合适的智能体及其依赖关系。

用户场景描述:
{scenario_description}

请分析上述场景，并创建一个多智能体系统，遵循以下规则：
1. 确定所需的智能体类型和角色
2. 为每个智能体定义明确的任务和职责
3. 确定智能体之间的依赖关系
4. 确保系统整体可以解决用户的问题

请用以下JSON格式返回你的设计：

```json
{{
  "template_name": "模板名称",
  "description": "模板描述",
  "agents": [
    {{
      "name": "智能体1名称",
      "backstory": "智能体1的背景故事和角色定义",
      "task_description": "智能体1的具体任务描述",
      "task_expected_output": "<response>\n  <task>任务名称</task>\n  <people>相关人员</people>\n  <time>相关时间安排</time>\n</response>"
    }},
    {{
      "name": "智能体2名称",
      "backstory": "智能体2的背景故事和角色定义",
      "task_description": "智能体2的具体任务描述",
      "task_expected_output": "<response>\n  <task>任务名称</task>\n  <people>相关人员</people>\n  <time>相关时间安排</time>\n</response>"
    }}
    // 更多智能体...
  ],
  "dependencies": [
    {{"from": "上游智能体名称", "to": "下游智能体名称"}},
    {{"from": "上游智能体名称", "to": "下游智能体名称"}}
    // 更多依赖关系...
  ]
}}
```

确保你的设计是合理的，智能体职责明确，依赖关系清晰，没有循环依赖。
"""
    
    # 调用OpenAI API生成模板
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    # 提取JSON模板
    result = response.choices[0].message.content
    try:
        # 从回复中提取JSON部分
        json_str = result.split("```json")[1].split("```")[0].strip() if "```json" in result else result
        template = json.loads(json_str)
        print("✅ 成功生成模板")
        return template
    except Exception as e:
        print(f"❌ 解析模板JSON失败: {e}")
        print(f"原始返回内容: {result}")
        return None

def create_agents_from_template(template):
    """
    根据生成的模板创建智能体及其依赖关系
    
    Args:
        template: 包含智能体定义和依赖关系的模板
        
    Returns:
        agents: 创建的智能体列表
        agent_dict: 智能体名称到对象的映射
    """
    print("🏗️ 根据生成的模板创建智能体...")
    
    agents = []
    agent_dict = {}
    
    # 创建智能体
    for agent_data in template["agents"]:
        print(f"📝 创建智能体: {agent_data['name']}")
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
            print(f"❌ 创建智能体 {agent_data['name']} 失败: {e}")
            traceback.print_exc()
    
    # 建立依赖关系
    for dep in template["dependencies"]:
        from_agent = agent_dict.get(dep["from"])
        to_agent = agent_dict.get(dep["to"])
        if from_agent and to_agent:
            print(f"🔗 建立依赖关系: {dep['from']} → {dep['to']}")
            try:
                from_agent.add_dependent(to_agent)
            except Exception as e:
                print(f"❌ 建立依赖关系失败: {e}")
                traceback.print_exc()
    
    return agents, agent_dict

def execute_template(agents):
    """
    执行创建的智能体模板
    
    Args:
        agents: 智能体列表
        
    Returns:
        results: 执行结果
    """
    print("\n🚀 执行智能体任务...")
    
    # 创建Saga实例
    saga = Saga()
    results = {"success": False, "context": {}, "error": None}
    
    try:
        # 注册智能体并执行
        saga.transaction_manager(agents)
        saga.saga_coordinator(with_rollback=True)
        
        # 收集结果
        results["success"] = True
        results["context"] = saga.context
    except Exception as e:
        results["error"] = str(e)
        traceback.print_exc()
    
    return results, saga

def create_streamlit_app():
    """创建Streamlit应用界面"""
    if st is None:
        print("❌ Streamlit未安装，无法创建Web界面")
        return
        
    st.set_page_config(page_title="SagaLLM模板生成器", page_icon="🧠", layout="wide")
    
    st.title("🧠 SagaLLM智能模板生成器")
    st.write("输入你的问题场景，AI将自动创建并执行一个多智能体系统来解决它")
    
    # 用户输入
    scenario = st.text_area(
        "描述你的场景、任务和约束条件", 
        height=200,
        placeholder="例如：我需要规划一次家庭聚会，有10个亲戚要来，其中有些人需要接送，活动包括准备食物、游戏和住宿安排。有些人是素食者，有些人对花生过敏..."
    )
    
    # 生成模板部分
    if st.button("生成并执行"):
        if not scenario:
            st.error("请输入场景描述")
            return
        
        # 生成模板
        with st.spinner("正在分析场景并生成智能体模板..."):
            template = generate_template(scenario)
            
        if not template:
            st.error("生成模板失败，请重试或修改输入")
            return
        
        # 显示生成的模板
        st.success("✅ 智能体模板生成成功!")
        st.subheader("📋 生成的模板")
        
        # 显示模板详情
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**名称**: {template.get('template_name', '自定义模板')}")
            st.write(f"**描述**: {template.get('description', '根据用户输入生成的模板')}")
            
            st.write("**智能体**:")
            for idx, agent in enumerate(template["agents"]):
                with st.expander(f"{idx+1}. {agent['name']}"):
                    st.write(f"**背景**: {agent['backstory']}")
                    st.write(f"**任务**: {agent['task_description']}")
                    st.write("**预期输出**:")
                    st.code(agent.get('task_expected_output', ''), language="xml")
        
        with col2:
            st.write("**依赖关系**:")
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
                st.warning(f"无法绘制依赖关系图: {e}")
        
        # 创建并执行智能体
        with st.spinner("正在创建并执行智能体..."):
            try:
                agents, agent_dict = create_agents_from_template(template)
                results, saga = execute_template(agents)
            except Exception as e:
                st.error(f"执行过程中出错: {str(e)}")
                st.code(traceback.format_exc())
                return
        
        # 显示执行结果
        if results["success"]:
            st.success("✅ 智能体执行成功!")
        else:
            st.error(f"❌ 执行出错: {results['error']}")
        
        # 显示每个智能体的输出
        st.subheader("🔍 执行结果")
        
        for agent in agents:
            with st.expander(f"{agent.name} 的输出"):
                if agent.name in saga.context:
                    st.code(saga.context[agent.name], language="xml")
                else:
                    st.warning("该智能体未执行或执行失败")
        
        # 显示总体结论
        st.subheader("📊 总体分析")
        
        # 从结果中提取关键信息生成总结
        agent_outputs = []
        for agent in agents:
            if agent.name in saga.context:
                agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")
        
        summary_prompt = f"""
根据以下多智能体系统的执行结果，为用户提供一个简洁的总结。原始问题是:

{scenario}

各智能体的输出:
{agent_outputs}

请提供一个简明的总结，解释系统如何解决了用户的问题，以及关键的见解和建议。
"""
        
        with st.spinner("正在生成总结..."):
            summary_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.7,
            )
            summary = summary_response.choices[0].message.content
        
        st.write(summary)

def cli_interface():
    """命令行界面"""
    print("\n==================================================")
    print("🧠 SagaLLM智能模板生成器")
    print("==================================================\n")
    
    # 获取用户输入
    print("请描述你的场景、任务和约束条件（输入完成后按Ctrl+D或Ctrl+Z+回车结束）：")
    scenario_lines = []
    try:
        while True:
            line = input()
            scenario_lines.append(line)
    except EOFError:
        pass
    
    scenario_description = "\n".join(scenario_lines)
    
    if not scenario_description.strip():
        print("❌ 未输入场景描述，程序退出")
        return
    
    # 生成模板
    template = generate_template(scenario_description)
    if not template:
        print("❌ 生成模板失败，程序退出")
        return
    
    # 打印模板详情
    print("\n==================================================")
    print(f"📋 生成的模板: {template.get('template_name', '自定义模板')}")
    print(f"📝 描述: {template.get('description', '根据用户输入生成的模板')}")
    print("==================================================\n")
    
    print("📑 智能体:")
    for idx, agent in enumerate(template["agents"]):
        print(f"  {idx+1}. {agent['name']}")
        print(f"     背景: {agent['backstory'][:100]}...")
        print(f"     任务: {agent['task_description'][:100]}...")
    
    print("\n🔗 依赖关系:")
    for dep in template["dependencies"]:
        print(f"  - {dep['from']} → {dep['to']}")
    
    # 确认是否执行
    confirm = input("\n是否创建并执行该模板？(y/n): ")
    if confirm.lower() != 'y':
        print("用户取消执行，程序退出")
        return
    
    # 创建并执行智能体
    agents, agent_dict = create_agents_from_template(template)
    results, saga = execute_template(agents)
    
    # 打印执行结果
    print("\n==================================================")
    print("📊 执行结果:")
    print("==================================================\n")
    
    if not results["success"]:
        print(f"❌ 执行出错: {results['error']}")
    
    for agent in agents:
        if agent.name in saga.context:
            print(f"✅ {agent.name}: 执行成功")
            print(f"📄 结果: {saga.context[agent.name][:200]}...\n")
        else:
            print(f"❌ {agent.name}: 未执行或执行失败\n")
    
    # 生成总结
    print("\n==================================================")
    print("📊 总体分析:")
    print("==================================================\n")
    
    agent_outputs = []
    for agent in agents:
        if agent.name in saga.context:
            agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")
    
    summary_prompt = f"""
根据以下多智能体系统的执行结果，为用户提供一个简洁的总结。原始问题是:

{scenario_description}

各智能体的输出:
{agent_outputs}

请提供一个简明的总结，解释系统如何解决了用户的问题，以及关键的见解和建议。
"""
    
    summary_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.7,
    )
    summary = summary_response.choices[0].message.content
    
    print(summary)

if __name__ == "__main__":
    # 检查是否从命令行启动
    if len(sys.argv) > 1 and sys.argv[1] == "--streamlit":
        create_streamlit_app()
    else:
        cli_interface() 