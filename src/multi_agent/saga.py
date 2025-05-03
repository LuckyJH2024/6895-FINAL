from collections import deque
from colorama import Fore
from graphviz import Digraph  # type: ignore
from utils.validation import detect_conflict_across_agents
from utils.logging import custom_print
# from src.utils.logging import custom_print

import sys
import os

# Get the project root by going up one level from 'applications'
project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
print(f"📂 Project Root: {project_root}")

# Append 'src' directory to sys.path
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

# Print sys.path to verify
print("🔍 Updated sys.path:")
for path in sys.path:
    print(path)

# Try importing Saga again
try:
    from utils.logging import custom_print
    print("✅ Utils imported successfully!")
except ModuleNotFoundError as e:
    print("❌ Import failed:", e)

class Saga:
    """
    Saga framework managing transaction flows, inter-agent dependencies, and rollback mechanisms.

    Key Functions:
    1) `transaction_manager` - Initializes agents, sets dependencies.
    2) `saga_coordinator` - Runs agents with or without rollback.
    3) `intra_agent` - Prints intra-agent details.
    4) `inter_agent` - Prints inter-agent relationships.
    5) `select_context` - User input node and context display.
    6) `restore_context` - Rolls back a selected node.

    Attributes:
        agents (list): List of all registered agents.
        context (dict): Stores execution context per agent.
    """

    def __init__(self):
        self.agents = []
        self.context = {}

    def transaction_manager(self, agents):
        self.agents = agents
        custom_print("🛠 Transaction Manager: Agents and dependencies initialized.")

    def saga_coordinator(self, with_rollback=True):
        sorted_agents = self.topological_sort()
        executed_agents = []

        try:
            for agent in sorted_agents:
                custom_print(f"🚀 Running Agent: {agent.name}")
                # Aggregate contexts from dependencies
                agent.context = "".join([
                    self.context[dep.name]
                    for dep in agent.dependencies if dep.name in self.context
                ])

                # Run agent, catch risk prediction if returned in tuple
                result = agent.run()

                # ✅ 处理可能返回风险结构（要求 agent.run() 返回 dict 或 tuple）
                if isinstance(result, dict) and "risk" in result:
                    risk = result["risk"]
                    reason = result.get("reason", "No reason provided.")
                    if risk == "HIGH":
                        print(Fore.YELLOW + f"⚠️ {agent.name} skipped due to HIGH risk: {reason}")
                        self.context[agent.name] = (
                            f"<response><status>skipped</status><reason>{reason}</reason></response>"
                        )
                        continue  # ✅ skip execution, don't append to executed_agents

                    result = result.get("content", "")  # ✅ continue with content if not high risk

                self.context[agent.name] = result
                executed_agents.append(agent)
                print(Fore.GREEN + f"✅ {agent.name} completed successfully.")

            if executed_agents:
                conflict_report = detect_conflict_across_agents(self.context)
                print(f"⚠️ Conflict Report: {conflict_report}")
                if "Conflict Detected" in conflict_report:
                    raise RuntimeError(f"Conflict found: {conflict_report}")

        except Exception as e:
            print(Fore.RED + f"❌ ERROR in {agent.name}: {str(e)}")

            if with_rollback:
                print(Fore.YELLOW + "🔄 Rolling back executed agents...")
                for completed_agent in reversed(executed_agents):
                    try:
                        completed_agent.rollback()
                        print(Fore.BLUE + f"↩️ Rolled back: {completed_agent.name}")
                    except AttributeError:
                        print(Fore.RED + f"⚠️ {completed_agent.name} has no rollback method.")
                    except Exception as rollback_error:
                        print(Fore.RED + f"⚠️ Error rolling back {completed_agent.name}: {rollback_error}")

            print(Fore.RED + "🚨 Execution halted due to error.")


    def intra_agent(self):
        print("\n📌 **Intra-Agent Execution Details**")
        for agent in self.agents:
            print(f"🔹 {agent.name}: {self.context.get(agent.name, 'Not executed')}")

    def inter_agent(self):
        print("\n🔗 **Inter-Agent Dependencies**")
        for agent in self.agents:
            dep_names = [dep.name for dep in agent.dependencies]
            print(f"🔸 {agent.name} depends on: {', '.join(dep_names) if dep_names else 'None'}")

    def select_context(self, node_name):
        if node_name in self.context:
            print(f"\n🎯 **Context for {node_name}:**\n{self.context[node_name]}")
        else:
            print(Fore.RED + f"⚠️ No execution context found for {node_name}.")

    def restore_context(self, node_name):
        agent = next((a for a in self.agents if a.name == node_name), None)
        if agent:
            try:
                agent.rollback()
                del self.context[node_name]
                print(Fore.BLUE + f"🔄 {node_name} rolled back successfully.")
            except AttributeError:
                print(Fore.RED + f"⚠️ {node_name} has no rollback method.")
            except Exception as e:
                print(Fore.RED + f"⚠️ Error during rollback of {node_name}: {e}")
        else:
            print(Fore.RED + f"⚠️ Agent {node_name} not found.")

    def topological_sort(self):
        in_degree = {agent: len(agent.dependencies) for agent in self.agents}
        queue = deque([agent for agent in self.agents if in_degree[agent] == 0])

        sorted_agents = []
        while queue:
            current_agent = queue.popleft()
            sorted_agents.append(current_agent)

            for dependent in current_agent.dependents:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(sorted_agents) != len(self.agents):
            raise ValueError("Circular dependencies detected, preventing execution order.")

        return sorted_agents
