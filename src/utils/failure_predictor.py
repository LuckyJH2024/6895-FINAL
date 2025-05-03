import re
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class FailurePredictor:
    def __init__(self):
        self.client = OpenAI()
        self.previous_risk_reason = None
        self.previous_output = None

    def predict(self, agent_name: str, prompt: str) -> dict:
        # If there was a previous high-risk reason, include it in the prompt for context
        if self.previous_risk_reason:
            prompt = f"{prompt}\n\nNote: Your previous attempt was risky because: \"{self.previous_risk_reason}\". Please revise the plan to reduce ambiguity or coordination errors."

        gpt_prompt = f"""
        You are a reasoning risk assessor for autonomous agents. 
        Given the following task prompt, assess how likely the agent is to produce a failure or invalid output.

        Please rate the risk level as:

        - HIGH: only if the task is fundamentally ambiguous, internally contradictory, or nearly impossible to complete without major assumptions. Use this **only** when the output is very likely to be invalid.
        - MEDIUM: if the task requires modest assumptions, clarifications, or minor coordination, but is overall understandable and likely to succeed.
        - LOW: if the task is clearly defined, well-scoped, and deterministic with minimal risk of failure.

        Prefer MEDIUM when the structure is clear and output format is predictable, even if it requires some reasoning or coordination.
        Avoid labeling HIGH unless major gaps, contradictions, or unresolvable ambiguity are present.

        Reply strictly in JSON with this format:
        {{
            "risk": "HIGH | MEDIUM | LOW",
            "reason": "Explanation of why"
        }}

        Prompt to evaluate:
        \"\"\"{prompt}\"\"\"
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": gpt_prompt}],
            temperature=0.2,
        )

        # Parsing the GPT response
        try:
            content = response.choices[0].message.content.strip()
            print(f"🔍 GPT raw output: {content}")

            # Clean up the raw JSON response
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
                content = re.sub(r"\s*```$", "", content)

            result = json.loads(content)
            risk = result.get("risk", "UNKNOWN")
            reason = result.get("reason", "No explanation provided.")
            print(f"🔮 GPT Risk Prediction for {agent_name}: {risk} | Reason: {reason}")

            # Store the output and reason for future reference
            self.previous_risk_reason = reason
            self.previous_output = result

            return {"risk": risk, "reason": reason}

        except Exception as e:
            print("❌ Failed to parse GPT output:", e)
            return {"risk": "UNKNOWN", "reason": "GPT output parsing error."}
