"""
预定义的智能体模板，用于快速创建常见场景的智能体组。
每个模板包含多个Agent的配置信息和它们之间的依赖关系。
"""

TEMPLATES = {
    "婚礼计划": {
        "description": "一个用于婚礼规划的智能体团队，负责地点选择、时间安排和交通协调。",
        "agents": [
            {
                "name": "地点与时间设置智能体",
                "backstory": "你负责定义地点、交通时间和宾客到达时间表。",
                "task_description": "设置地点、交通时间和确保准确的到达时间安排。",
                "task_expected_output": """
<response>
  <task>设置地点和时间计划</task>
  <people>所有宾客</people>
  <time>各个地点之间的旅行时间和宾客预计到达时间</time>
</response>
"""
            },
            {
                "name": "任务安排智能体",
                "backstory": "你负责管理所需的婚礼任务的调度。",
                "task_description": "在12:00后安排礼品收集，在2:00前安排服装取货，确保3:00的拍照时间。",
                "task_expected_output": """
<response>
  <task>优化任务日程安排</task>
  <people>工作人员和参与者</people>
  <time>所有任务的具体时间安排</time>
</response>
"""
            },
            {
                "name": "资源管理智能体",
                "backstory": "你高效地分配可用的交通资源。",
                "task_description": "协调5座车辆的使用和可用的朋友帮助，确保宾客运输和任务完成。",
                "task_expected_output": """
<response>
  <task>车辆和资源分配</task>
  <people>司机和负责人</people>
  <time>各种资源的调度时间表</time>
</response>
"""
            },
            {
                "name": "约束验证智能体",
                "backstory": "你验证所有调度约束以确保顺利执行。",
                "task_description": "确保所有任务在营业时间内完成，且车辆约束得到满足。",
                "task_expected_output": """
<response>
  <task>验证所有计划的合规性</task>
  <people>所有参与的人员</people>
  <time>各项约束的时间窗口</time>
</response>
"""
            },
            {
                "name": "婚礼监督智能体",
                "backstory": "你监督整个婚礼物流，确保任务顺利执行。",
                "task_description": "监控并确保所有任务按时完成，解决任何物流问题。",
                "task_expected_output": """
<response>
  <task>全局婚礼计划协调</task>
  <people>所有相关人员</people>
  <time>完整的事件时间表</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "地点与时间设置智能体", "to": "任务安排智能体"},
            {"from": "地点与时间设置智能体", "to": "资源管理智能体"},
            {"from": "任务安排智能体", "to": "约束验证智能体"},
            {"from": "资源管理智能体", "to": "约束验证智能体"},
            {"from": "约束验证智能体", "to": "婚礼监督智能体"}
        ]
    },
    
    "家庭聚餐规划": {
        "description": "一个用于规划和协调家庭聚餐的智能体团队。",
        "agents": [
            {
                "name": "成员和时间设置智能体",
                "backstory": "你跟踪家庭成员的到达情况并确保准确的时间安排。",
                "task_description": "设置到达时间、地点和所有家庭成员的旅行持续时间。",
                "task_expected_output": """
<response>
  <task>设置家庭成员到达时间表</task>
  <people>所有家庭成员</people>
  <time>每个人的到达时间和旅行计划</time>
</response>
"""
            },
            {
                "name": "需求设置智能体",
                "backstory": "你管理烹饪时间表和关键的后勤需求。",
                "task_description": "安排火鸡和配菜的准备工作，确保有人在家监督。",
                "task_expected_output": """
<response>
  <task>规划烹饪任务</task>
  <people>负责烹饪的人</people>
  <time>所有烹饪任务的时间安排</time>
</response>
"""
            },
            {
                "name": "约束验证智能体",
                "backstory": "你验证所有调度约束并确保合规性。",
                "task_description": "验证所有接送、烹饪时间表和监督要求都得到满足。",
                "task_expected_output": """
<response>
  <task>验证接送和烹饪的可行性</task>
  <people>所有相关人员</people>
  <time>各项约束的时间窗口</time>
</response>
"""
            },
            {
                "name": "监督智能体",
                "backstory": "你监督所有的后勤元素并生成最终的晚餐准备报告。",
                "task_description": "监控和报告关键任务，包括烹饪开始时间、接送和准备工作。",
                "task_expected_output": """
<response>
  <task>监督晚餐准备和确认所有后勤</task>
  <people>所有家庭成员</people>
  <time>所有活动的最终时间表</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "成员和时间设置智能体", "to": "需求设置智能体"},
            {"from": "需求设置智能体", "to": "约束验证智能体"},
            {"from": "约束验证智能体", "to": "监督智能体"}
        ]
    },
    
    "旅行计划": {
        "description": "一个用于规划和协调多人旅行的智能体团队。",
        "agents": [
            {
                "name": "目的地分析智能体",
                "backstory": "你分析旅行目的地并提供天气、交通和景点信息。",
                "task_description": "研究和汇总目的地的关键信息，包括最佳参观时间和地点建议。",
                "task_expected_output": """
<response>
  <task>目的地分析和推荐</task>
  <people>所有旅行者</people>
  <time>最佳参观月份和每日时间</time>
</response>
"""
            },
            {
                "name": "行程安排智能体",
                "backstory": "你创建详细的每日行程，包括景点、餐厅和活动。",
                "task_description": "为旅行的每一天创建优化的行程，确保地点之间的合理交通时间。",
                "task_expected_output": """
<response>
  <task>创建每日行程</task>
  <people>所有旅行者</people>
  <time>每个地点的具体时间安排</time>
</response>
"""
            },
            {
                "name": "预算管理智能体",
                "backstory": "你跟踪和管理旅行预算，包括住宿、交通和活动成本。",
                "task_description": "分配预算到不同的旅行类别，确保总支出在限制范围内。",
                "task_expected_output": """
<response>
  <task>预算分配和成本跟踪</task>
  <people>所有旅行者</people>
  <time>支出的时间安排</time>
</response>
"""
            },
            {
                "name": "协调智能体",
                "backstory": "你确保所有旅行元素无缝协作，并解决任何冲突。",
                "task_description": "检查行程、预算和目的地信息之间的一致性，并提出整合的旅行计划。",
                "task_expected_output": """
<response>
  <task>协调和优化完整旅行计划</task>
  <people>所有旅行者</people>
  <time>完整旅行的时间表</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "目的地分析智能体", "to": "行程安排智能体"},
            {"from": "目的地分析智能体", "to": "预算管理智能体"},
            {"from": "行程安排智能体", "to": "协调智能体"},
            {"from": "预算管理智能体", "to": "协调智能体"}
        ]
    }
}

def get_templates():
    """获取所有可用的模板名称"""
    return list(TEMPLATES.keys())

def get_template_description(template_name):
    """获取指定模板的描述"""
    if template_name in TEMPLATES:
        return TEMPLATES[template_name]["description"]
    return "未找到模板"

def get_template(template_name):
    """获取完整的模板数据"""
    if template_name in TEMPLATES:
        return TEMPLATES[template_name]
    return None 