import sys
import os

# Step 1: Add the 'src' path to sys.path to ensure the 'utils' module can be imported
project_root = os.path.abspath(os.path.join(os.getcwd(), 'src'))
sys.path.append(project_root)

# Step 2: Import the module normally
from utils.failure_predictor import FailurePredictor

# Step 3: Instantiate and test
predictor = FailurePredictor()
prompt = "You define locations, travel times, and guest arrival schedules."
result = predictor.predict("Test Agent", prompt)
print(result)
