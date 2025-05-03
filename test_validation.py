import sys
import os

# 添加 src 路径以导入 utils 模块
project_root = os.path.abspath(os.path.join(os.getcwd(), 'src'))
sys.path.append(project_root)

# 导入验证函数
from utils.validation import validate_response_format

# 测试示例 1：合格输出
output_valid = """
<response>
  <task>Coordinate arrivals</task>
  <time>James at 2PM, Emily at 3PM</time>
  <people>James, Emily, Grandma</people>
</response>
"""

# 测试示例 2：缺少字段
output_invalid = """
<response>
  <time>Only time provided</time>
</response>
"""

# 运行测试
print("✅ Valid Output:", validate_response_format(output_valid))      # 应返回 True
print("❌ Invalid Output:", validate_response_format(output_invalid))  # 应返回 False
