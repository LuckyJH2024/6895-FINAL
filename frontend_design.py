import os
import sys
import gradio as gr
from dotenv import load_dotenv
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# 设置正确的导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到路径，以便可以直接导入src
sys.path.insert(0, current_dir)

# 导入必要的模块
from src.multi_agent.saga import Saga
from src.multi_agent.agent import Agent

load_dotenv()

class SagaLLMInterface:
    """SagaLLM的Gradio界面管理类"""
    
    def __init__(self):
        self.saga = Saga()
        self.agents = []
        self.agent_names = []
        self.execution_log = []
        self.current_status = "就绪"
    
    def add_agent(self, name, backstory, task_description, expected_output):
        """添加一个新的Agent"""
        if name in self.agent_names:
            return f"❌ Agent '{name}' 已存在"
        
        try:
            new_agent = Agent(
                name=name,
                backstory=backstory,
                task_description=task_description,
                task_expected_output=expected_output
            )
            self.agents.append(new_agent)
            self.agent_names.append(name)
            return f"✅ Agent '{name}' 已创建成功"
        except Exception as e:
            return f"❌ 创建Agent失败: {str(e)}"
    
    def add_dependency(self, agent_name, dependency_name):
        """添加Agent之间的依赖关系"""
        if agent_name not in self.agent_names or dependency_name not in self.agent_names:
            return f"❌ Agent名称不存在"
        
        agent = next((a for a in self.agents if a.name == agent_name), None)
        dependency = next((a for a in self.agents if a.name == dependency_name), None)
        
        try:
            agent.add_dependency(dependency)
            return f"✅ 依赖关系已添加: {dependency_name} → {agent_name}"
        except Exception as e:
            return f"❌ 添加依赖关系失败: {str(e)}"
    
    def visualize_agents(self):
        """创建并返回Agent依赖关系的可视化图"""
        G = nx.DiGraph()
        
        # 添加节点
        for agent in self.agents:
            G.add_node(agent.name)
        
        # 添加边
        for agent in self.agents:
            for dep in agent.dependencies:
                G.add_edge(dep.name, agent.name)
        
        # 使用matplotlib创建图像
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, arrowsize=20, font_size=10,
                font_weight='bold', arrows=True)
        
        # 将图像转换为base64编码
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def run_saga(self, with_rollback=True):
        """执行Saga协调器并返回日志"""
        try:
            self.execution_log = []
            self.current_status = "执行中"
            
            # 创建自定义日志记录函数
            def log_callback(message):
                self.execution_log.append(message)
            
            # 注册Agent并执行
            self.saga.transaction_manager(self.agents)
            
            # 这里需要修改Saga代码以支持回调函数
            # 为了示例，我们假设执行后会产生一些日志
            self.saga.saga_coordinator(with_rollback=with_rollback)
            
            self.current_status = "已完成"
            return "\n".join(self.execution_log) or "执行已完成，但没有产生日志"
        except Exception as e:
            self.current_status = "执行出错"
            return f"❌ 执行过程中出错: {str(e)}"
    
    def view_context(self, agent_name):
        """查看特定Agent的上下文"""
        if agent_name not in self.agent_names:
            return "未找到该Agent"
        
        try:
            if agent_name in self.saga.context:
                return self.saga.context[agent_name]
            else:
                return f"Agent '{agent_name}' 没有执行上下文"
        except Exception as e:
            return f"获取上下文出错: {str(e)}"
    
    def rollback_agent(self, agent_name):
        """回滚特定Agent的执行"""
        if agent_name not in self.agent_names:
            return "未找到该Agent"
        
        try:
            self.saga.restore_context(agent_name)
            return f"已成功回滚Agent '{agent_name}'"
        except Exception as e:
            return f"回滚过程中出错: {str(e)}"

def create_interface():
    """创建Gradio界面"""
    saga_interface = SagaLLMInterface()
    
    with gr.Blocks(title="SagaLLM交互界面") as interface:
        gr.Markdown("# SagaLLM多智能体系统")
        gr.Markdown("## 配置智能体")
        
        with gr.Tab("创建智能体"):
            with gr.Row():
                with gr.Column():
                    agent_name = gr.Textbox(label="智能体名称")
                    agent_backstory = gr.Textbox(label="背景描述", lines=3)
                    agent_task = gr.Textbox(label="任务描述", lines=3)
                    agent_output = gr.Textbox(label="预期输出", lines=3)
                    add_agent_btn = gr.Button("添加智能体")
                
                with gr.Column():
                    agent_status = gr.Textbox(label="状态", interactive=False)
                    agent_list = gr.Dropdown(label="已创建的智能体", choices=saga_interface.agent_names, interactive=True)
        
        with gr.Tab("配置依赖关系"):
            with gr.Row():
                with gr.Column():
                    source_agent = gr.Dropdown(label="源智能体", choices=saga_interface.agent_names)
                    target_agent = gr.Dropdown(label="目标智能体", choices=saga_interface.agent_names)
                    add_dep_btn = gr.Button("添加依赖")
                
                with gr.Column():
                    dep_status = gr.Textbox(label="依赖状态", interactive=False)
        
        with gr.Tab("可视化"):
            vis_btn = gr.Button("生成关系图")
            vis_output = gr.Image(label="依赖关系图")
        
        with gr.Tab("执行"):
            with gr.Row():
                with gr.Column():
                    rollback_checkbox = gr.Checkbox(label="启用回滚", value=True)
                    run_btn = gr.Button("执行任务")
                    status_label = gr.Label(label="当前状态", value=saga_interface.current_status)
                
                with gr.Column():
                    log_output = gr.Textbox(label="执行日志", interactive=False, lines=10)
        
        with gr.Tab("检查结果"):
            with gr.Row():
                with gr.Column():
                    context_agent = gr.Dropdown(label="选择智能体", choices=saga_interface.agent_names)
                    context_btn = gr.Button("查看上下文")
                    rollback_btn = gr.Button("回滚智能体")
                
                with gr.Column():
                    context_output = gr.Textbox(label="上下文内容", interactive=False, lines=10)
        
        # 事件处理
        add_agent_btn.click(
            fn=saga_interface.add_agent,
            inputs=[agent_name, agent_backstory, agent_task, agent_output],
            outputs=[agent_status]
        ).then(
            fn=lambda: saga_interface.agent_names,
            inputs=None,
            outputs=[agent_list, source_agent, target_agent, context_agent]
        )
        
        add_dep_btn.click(
            fn=saga_interface.add_dependency,
            inputs=[target_agent, source_agent],
            outputs=[dep_status]
        )
        
        vis_btn.click(
            fn=saga_interface.visualize_agents,
            inputs=None,
            outputs=[vis_output]
        )
        
        run_btn.click(
            fn=saga_interface.run_saga,
            inputs=[rollback_checkbox],
            outputs=[log_output]
        ).then(
            fn=lambda: saga_interface.current_status,
            inputs=None,
            outputs=[status_label]
        )
        
        context_btn.click(
            fn=saga_interface.view_context,
            inputs=[context_agent],
            outputs=[context_output]
        )
        
        rollback_btn.click(
            fn=saga_interface.rollback_agent,
            inputs=[context_agent],
            outputs=[context_output]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True) 