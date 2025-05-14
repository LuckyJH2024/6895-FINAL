"""
Predefined agent templates for quickly creating agent groups for common scenarios.
Each template contains configurations for multiple agents and their dependency relationships.
"""

TEMPLATES = {
    "Wedding Planning": {
        "description": "An agent team for planning a wedding, responsible for venue selection, scheduling, and transportation coordination.",
        "agents": [
            {
                "name": "Location and Time Setup Agent",
                "backstory": "You are responsible for defining locations, travel times, and guest arrival schedules.",
                "task_description": "Set locations, travel durations, and ensure accurate arrival arrangements.",
                "task_expected_output": """
<response>
  <task>Set location and time plans</task>
  <people>All guests</people>
  <time>Travel durations and guest expected arrival times</time>
</response>
"""
            },
            {
                "name": "Task Scheduling Agent",
                "backstory": "You are responsible for managing the scheduling of required wedding tasks.",
                "task_description": "Schedule gift pickup after 12:00, clothing pickup before 2:00, and ensure a 3:00 photo session.",
                "task_expected_output": """
<response>
  <task>Optimize task schedule</task>
  <people>Staff and participants</people>
  <time>Specific time slots for all tasks</time>
</response>
"""
            },
            {
                "name": "Resource Management Agent",
                "backstory": "You efficiently allocate available transportation resources.",
                "task_description": "Coordinate the use of 5-seat vehicles and available helpers to ensure guest transport and task completion.",
                "task_expected_output": """
<response>
  <task>Vehicle and resource allocation</task>
  <people>Drivers and coordinators</people>
  <time>Scheduling of various resources</time>
</response>
"""
            },
            {
                "name": "Constraint Validation Agent",
                "backstory": "You validate all scheduling constraints to ensure smooth execution.",
                "task_description": "Ensure all tasks are completed within operating hours and that vehicle constraints are respected.",
                "task_expected_output": """
<response>
  <task>Validate compliance of all plans</task>
  <people>All involved personnel</people>
  <time>Time windows for all constraints</time>
</response>
"""
            },
            {
                "name": "Wedding Supervisor Agent",
                "backstory": "You supervise the overall wedding logistics to ensure task execution.",
                "task_description": "Monitor and ensure on-time completion of all tasks and resolve any logistical issues.",
                "task_expected_output": """
<response>
  <task>Global wedding plan coordination</task>
  <people>All related personnel</people>
  <time>Complete event schedule</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "Location and Time Setup Agent", "to": "Task Scheduling Agent"},
            {"from": "Location and Time Setup Agent", "to": "Resource Management Agent"},
            {"from": "Task Scheduling Agent", "to": "Constraint Validation Agent"},
            {"from": "Resource Management Agent", "to": "Constraint Validation Agent"},
            {"from": "Constraint Validation Agent", "to": "Wedding Supervisor Agent"}
        ]
    },
    
    "Family Dinner Planning": {
        "description": "An agent team for planning and coordinating a family dinner.",
        "agents": [
            {
                "name": "Members and Time Setup Agent",
                "backstory": "You track family members' arrivals and ensure accurate scheduling.",
                "task_description": "Set arrival times, locations, and travel durations for all family members.",
                "task_expected_output": """
<response>
  <task>Set family arrival schedule</task>
  <people>All family members</people>
  <time>Arrival times and travel plans for everyone</time>
</response>
"""
            },
            {
                "name": "Requirement Setup Agent",
                "backstory": "You manage cooking schedules and key logistical needs.",
                "task_description": "Arrange turkey and side dish preparation, and ensure someone is home for supervision.",
                "task_expected_output": """
<response>
  <task>Plan cooking tasks</task>
  <people>Designated cooks</people>
  <time>Timing for all cooking tasks</time>
</response>
"""
            },
            {
                "name": "Constraint Validation Agent",
                "backstory": "You validate all scheduling constraints and ensure
