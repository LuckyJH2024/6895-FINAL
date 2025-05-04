#!/usr/bin/env python3
"""
SagaLLM前端启动脚本
此脚本确保所有路径设置正确，并启动选择的前端界面
"""

import os
import sys
import subprocess
import argparse
import io

def setup_environment():
    """设置必要的环境变量和Python路径"""
    # 获取当前目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 将当前目录添加到Python路径
    os.environ["PYTHONPATH"] = current_dir
    sys.path.insert(0, current_dir)
    
    # 保存原始的标准输出和错误流，防止被垃圾回收
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # 设置UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "en_US.UTF-8"
    os.environ["LANG"] = "en_US.UTF-8"
    
    # 确保有.env文件
    env_file = os.path.join(current_dir, '.env')
    if not os.path.exists(env_file):
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# SagaLLM环境变量\n")
            f.write("# 如有需要，请在此添加OPENAI_API_KEY=你的密钥\n")
            f.write("OPENAI_API_KEY=\n")
        print(f"已创建.env文件，请编辑 {env_file} 添加必要的API密钥")
    
    print(f"设置PYTHONPATH={os.environ['PYTHONPATH']}")
    print(f"设置PYTHONIOENCODING={os.environ['PYTHONIOENCODING']}")

def check_dependencies():
    """检查必要的Python依赖是否已安装"""
    required_packages = {
        "streamlit": "streamlit",
        "gradio": "gradio",
        "networkx": "networkx",
        "matplotlib": "matplotlib", 
        "python-dotenv": "dotenv",
        "openai": "openai",
        "colorama": "colorama"
    }
    
    missing = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def verify_modules():
    """验证核心模块是否可以正确导入"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.multi_agent.saga import Saga
        from src.multi_agent.agent import Agent
        print("✅ 核心模块验证成功")
        return True
    except ImportError as e:
        print(f"❌ 核心模块导入失败: {e}")
        print("请确保当前目录下有src/multi_agent/saga.py和src/multi_agent/agent.py文件")
        return False

def run_streamlit():
    """启动Streamlit前端"""
    streamlit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'streamlit_frontend.py')
    print(f"启动Streamlit前端: {streamlit_path}")
    # 使用环境变量设置Python路径
    env = os.environ.copy()
    # 添加PYTHONIOENCODING环境变量，确保Python正确处理UTF-8
    env["PYTHONIOENCODING"] = "utf-8"
    # 使用subprocess调用streamlit
    subprocess.call(['streamlit', 'run', streamlit_path], env=env)

def run_gradio():
    """启动Gradio前端"""
    gradio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend_design.py')
    print(f"启动Gradio前端: {gradio_path}")
    # 使用环境变量设置Python路径
    env = os.environ.copy()
    # 添加PYTHONIOENCODING环境变量，确保Python正确处理UTF-8
    env["PYTHONIOENCODING"] = "utf-8"
    # 使用subprocess调用python
    subprocess.call(['python', gradio_path], env=env)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='启动SagaLLM前端界面')
    parser.add_argument('--frontend', choices=['streamlit', 'gradio'], default='streamlit',
                      help='选择要启动的前端类型 (默认: streamlit)')
    
    args = parser.parse_args()
    
    # 设置环境
    setup_environment()
    
    # 检查依赖
    if not check_dependencies():
        print("请安装缺少的依赖后重试")
        sys.exit(1)
    
    # 验证核心模块
    if not verify_modules():
        print("核心模块验证失败，但仍将尝试启动前端")
    
    # 启动选择的前端
    if args.frontend == 'streamlit':
        run_streamlit()
    else:
        run_gradio() 