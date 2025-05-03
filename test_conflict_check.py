import sys
import os

# 添加 src 路径以导入 utils 模块
project_root = os.path.abspath(os.path.join(os.getcwd(), 'src'))
sys.path.append(project_root)

from utils.validation import detect_conflict_across_agents

# 构造模拟 Agent 输出（含冲突）
outputs = {
    "Agent A": """
    <response>
      <task>Pick up Grandma</task>
      <time>2:00 PM</time>
      <people>James</people>
    </response>
    """,
    "Agent B": """
    <response>
      <task>James cooks turkey</task>
      <time>2:00 PM</time>
      <people>James</people>
    </response>
    """,
}

# 检测冲突
conflict_report = detect_conflict_across_agents(outputs)
print("⚠️ Conflict Report:", conflict_report)
