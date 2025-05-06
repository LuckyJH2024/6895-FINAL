#!/usr/bin/env python3
"""
SagaLLM模板演示应用（中文版）
无论用户输入什么，都使用预先定义好的中文模板来运行多智能体系统
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

# 预定义的演示模板（中文版）
DEMO_TEMPLATE = {
    "template_name": "婚礼日程物流管理系统",
    "description": "一个多智能体系统，用于管理和优化婚礼日的物流安排，确保宾客接送、服装准备、礼品管理和摄影等环节顺利进行。",
    "agents": [
        {
            "name": "机场接机智能体",
            "backstory": "你负责从机场接送宾客并将他们送到婚礼场地。需要考虑航班到达时间、宾客数量和可用车辆。",
            "task_description": "创建一个详细的机场接机时间表，考虑航班到达时间、宾客数量和可用车辆，确保所有宾客都能顺利到达婚礼场地。",
            "task_expected_output": "<response>\n  <接机安排>\n    <时间>上午10:00</时间>\n    <宾客>李家（4人）</宾客>\n    <航班>CA1234</航班>\n    <车辆>SUV</车辆>\n  </接机安排>\n  <接机安排>\n    <时间>上午11:30</时间>\n    <宾客>王家（3人）</宾客>\n    <航班>MU5678</航班>\n    <车辆>轿车</车辆>\n  </接机安排>\n</response>"
        },
        {
            "name": "场地接待智能体",
            "backstory": "你管理宾客在婚礼场地的到达流程，确保顺利过渡和适当的住宿安排。",
            "task_description": "为到达场地的宾客组织接待计划，包括登记程序、欢迎礼包和房间分配。",
            "task_expected_output": "<response>\n  <场地接待>\n    <登记流程>登记流程的详细步骤</登记流程>\n    <欢迎礼包>欢迎礼包中的物品清单</欢迎礼包>\n    <住宿安排>宾客的房间分配</住宿安排>\n  </场地接待>\n</response>"
        },
        {
            "name": "婚礼服装智能体",
            "backstory": "你负责收集和分发婚礼参与者的服装。",
            "task_description": "创建一个系统，用于从店铺/设计师处收集婚礼服装，并将其分发给婚礼参与人员。",
            "task_expected_output": "<response>\n  <服装收集>\n    <店铺取件>店铺列表和取件时间</店铺取件>\n    <分发计划>向婚礼参与者分发服装的计划</分发计划>\n    <试衣安排>最终试衣的时间安排</试衣安排>\n  </服装收集>\n</response>"
        },
        {
            "name": "礼品管理智能体",
            "backstory": "你负责收集、整理和保管宾客带来的婚礼礼品。",
            "task_description": "开发一个系统，用于在婚礼场地接收、记录和安全存放婚礼礼品。",
            "task_expected_output": "<response>\n  <礼品管理>\n    <收集流程>收集礼品的流程</收集流程>\n    <记录系统>记录礼品信息的系统</记录系统>\n    <存放方案>礼品的安全存放方案</存放方案>\n  </礼品管理>\n</response>"
        },
        {
            "name": "婚礼摄影智能体",
            "backstory": "你是婚礼摄影环节的协调者，确保所有重要时刻都被捕捉到。",
            "task_description": "创建一个详细的摄影环节时间表，包括婚礼前拍摄、仪式照片和接待处的覆盖范围。",
            "task_expected_output": "<response>\n  <摄影安排>\n    <仪式前>婚礼前照片的安排</仪式前>\n    <仪式中>仪式摄影计划</仪式中>\n    <接待处>接待处照片覆盖时间表</接待处>\n    <特殊时刻>必须捕捉的时刻列表</特殊时刻>\n  </摄影安排>\n</response>"
        }
    ],
    "dependencies": [
        {"from": "机场接机智能体", "to": "场地接待智能体"},
        {"from": "场地接待智能体", "to": "机场接机智能体"},
        {"from": "机场接机智能体", "to": "婚礼服装智能体"},
        {"from": "婚礼服装智能体", "to": "礼品管理智能体"},
        {"from": "礼品管理智能体", "to": "场地接待智能体"},
        {"from": "场地接待智能体", "to": "婚礼摄影智能体"}
    ]
}

def execute_agents():
    """执行模板函数"""
    st.session_state.execute_clicked = True
    print("🚀 执行按钮被点击")

def main():
    """主函数 - Streamlit应用入口点"""
    st.set_page_config(page_title="SagaLLM婚礼规划演示", page_icon="💍", layout="wide")
    
    # 初始化session_state以存储模板和执行状态
    if 'executed' not in st.session_state:
        st.session_state.executed = False
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = None
    if 'execute_clicked' not in st.session_state:
        st.session_state.execute_clicked = False
    
    st.title("💍 婚礼日程智能规划系统")
    st.write("这是一个婚礼日程规划的智能多智能体系统演示")
    
    # 虚拟用户输入（仅用于演示，实际不影响结果）
    scenario = st.text_area(
        "描述你的婚礼计划和需求", 
        height=150,
        placeholder="请描述您的婚礼计划，包括日期、地点、宾客人数、特殊需求等..."
    )
    
    # 直接显示预定义模板详情
    st.subheader("📋 婚礼日程规划系统")
    
    # 显示模板详情
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**名称**: {DEMO_TEMPLATE['template_name']}")
        st.write(f"**描述**: {DEMO_TEMPLATE['description']}")
        
        st.write("**智能体**:")
        for idx, agent in enumerate(DEMO_TEMPLATE["agents"]):
            with st.expander(f"{idx+1}. {agent['name']}"):
                st.write(f"**背景**: {agent['backstory']}")
                st.write(f"**任务**: {agent['task_description']}")
                st.write("**预期输出**:")
                st.code(agent.get('task_expected_output', ''), language="xml")
    
    with col2:
        st.write("**依赖关系**:")
        for dep in DEMO_TEMPLATE["dependencies"]:
            st.write(f"- {dep['from']} → {dep['to']}")
        
        # 可视化依赖关系
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            
            G = nx.DiGraph()
            for agent in DEMO_TEMPLATE["agents"]:
                G.add_node(agent["name"])
            
            for dep in DEMO_TEMPLATE["dependencies"]:
                G.add_edge(dep["from"], dep["to"])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, node_color='skyblue', 
                    node_size=2000, arrowsize=20, font_size=10,
                    font_weight='bold', arrows=True, ax=ax)
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"无法绘制依赖关系图: {e}")
    
    # 执行按钮 - 置于画面中央并加大
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    
    if st.button("💫 执行智能体系统", key="execute_button", use_container_width=True, 
                on_click=execute_agents):
        pass  # 使用on_click回调处理点击事件
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 处理执行模板按钮
    if st.session_state.execute_clicked:
        # 重置点击状态
        st.session_state.execute_clicked = False
        
        with st.spinner("🔮 正在创建并执行智能体系统..."):
            try:
                # 直接使用预定义模板
                agents, agent_dict = create_agents_from_template(DEMO_TEMPLATE)
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
        st.subheader("🔍 婚礼规划方案")
        
        if results["success"]:
            st.success("✅ 婚礼规划系统执行成功!")
        else:
            st.error(f"❌ 执行出错: {results.get('error', '未知错误')}")
        
        # 显示每个智能体的输出
        for agent in agents:
            with st.expander(f"{agent.name} 的规划方案", expanded=True):
                if agent.name in saga.context:
                    st.code(saga.context[agent.name], language="xml")
                else:
                    st.warning("该智能体未执行或执行失败")
        
        # 显示总体结论
        st.subheader("📊 婚礼规划总结")
        
        # 从结果中提取关键信息生成总结
        agent_outputs = []
        for agent in agents:
            if agent.name in saga.context:
                agent_outputs.append(f"{agent.name}: {saga.context[agent.name][:200]}...")
        
        if agent_outputs:
            from openai import OpenAI
            client = OpenAI()
            
            summary_prompt = f"""
根据以下多智能体系统的执行结果，为新人提供一个婚礼规划的总结和建议。

各智能体的输出:
{agent_outputs}

请用中文提供一个简明的总结，解释这个婚礼规划系统如何协调各个方面的工作，以及给新人的关键建议。务必使用中文回答。
"""
            
            with st.spinner("正在生成婚礼规划总结..."):
                summary_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=0.7,
                )
                summary = summary_response.choices[0].message.content
            
            st.write(summary)
        else:
            st.warning("无法生成婚礼规划总结")

if __name__ == "__main__":
    main() 