import os
import sys
import gradio as gr
from dotenv import load_dotenv
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Set correct import path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add current directory to path for direct import from src
sys.path.insert(0, current_dir)

# Import necessary modules
from src.multi_agent.saga import Saga
from src.multi_agent.agent import Agent

load_dotenv()

class SagaLLMInterface:
    """Gradio interface management class for SagaLLM"""
    
    def __init__(self):
        self.saga = Saga()
        self.agents = []
        self.agent_names = []
        self.execution_log = []
        self.current_status = "Ready"
    
    def add_agent(self, name, backstory, task_description, expected_output):
        """Add a new Agent"""
        if name in self.agent_names:
            return f"❌ Agent '{name}' already exists"
        
        try:
            new_agent = Agent(
                name=name,
                backstory=backstory,
                task_description=task_description,
                task_expected_output=expected_output
            )
            self.agents.append(new_agent)
            self.agent_names.append(name)
            return f"✅ Agent '{name}' created successfully"
        except Exception as e:
            return f"❌ Failed to create Agent: {str(e)}"
    
    def add_dependency(self, agent_name, dependency_name):
        """Add dependency relationship between Agents"""
        if agent_name not in self.agent_names or dependency_name not in self.agent_names:
            return f"❌ Agent name does not exist"
        
        agent = next((a for a in self.agents if a.name == agent_name), None)
        dependency = next((a for a in self.agents if a.name == dependency_name), None)
        
        try:
            agent.add_dependency(dependency)
            return f"✅ Dependency added: {dependency_name} → {agent_name}"
        except Exception as e:
            return f"❌ Failed to add dependency: {str(e)}"
    
    def visualize_agents(self):
        """Create and return visualization of Agent dependencies"""
        G = nx.DiGraph()
        
        # Add nodes
        for agent in self.agents:
            G.add_node(agent.name)
        
        # Add edges
        for agent in self.agents:
            for dep in agent.dependencies:
                G.add_edge(dep.name, agent.name)
        
        # Create image using matplotlib
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, arrowsize=20, font_size=10,
                font_weight='bold', arrows=True)
        
        # Convert image to base64 encoding
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{img_str}"
    
    def run_saga(self, with_rollback=True):
        """Execute Saga coordinator and return logs"""
        try:
            self.execution_log = []
            self.current_status = "Executing"
            
            # Create custom logging callback function
            def log_callback(message):
                self.execution_log.append(message)
            
            # Register Agents and execute
            self.saga.transaction_manager(self.agents)
            
            # We need to modify Saga code to support callback functions
            # For the example, we assume some logs will be generated after execution
            self.saga.saga_coordinator(with_rollback=with_rollback)
            
            self.current_status = "Completed"
            return "\n".join(self.execution_log) or "Execution completed, but no logs were generated"
        except Exception as e:
            self.current_status = "Execution error"
            return f"❌ Error during execution: {str(e)}"
    
    def view_context(self, agent_name):
        """View context for a specific Agent"""
        if agent_name not in self.agent_names:
            return "Agent not found"
        
        try:
            if agent_name in self.saga.context:
                return self.saga.context[agent_name]
            else:
                return f"Agent '{agent_name}' has no execution context"
        except Exception as e:
            return f"Error retrieving context: {str(e)}"
    
    def rollback_agent(self, agent_name):
        """Rollback execution for a specific Agent"""
        if agent_name not in self.agent_names:
            return "Agent not found"
        
        try:
            self.saga.restore_context(agent_name)
            return f"Successfully rolled back Agent '{agent_name}'"
        except Exception as e:
            return f"Error during rollback: {str(e)}"

def create_interface():
    """Create Gradio interface"""
    saga_interface = SagaLLMInterface()
    
    with gr.Blocks(title="SagaLLM Interactive Interface") as interface:
        gr.Markdown("# SagaLLM Multi-Agent System")
        gr.Markdown("## Configure Agents")
        
        with gr.Tab("Create Agent"):
            with gr.Row():
                with gr.Column():
                    agent_name = gr.Textbox(label="Agent Name")
                    agent_backstory = gr.Textbox(label="Background Description", lines=3)
                    agent_task = gr.Textbox(label="Task Description", lines=3)
                    agent_output = gr.Textbox(label="Expected Output", lines=3)
                    add_agent_btn = gr.Button("Add Agent")
                
                with gr.Column():
                    agent_status = gr.Textbox(label="Status", interactive=False)
                    agent_list = gr.Dropdown(label="Created Agents", choices=saga_interface.agent_names, interactive=True)
        
        with gr.Tab("Configure Dependencies"):
            with gr.Row():
                with gr.Column():
                    source_agent = gr.Dropdown(label="Source Agent", choices=saga_interface.agent_names)
                    target_agent = gr.Dropdown(label="Target Agent", choices=saga_interface.agent_names)
                    add_dep_btn = gr.Button("Add Dependency")
                
                with gr.Column():
                    dep_status = gr.Textbox(label="Dependency Status", interactive=False)
        
        with gr.Tab("Visualization"):
            vis_btn = gr.Button("Generate Relationship Graph")
            vis_output = gr.Image(label="Dependency Graph")
        
        with gr.Tab("Execute"):
            with gr.Row():
                with gr.Column():
                    rollback_checkbox = gr.Checkbox(label="Enable Rollback", value=True)
                    run_btn = gr.Button("Execute Task")
                    status_label = gr.Label(label="Current Status", value=saga_interface.current_status)
                
                with gr.Column():
                    log_output = gr.Textbox(label="Execution Log", interactive=False, lines=10)
        
        with gr.Tab("Check Results"):
            with gr.Row():
                with gr.Column():
                    context_agent = gr.Dropdown(label="Select Agent", choices=saga_interface.agent_names)
                    context_btn = gr.Button("View Context")
                    rollback_btn = gr.Button("Rollback Agent")
                
                with gr.Column():
                    context_output = gr.Textbox(label="Context Content", interactive=False, lines=10)
        
        # Event handling
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