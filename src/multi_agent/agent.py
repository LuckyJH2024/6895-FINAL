from textwrap import dedent
from utils.failure_predictor import FailurePredictor
from utils.validation import validate_response_format
from multi_agent.crew import Crew
from planning_agent.react_agent import ReactAgent
from tool_agent.tool import Tool

class Agent:
    def __init__(
        self,
        name: str,
        backstory: str,
        task_description: str,
        task_expected_output: str = "",
        tools: list[Tool] | None = None,
        llm: str = "gpt-4o",
    ):
        self.name = name
        self.backstory = backstory
        self.task_description = task_description
        self.task_expected_output = task_expected_output
        self.react_agent = ReactAgent(
            model=llm, system_prompt=self.backstory, tools=tools or []
        )

        self.dependencies: list[Agent] = []  # Agents that this agent depends on
        self.dependents: list[Agent] = []    # Agents that depend on this agent

        self.context = ""
        self.output = ""  # 存储Agent自己的输出，方便共享
        self.predictor = FailurePredictor()

        Crew.register_agent(self)

    def __repr__(self):
        return f"{self.name}"

    def __rshift__(self, other):
        self.add_dependent(other)
        return other

    def __lshift__(self, other):
        self.add_dependency(other)
        return other

    def add_dependency(self, other):
        if isinstance(other, Agent):
            self.dependencies.append(other)
            other.dependents.append(self)
        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                self.dependencies.append(item)
                item.dependents.append(self)
        else:
            raise TypeError("The dependency must be an instance or list of Agent.")

    def add_dependent(self, other):
        if isinstance(other, Agent):
            other.dependencies.append(self)
            self.dependents.append(other)
        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                item.dependencies.append(self)
                self.dependents.append(item)
        else:
            raise TypeError("The dependent must be an instance or list of Agent.")

    def receive_context(self, input_data):
        self.context += f"{self.name} received context: \n{input_data}\n"

    def create_prompt(self):
        prompt = dedent(f"""
        You are an AI agent, part of a multi-agent team.

        <task_description>
        {self.task_description}
        </task_description>

        <task_expected_output>
        {self.task_expected_output}
        </task_expected_output>

        <context>
        {self.context}
        </context>

        Your response:
        """).strip()

        return prompt

    def rollback(self):
        print(f"🔄 Rolling back {self.name}'s operation...")

    def run(self):
        msg = self.create_prompt()

        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            prediction = self.predictor.predict(agent_name=self.name, prompt=msg)
            risk_level = prediction.get("risk", "").lower()
            reason = prediction.get("reason", "")

            if risk_level != "high":
                break

            print(f"⚠️ Attempt {attempt+1}: Predicted failure risk for {self.name} is HIGH. Reason: {reason}")
            attempt += 1

        if risk_level == "high":
            print(f"❌ All attempts resulted in high risk for {self.name}. Skipping execution.")
            self.rollback()
            self.output = f"<response>Skipped due to high predicted failure risk. Reason: {reason}</response>"
            return self.output

        output = self.react_agent.run(user_msg=msg)

        if not validate_response_format(output):
            print(f"❌ Validation failed for agent {self.name}: Missing required structure.")
            raise ValueError(f"Agent {self.name} output format invalid.")

        self.output = output  # 存储自己的输出到output属性

        for dependent in self.dependents:
            dependent.receive_context(self.output)

        return output
