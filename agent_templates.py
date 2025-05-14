"""
Predefined agent templates for quickly creating agent groups for common scenarios.
Each template contains configuration information for multiple Agents and their dependencies.
"""

TEMPLATES = {
    "Wedding Planning": {
        "description": "An agent team for wedding planning, responsible for venue selection, scheduling, and transportation coordination.",
        "agents": [
            {
                "name": "Venue and Time Setup Agent",
                "backstory": "You are responsible for defining venues, transportation times, and guest arrival schedules.",
                "task_description": "Set up venues, transportation times, and ensure accurate arrival time scheduling.",
                "task_expected_output": """
<response>
  <task>Set up venue and time schedule</task>
  <people>All guests</people>
  <time>Travel times between venues and expected guest arrival times</time>
</response>
"""
            },
            {
                "name": "Task Scheduling Agent",
                "backstory": "You are responsible for managing the scheduling of required wedding tasks.",
                "task_description": "Schedule gift collection after 12:00, arrange clothing pickup before 2:00, ensure photography time at 3:00.",
                "task_expected_output": """
<response>
  <task>Optimize task schedule</task>
  <people>Staff and participants</people>
  <time>Specific time arrangements for all tasks</time>
</response>
"""
            },
            {
                "name": "Resource Management Agent",
                "backstory": "You efficiently allocate available transportation resources.",
                "task_description": "Coordinate the use of 5 vehicles and available friends to help, ensuring guest transportation and task completion.",
                "task_expected_output": """
<response>
  <task>Vehicle and resource allocation</task>
  <people>Drivers and persons in charge</people>
  <time>Schedule timeline for various resources</time>
</response>
"""
            },
            {
                "name": "Constraint Validation Agent",
                "backstory": "You validate all scheduling constraints to ensure smooth execution.",
                "task_description": "Ensure all tasks are completed during business hours and vehicle constraints are met.",
                "task_expected_output": """
<response>
  <task>Validate compliance of all plans</task>
  <people>All participating personnel</people>
  <time>Time windows for various constraints</time>
</response>
"""
            },
            {
                "name": "Wedding Supervision Agent",
                "backstory": "You supervise the entire wedding logistics, ensuring tasks are executed smoothly.",
                "task_description": "Monitor and ensure all tasks are completed on time, resolve any logistics issues.",
                "task_expected_output": """
<response>
  <task>Global wedding plan coordination</task>
  <people>All relevant personnel</people>
  <time>Complete event timeline</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "Venue and Time Setup Agent", "to": "Task Scheduling Agent"},
            {"from": "Venue and Time Setup Agent", "to": "Resource Management Agent"},
            {"from": "Task Scheduling Agent", "to": "Constraint Validation Agent"},
            {"from": "Resource Management Agent", "to": "Constraint Validation Agent"},
            {"from": "Constraint Validation Agent", "to": "Wedding Supervision Agent"}
        ]
    },
    
    "Family Dinner Planning": {
        "description": "An agent team for planning and coordinating family dinners.",
        "agents": [
            {
                "name": "Member and Time Setup Agent",
                "backstory": "You track family members' arrivals and ensure accurate scheduling.",
                "task_description": "Set arrival times, locations, and travel durations for all family members.",
                "task_expected_output": """
<response>
  <task>Set up family member arrival schedule</task>
  <people>All family members</people>
  <time>Arrival time and travel plans for each person</time>
</response>
"""
            },
            {
                "name": "Requirements Setup Agent",
                "backstory": "You manage cooking schedules and key logistics requirements.",
                "task_description": "Schedule turkey and side dish preparation, ensure someone is at home for supervision.",
                "task_expected_output": """
<response>
  <task>Plan cooking tasks</task>
  <people>People responsible for cooking</people>
  <time>Schedule for all cooking tasks</time>
</response>
"""
            },
            {
                "name": "Constraint Validation Agent",
                "backstory": "You validate all scheduling constraints and ensure compliance.",
                "task_description": "Validate that all pickup, cooking schedules, and supervision requirements are met.",
                "task_expected_output": """
<response>
  <task>Validate feasibility of pickups and cooking</task>
  <people>All relevant personnel</people>
  <time>Time windows for various constraints</time>
</response>
"""
            },
            {
                "name": "Supervision Agent",
                "backstory": "You supervise all logistics elements and generate the final dinner preparation report.",
                "task_description": "Monitor and report on key tasks, including cooking start times, pickups, and preparations.",
                "task_expected_output": """
<response>
  <task>Supervise dinner preparation and confirm all logistics</task>
  <people>All family members</people>
  <time>Final schedule for all activities</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "Member and Time Setup Agent", "to": "Requirements Setup Agent"},
            {"from": "Requirements Setup Agent", "to": "Constraint Validation Agent"},
            {"from": "Constraint Validation Agent", "to": "Supervision Agent"}
        ]
    },
    
    "Travel Planning": {
        "description": "An agent team for planning and coordinating multi-person travel.",
        "agents": [
            {
                "name": "Destination Analysis Agent",
                "backstory": "You analyze travel destinations and provide information on weather, transportation, and attractions.",
                "task_description": "Research and summarize key information about destinations, including optimal visiting times and venue recommendations.",
                "task_expected_output": """
<response>
  <task>Destination analysis and recommendations</task>
  <people>All travelers</people>
  <time>Best months to visit and daily timing</time>
</response>
"""
            },
            {
                "name": "Itinerary Planning Agent",
                "backstory": "You create detailed daily itineraries, including attractions, restaurants, and activities.",
                "task_description": "Create optimized itineraries for each day of travel, ensuring reasonable transportation times between locations.",
                "task_expected_output": """
<response>
  <task>Create daily itinerary</task>
  <people>All travelers</people>
  <time>Specific time arrangements for each location</time>
</response>
"""
            },
            {
                "name": "Budget Management Agent",
                "backstory": "You track and manage the travel budget, including accommodations, transportation, and activity costs.",
                "task_description": "Allocate budget to different travel categories, ensuring total expenditure is within limits.",
                "task_expected_output": """
<response>
  <task>Budget allocation and cost tracking</task>
  <people>All travelers</people>
  <time>Expenditure schedule</time>
</response>
"""
            },
            {
                "name": "Coordination Agent",
                "backstory": "You ensure all travel elements work together seamlessly and resolve any conflicts.",
                "task_description": "Check consistency between itinerary, budget, and destination information, and propose an integrated travel plan.",
                "task_expected_output": """
<response>
  <task>Coordinate and optimize complete travel plan</task>
  <people>All travelers</people>
  <time>Complete travel schedule</time>
</response>
"""
            }
        ],
        "dependencies": [
            {"from": "Destination Analysis Agent", "to": "Itinerary Planning Agent"},
            {"from": "Destination Analysis Agent", "to": "Budget Management Agent"},
            {"from": "Itinerary Planning Agent", "to": "Coordination Agent"},
            {"from": "Budget Management Agent", "to": "Coordination Agent"}
        ]
    }
}

def get_templates():
    """Get all available template names"""
    return list(TEMPLATES.keys())

def get_template_description(template_name):
    """Get the description of the specified template"""
    if template_name in TEMPLATES:
        return TEMPLATES[template_name]["description"]
    return "Template not found"

def get_template(template_name):
    """Get complete template data"""
    if template_name in TEMPLATES:
        return TEMPLATES[template_name]
    return None 