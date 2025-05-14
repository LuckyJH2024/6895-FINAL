import os
import sys

# load src path 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(project_root)

from utils.failure_predictor import FailurePredictor

def simulate_reflective_retry(task_prompt, agent_name="Test Agent", max_attempts=10):
    predictor = FailurePredictor()
    previous_reason = None

    for attempt in range(1, max_attempts + 1):
        full_prompt = task_prompt
        if previous_reason:
            full_prompt += f"\n\nNote: Your previous attempt was risky because: \"{previous_reason}\". " \
                           f"Please revise the plan to reduce ambiguity or coordination errors."

        print(f"\n🧠 Attempt {attempt} prompt:\n{full_prompt}\n")
        result = predictor.predict(agent_name=agent_name, prompt=full_prompt)
        risk = result["risk"]
        reason = result["reason"]

        print(f"🔮 Prediction: Risk = {risk}, Reason = {reason}")

        if risk.lower() != "high":
            print("✅ Success: Risk reduced.")
            return

        previous_reason = reason

    print("❌ Final result: Still HIGH risk after max attempts.")

# 初始 prompt 故意模糊
initial_prompt = "Plan a schedule for the wedding day. Include all necessary things."

simulate_reflective_retry(task_prompt=initial_prompt)
