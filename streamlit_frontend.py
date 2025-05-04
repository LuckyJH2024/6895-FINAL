import os
import sys
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 设置正确的导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到路径，以便可以直接导入src
sys.path.insert(0, current_dir)

# 导入必要的模块
from src.multi_agent.saga import Saga
from src.multi_agent.agent import Agent
from agent_templates import get_templates, get_template_description, get_template

load_dotenv()

# 初始化session_state
if 'saga' not in st.session_state:
    st.session_state.saga = Saga()
if 'agents' not in st.session_state:
    st.session_state.agents = []
if 'agent_names' not in st.session_state:
    st.session_state.agent_names = []
if 'execution_log' not in st.session_state:
    st.session_state.execution_log = []
if 'current_status' not in st.session_state:
    st.session_state.current_status = "就绪"
if 'context' not in st.session_state:
    st.session_state.context = {}

# 页面标题
st.title("SagaLLM多智能体系统")

# 侧边栏导航
page = st.sidebar.selectbox(
    "导航", 
    ["创建智能体", "从模板创建", "配置依赖关系", "可视化", "执行", "检查结果"]
)

def add_agent(name, backstory, task_description, expected_output):
    """添加一个新的Agent"""
    if name in st.session_state.agent_names:
        return f"❌ Agent '{name}' 已存在"
    
    try:
        new_agent = Agent(
            name=name,
            backstory=backstory,
            task_description=task_description,
            task_expected_output=expected_output
        )
        st.session_state.agents.append(new_agent)
        st.session_state.agent_names.append(name)
        return f"✅ Agent '{name}' 已创建成功"
    except Exception as e:
        return f"❌ 创建Agent失败: {str(e)}"

def add_dependency(agent_name, dependency_name):
    """添加Agent之间的依赖关系"""
    if agent_name not in st.session_state.agent_names or dependency_name not in st.session_state.agent_names:
        return f"❌ Agent名称不存在"
    
    agent = next((a for a in st.session_state.agents if a.name == agent_name), None)
    dependency = next((a for a in st.session_state.agents if a.name == dependency_name), None)
    
    try:
        agent.add_dependency(dependency)
        return f"✅ 依赖关系已添加: {dependency_name} → {agent_name}"
    except Exception as e:
        return f"❌ 添加依赖关系失败: {str(e)}"

def create_from_template(template_name):
    """从模板创建一组Agent和依赖关系"""
    template_data = get_template(template_name)
    if not template_data:
        return f"❌ 模板 '{template_name}' 不存在"
    
    # 清空现有智能体
    st.session_state.agents = []
    st.session_state.agent_names = []
    
    # 创建智能体
    for agent_data in template_data["agents"]:
        add_agent(
            agent_data["name"],
            agent_data["backstory"],
            agent_data["task_description"],
            agent_data["task_expected_output"]
        )
    
    # 建立依赖关系
    for dep in template_data["dependencies"]:
        add_dependency(dep["to"], dep["from"])
    
    return f"✅ 已成功从模板 '{template_name}' 创建 {len(template_data['agents'])} 个智能体"

def visualize_agents():
    """创建并绘制Agent依赖关系的可视化图"""
    if not st.session_state.agents:
        st.warning("没有可视化的智能体，请先创建智能体。")
        return
    
    G = nx.DiGraph()
    
    # 添加节点
    for agent in st.session_state.agents:
        G.add_node(agent.name)
    
    # 添加边
    for agent in st.session_state.agents:
        for dep in agent.dependencies:
            G.add_edge(dep.name, agent.name)
    
    # 使用matplotlib创建图像
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, seed=42)  # 使用固定的随机种子确保布局一致性
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, arrowsize=20, font_size=10,
            font_weight='bold', arrows=True, ax=ax)
    
    return fig

def run_saga(with_rollback=True):
    """执行Saga协调器并返回日志"""
    if not st.session_state.agents:
        return "❌ 没有要执行的智能体，请先创建智能体。"
    
    try:
        st.session_state.execution_log = []
        st.session_state.current_status = "执行中"
        
        # 注册Agent并执行
        st.session_state.saga.transaction_manager(st.session_state.agents)
        st.session_state.saga.saga_coordinator(with_rollback=with_rollback)
        
        # 获取执行结果
        st.session_state.context = st.session_state.saga.context
        st.session_state.current_status = "已完成"
        
        # 日志处理
        log = []
        for agent in st.session_state.agents:
            if agent.name in st.session_state.context:
                log.append(f"✅ {agent.name}: 执行成功")
            else:
                log.append(f"❌ {agent.name}: 未执行或执行失败")
        
        return "\n".join(log)
    except Exception as e:
        st.session_state.current_status = "执行出错"
        return f"❌ 执行过程中出错: {str(e)}"

def view_context(agent_name):
    """查看特定Agent的上下文"""
    if agent_name not in st.session_state.agent_names:
        return "未找到该Agent"
    
    try:
        if agent_name in st.session_state.context:
            return st.session_state.context[agent_name]
        else:
            return f"Agent '{agent_name}' 没有执行上下文"
    except Exception as e:
        return f"获取上下文出错: {str(e)}"

