# **SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning**



## Demo Video
[![SagaLLM Demo Video](https://img.youtube.com/vi/FtVVQzks0xk/0.jpg)](https://youtu.be/AvqI6EkNetM?si=p1L85l04bCjw2MLf "SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning")

This repository extends based on the REALM-Bench (a general mutli-agent framework for of real-world use cases of Multi Agentic Design, Orchestration, and Planning in Real-World Scenerios).
The SagaLLM provides a **comprehensive middleware** for agent application layer and multi-agent databases.

  
1. It supports **Application Layer** for:
    - **Planning and Scheduling:** 1) Sequential planning, 2) Reactive planning, 3) Complex planning, 4) Others
   - **Reflection**
   - **Memory**
   - **Reasoning**
   - **Forecasting**
   - **Math Induction, Calculation**
   - **Multi-Agent Collaboration**: workflow generation

2. It supports **Multi-Agent Database Frameworks** across different agent ecosystems:  
   - **AutoGen**  
   - **CrewAI**  
   - **Swarm**  
   - **LangGraph**  

## **🌟 New Feature: SagaLLM Interactive Web Application**

We've implemented a Streamlit-based web application that allows you to interact with SagaLLM's multi-agent systems through a graphical interface. This application enables:

1. **Multi-Agent Template Generation**: Transform your scenarios into intelligent agent workflows
2. **Agent Execution Visualization**: Watch as multiple specialized agents collaborate on your tasks
3. **Real-time Execution Monitoring**: Track the progress and output of each agent
4. **Detailed Planning Analysis**: Get comprehensive results including timelines and recommendations

The web application includes full functionality for complex scenarios like wedding logistics planning, project coordination, travel arrangements, and more.

### **Running the Web Application**
To launch the interactive web application:
```bash
cd applications
streamlit run streamlit_frontend.py
```

The interface provides:
- Scenario input area for your specific requirements
- Pre-configured example scenarios to explore system capabilities
- Graphical visualization of agent dependencies and workflows
- Detailed execution results with comprehensive scheduling information

## **Key Functions of `Saga` libraries**

- 1) Context Management Framework
- 2) Validation Framework
- 3) Transaction Framework
- 4) Extension of multi-agent frameworks,
- 5) Built for application layers.
     

| **Function**            | **Description**                                      | **Function Name**                      | **Input**                                      |
|-------------------------|------------------------------------------------------|-----------------------------------------|------------------------------------------------|
| **Transaction Manager** | Defines context, agents, and dependencies.          | `transaction_manager(self, agents, dependencies, context)` | List of agents, dependencies, and context.   |
| **Saga Coordinator**    | Executes agents with optional rollback support.     | `saga_coordinator(self, with_rollback, agents)` | `with_rollback` (boolean flag), agent list.  |
| **Intra-Agent Details** | Prints each agent's execution details.              | `intra_agent(self, agents)`            | Agent list.                                   |
| **Inter-Agent Dependencies** | Displays inter-agent dependencies.          | `inter_agent(self, dependency_graph)`  | Agent dependency graph.                      |
| **Select Context**      | Allows user to query execution context of a node.   | `select_context(self, node_name)`       | User-input node name.                         |
| **Restore Context**     | Rolls back execution of a specified agent.          | `restore_context(self, agent_name)`     | User-input agent to rollback.                |

![SagaLLM Functions](img/saga_functions.png)
---

