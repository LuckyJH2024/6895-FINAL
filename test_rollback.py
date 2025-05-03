import sys
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ 1. 设置项目根目录，并强制切换当前工作目录
project_root = os.path.abspath(os.path.dirname(__file__))  # 如果当前脚本就在根目录
os.chdir(project_root)  # 强制切换工作目录到项目根
print(f"📂 Project Root: {project_root}")

# ✅ 2. 设置并添加 src 目录到 sys.path
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# ✅ 3. 打印 sys.path 和 src 目录下内容用于调试
print("🔍 Updated sys.path:")
for path in sys.path:
    print(path)
print("📁 Contents in src:", os.listdir(src_path))

# ✅ 4. 尝试导入 Saga 模块
try:
    from multi_agent.saga import Saga
    from multi_agent.agent import Agent
    print("✅ Saga imported successfully!")
    print("✅ Agent imported successfully!")
except ModuleNotFoundError as e:
    print("❌ Import failed:", e)
    sys.exit(1)

# ✅ 5. 初始化 Saga 实例
saga = Saga()

# ✅ 6. 故意制造冲突的两个 Agent（相同时间+人物）
Agent_A = Agent(
    name="Agent A",
    backstory="安排 Alex 的行程。",
    task_description="安排 Alex 在 10:00 AM 处理任务。",
    task_expected_output="""
    <response>
        <task>任务 A</task>
        <time>10:00 AM</time>
        <people>Alex</people>
    </response>
    """
)

Agent_B = Agent(
    name="Agent B",
    backstory="安排 Alex 的第二个任务。",
    task_description="安排 Alex 在 10:00 AM 处理另一任务。",
    task_expected_output="""
    <response>
        <task>任务 B</task>
        <time>10:00 AM</time>
        <people>Alex</people>
    </response>
    """
)

# ✅ 7. 注册并执行 Saga，触发 rollback
saga.transaction_manager([Agent_A, Agent_B])
saga.saga_coordinator(with_rollback=True)
