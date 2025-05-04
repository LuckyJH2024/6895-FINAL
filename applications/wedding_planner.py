#!/usr/bin/env python3
"""
SagaLLM婚礼规划示例
此脚本专门用于运行婚礼规划智能体模板，并提供详细的调试输出
"""

import sys
import os
import io
import traceback
from dotenv import load_dotenv
load_dotenv()

# 保存原始的标准输出和错误流，防止被垃圾回收
original_stdout = sys.stdout
original_stderr = sys.stderr

# 设置标准输出和错误流编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取项目根目录路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"📂 项目根目录: {project_root}")

# 添加src目录到Python路径
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)
sys.path.append(project_root)

# 设置环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

# 打印Python路径以验证
print("🔍 Python路径:")
for path in sys.path:
    print(path)

# 尝试导入必要的模块
try:
    from src.multi_agent.saga import Saga
    from src.multi_agent.agent import Agent
    from agent_templates import get_template
    print("✅ 成功导入Saga和Agent类")
except ModuleNotFoundError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def create_wedding_agents():
    """创建婚礼规划智能体"""
    print("🏗️ 创建婚礼规划智能体...")
    
    # 从模板获取婚礼规划智能体配置
    template_data = get_template("婚礼计划")
    if not template_data:
        print("❌ 未找到婚礼计划模板")
        return None, None
    
    # 创建智能体
    agents = []
    agent_dict = {}
    
    for agent_data in template_data["agents"]:
        print(f"📝 创建智能体: {agent_data['name']}")
        try:
            agent = Agent(
                name=agent_data["name"],
                backstory=agent_data["backstory"],
                task_description=agent_data["task_description"],
                task_expected_output=agent_data["task_expected_output"]
            )
            agents.append(agent)
            agent_dict[agent_data["name"]] = agent
        except Exception as e:
            print(f"❌ 创建智能体 {agent_data['name']} 失败: {e}")
            traceback.print_exc()
    
    # 建立依赖关系
    for dep in template_data["dependencies"]:
        from_agent = agent_dict.get(dep["from"])
        to_agent = agent_dict.get(dep["to"])
        if from_agent and to_agent:
            print(f"🔗 建立依赖关系: {dep['from']} → {dep['to']}")
            try:
                from_agent.add_dependent(to_agent)
            except Exception as e:
                print(f"❌ 建立依赖关系失败: {e}")
                traceback.print_exc()
    
    return agents, agent_dict

def main():
    """主函数"""
    print("\n==================================================")
    print("🚀 启动婚礼规划智能体系统")
    print("==================================================\n")
    
    # 创建智能体
    agents, agent_dict = create_wedding_agents()
    if not agents:
        print("❌ 创建智能体失败，程序退出")
        return
    
    # 创建Saga实例
    print("\n🏗️ 初始化Saga协调器...")
    saga = Saga()
    
    # 注册智能体并执行
    try:
        print("\n🔄 注册智能体到Saga协调器...")
        saga.transaction_manager(agents)
        
        print("\n🚀 执行智能体任务...")
        saga.saga_coordinator(with_rollback=True)
        
        # 打印执行结果
        print("\n==================================================")
        print("📊 执行结果:")
        print("==================================================\n")
        
        for agent in agents:
            if agent.name in saga.context:
                print(f"✅ {agent.name}: 执行成功")
                print(f"📄 结果: {saga.context[agent.name][:200]}...\n")
            else:
                print(f"❌ {agent.name}: 未执行或执行失败\n")
        
        # 打印内部和外部关系
        saga.intra_agent()
        saga.inter_agent()
        
    except Exception as e:
        print(f"\n❌ 执行过程中出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 