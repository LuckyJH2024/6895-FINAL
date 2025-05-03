import sys
import os

# Step 1: 将 src 路径添加到 sys.path，确保可以导入 utils 模块
project_root = os.path.abspath(os.path.join(os.getcwd(), 'src'))
sys.path.append(project_root)

# Step 2: 正常导入模块
from utils.failure_predictor import FailurePredictor

# Step 3: 实例化并测试
predictor = FailurePredictor()
prompt = "You define locations, travel times, and guest arrival schedules."
result = predictor.predict("Test Agent", prompt)
print(result)
