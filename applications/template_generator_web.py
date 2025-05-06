#!/usr/bin/env python3
"""
SagaLLM模板生成器的Web界面
基于Streamlit的简易界面，用于创建和执行自定义智能体系统
"""

import sys
import os
import io
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
        generate_template = template_generator.generate_template
        create_agents_from_template = template_generator.create_agents_from_template
        execute_template = template_generator.execute_template
        
        print("✅ 成功导入必要的模块")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        traceback.print_exc()
        
except ModuleNotFoundError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 状态更新函数
def update_template(template):
    """更新模板状态"""
    st.session_state.template = template
    st.session_state.has_template = True
    print(f"📝 模板已更新，状态: {st.session_state.has_template}")

def execute_agents():
    """执行模板函数"""
    st.session_state.execute_clicked = True
    print("🚀 执行按钮被点击")

def main():
    """主函数 - Streamlit应用入口点"""
    st.set_page_config(page_title="SagaLLM模板生成器", page_icon="🧠", layout="wide")
    
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
    
    st.title("🧠 SagaLLM智能模板生成器")
    st.write("输入你的问题场景，AI将自动创建并执行一个多智能体系统来解决它")
    
    # 显示当前状态（调试用）
    st.sidebar.subheader("调试信息")
    st.sidebar.write(f"模板状态: {'已生成' if st.session_state.has_template else '未生成'}")
    if st.session_state.has_template:
        st.sidebar.write("模板名称:", st.session_state.template.get('template_name', '无名称'))
    st.sidebar.write(f"执行状态: {'已执行' if st.session_state.executed else '未执行'}")
    
    # 应用说明
    with st.expander("🔍 如何使用"):
        st.markdown("""
        **使用方法**:
        1. 在文本框中输入您想要解决的问题场景描述，可以包括背景、限制条件等
        2. 点击"生成模板"按钮，系统将:
           - 分析您的输入
           - 设计一个智能体系统
        3. 点击"执行模板"按钮，系统将:
           - 创建并执行智能体
           - 展示执行结果和分析
        
        **适合的场景示例**:
        - 旅行规划
        - 活动组织
        - 任务调度
        - 资源分配
        - 多步骤决策
        
        **提示**:
        - 提供详细的场景描述会获得更好的结果
        - 明确说明约束条件和考虑因素
        - 现实场景比抽象问题效果更好
        """)
    
    # 用户输入
    scenario = st.text_area(
        "描述你的场景、任务和约束条件", 
        height=200,
        placeholder="例如：我需要规划一次家庭聚会，有10个亲戚要来，其中有些人需要接送，活动包括准备食物、游戏和住宿安排。有些人是素食者，有些人对花生过敏..."
    )
    
    # 示例选择器
    st.subheader("或选择一个示例:")
    example_scenarios = {
        "家庭聚会规划": """
        我需要规划一次家庭聚会。有12个家庭成员要参加，包括4个小孩和2位老人。其中有3人是素食者，2人对坚果过敏。
        聚会将在我家举行，需要准备食物、饮料、游戏和座位安排。我有一个小厨房和一个可容纳15人的客厅。
        一些成员住得很远需要接送。聚会将持续6小时，从下午2点开始。
        我需要购买食材，准备餐点，安排活动，并确保所有人都能愉快地参与。
        """,
        
        "项目团队协作": """
        我们团队需要在3周内完成一个网站开发项目。团队包括2名前端开发、1名后端开发、1名UI设计师和1名项目经理。
        客户要求网站必须有响应式设计，包含用户认证系统、内容管理功能和支付集成。
        我们使用React和Node.js技术栈，采用敏捷开发方法，每周进行一次迭代。
        团队成员分布在不同时区，有些人只能兼职工作。我们需要协调任务分配、进度跟踪和质量控制。
        """,
        
        "旅行规划": """
        我计划与朋友一起进行为期7天的欧洲旅行，目的地包括巴黎、阿姆斯特丹和柏林。团队共5人，预算每人2000欧元。
        我们希望参观主要景点，体验当地美食，并有一些购物和夜生活活动。
        一位团队成员行动不便，需要考虑无障碍设施。另一位是素食者。
        我们需要规划交通方式、住宿选择、每日行程安排和预算分配。希望行程既充实又不过于匆忙，留有自由活动时间。
        """
    }
    
    example = st.selectbox("选择一个示例场景", ["无"] + list(example_scenarios.keys()))
    if example != "无":
        scenario = example_scenarios[example]
        st.text_area("示例场景", value=scenario, height=200, disabled=True)
    
    # 生成模板部分 - 将其拆分为两个按钮：生成模板和执行模板
    col1, col2 = st.columns(2)
    
    with col1:
        generate_button = st.button("1. 生成智能体模板", key="generate_template_button", use_container_width=True)
    
    with col2:
        # 完全独立的执行按钮，不使用disabled属性
        st.button("2. 执行智能体模板", key="execute_template_button", 
                                  use_container_width=True, 
                                  on_click=execute_agents)
    
    # 处理生成模板按钮
    if generate_button:
        if not scenario:
            st.error("请输入场景描述")
        else:
            # 生成模板
            with st.spinner("正在分析场景并生成智能体模板..."):
                template = generate_template(scenario)
                
            if not template:
                st.error("生成模板失败，请重试或修改输入")
            else:
                # 使用更新函数保存模板到session_state
                update_template(template)
                st.session_state.executed = False
                st.success("✅ 智能体模板生成成功! 现在您可以点击'执行智能体模板'按钮来运行它")
    
    # 如果模板已生成，显示模板详情
    if st.session_state.has_template and st.session_state.template is not None:
        template = st.session_state.template
        
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
    
    # 处理执行模板按钮
    if st.session_state.execute_clicked:
        # 重置点击状态
        st.session_state.execute_clicked = False
        
        # 检查是否有可用模板
        if not st.session_state.has_template or st.session_state.template is None:
            st.error("请先生成智能体模板")
        else:
            template = st.session_state.template
            
            with st.spinner("正在创建并执行智能体..."):
                try:
                    agents, agent_dict = create_agents_from_template(template)
                    results, saga = execute_template(agents)
                    
                    # 保存执行结果到session_state
                    st.session_state.execution_results = (results, saga, agents)
                    st.session_state.executed = True
                    
                    # 刷新页面显示结果
                    st.experimental_rerun()
                    
                except Exception as e:
                    st.error(f"执行过程中出错: {str(e)}")
                    st.code(traceback.format_exc())
    
    # 显示执行结果（如果已执行）
    if st.session_state.executed and st.session_state.execution_results is not None:
        results, saga, agents = st.session_state.execution_results
        
        # 显示执行结果
        st.subheader("🔍 执行结果")
        
        if results["success"]:
            st.success("✅ 智能体执行成功!")
        else:
            st.error(f"❌ 执行出错: {results.get('error', '未知错误')}")
        
        # 显示每个智能体的输出
        for agent in agents:
            with st.expander(f"{agent.name} 的输出", expanded=True):
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
        
        if agent_outputs:
            from openai import OpenAI
            client = OpenAI()
            
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
        else:
            st.warning("所有智能体执行失败，无法生成总结")

if __name__ == "__main__":
    main() 