def rollback_agent(agent_name):
    """回滚特定Agent的执行"""
    if agent_name not in st.session_state.agent_names:
        return "未找到该Agent"
    
    try:
        st.session_state.saga.restore_context(agent_name)
        # 更新本地缓存的上下文
        st.session_state.context = st.session_state.saga.context
        return f"已成功回滚Agent '{agent_name}'"
    except Exception as e:
        return f"回滚过程中出错: {str(e)}"

def clear_all_agents():
    """清空所有智能体"""
    st.session_state.agents = []
    st.session_state.agent_names = []
    st.session_state.context = {}
    st.session_state.execution_log = []
    return "已清空所有智能体"

# 根据选择的页面显示不同的内容
if page == "创建智能体":
    st.header("创建新的智能体")
    
    col1, col2 = st.columns(2)
    
    with col1:
        agent_name = st.text_input("智能体名称")
        agent_backstory = st.text_area("背景描述", height=100)
        agent_task = st.text_area("任务描述", height=100)
        agent_output = st.text_area("预期输出", height=100)
        
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("添加智能体"):
                result = add_agent(agent_name, agent_backstory, agent_task, agent_output)
                st.success(result) if "✅" in result else st.error(result)
        
        with col1b:
            if st.button("清空所有智能体"):
                result = clear_all_agents()
                st.success(result)
    
    with col2:
        st.subheader("已创建的智能体")
        if st.session_state.agents:
            for agent in st.session_state.agents:
                with st.expander(agent.name):
                    st.write(f"**背景:** {agent.backstory}")
                    st.write(f"**任务:** {agent.task_description}")
                    st.write(f"**预期输出:** {agent.task_expected_output}")
        else:
            st.info("还没有创建任何智能体")

elif page == "从模板创建":
    st.header("从模板创建智能体组")
    
    templates = get_templates()
    selected_template = st.selectbox("选择模板", templates)
    
    with st.expander("模板描述"):
        st.write(get_template_description(selected_template))
    
    if st.button("使用此模板"):
        result = create_from_template(selected_template)
        st.success(result) if "✅" in result else st.error(result)
    
    # 如果已有智能体，显示当前智能体列表
    if st.session_state.agents:
        st.subheader(f"已创建 {len(st.session_state.agents)} 个智能体")
        for agent in st.session_state.agents:
            with st.expander(agent.name):
                st.write(f"**背景:** {agent.backstory}")
                st.write(f"**任务:** {agent.task_description}")

elif page == "配置依赖关系":
    st.header("配置智能体依赖关系")
    
    if not st.session_state.agent_names:
        st.warning("请先创建智能体")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            source_agent = st.selectbox("源智能体（上游）", st.session_state.agent_names)
            target_agent = st.selectbox("目标智能体（下游）", st.session_state.agent_names)
            
            if st.button("添加依赖关系"):
                result = add_dependency(target_agent, source_agent)
                st.success(result) if "✅" in result else st.error(result)
        
        with col2:
            st.subheader("现有依赖关系")
            for agent in st.session_state.agents:
                deps = [dep.name for dep in agent.dependencies]
                if deps:
                    st.write(f"**{agent.name}** 依赖于: {', '.join(deps)}")

elif page == "可视化":
    st.header("智能体依赖关系可视化")
    
    fig = visualize_agents()
    if fig:
        st.pyplot(fig)

elif page == "执行":
    st.header("执行Saga任务流")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with_rollback = st.checkbox("启用回滚", value=True)
        st.write(f"**当前状态:** {st.session_state.current_status}")
        
        if st.button("执行任务"):
            with st.spinner("正在执行..."):
                result = run_saga(with_rollback)
                st.code(result)
    
    with col2:
        if st.session_state.current_status == "已完成":
            st.subheader("执行结果摘要")
            st.write(f"共执行智能体: {len(st.session_state.context)} 个")
            st.progress(len(st.session_state.context) / len(st.session_state.agents))

elif page == "检查结果":
    st.header("检查和管理执行结果")
    
    if not st.session_state.context:
        st.warning("还没有执行结果，请先执行任务")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            context_agent = st.selectbox("选择智能体", st.session_state.agent_names)
            col1a, col1b = st.columns(2)
            
            with col1a:
                if st.button("查看上下文"):
                    result = view_context(context_agent)
                    st.session_state.selected_context = result
            
            with col1b:
                if st.button("回滚智能体"):
                    result = rollback_agent(context_agent)
                    st.success(result) if "成功" in result else st.error(result)
        
        with col2:
            st.subheader("上下文内容")
            if 'selected_context' in st.session_state:
                st.code(st.session_state.selected_context)

# 显示当前版本和状态信息
st.sidebar.markdown("---")
st.sidebar.info(f"当前状态: {st.session_state.current_status}")
st.sidebar.info(f"智能体数量: {len(st.session_state.agents)}")
st.sidebar.info("SagaLLM 演示版") 