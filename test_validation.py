import sys
import os

# Add 'src' path to import the utils module
project_root = os.path.abspath(os.path.join(os.getcwd(), 'src'))
sys.path.append(project_root)

# Import the validation function
from utils.validation import validate_response_format

# Test Case 1: Valid output
output_valid = """
<response>
  <task>Coordinate arrivals</task>
  <time>James at 2PM, Emily at 3PM</time>
  <people>James, Emily, Grandma</people>
</response>
"""

# Test Case 2: Missing fields
output_invalid = """
<response>
  <time>Only time provided</time>
</response>
"""

# Run tests
print("✅ Valid Output:", validate_response_format(output_valid))      # Should return True
print("❌ Invalid Output:", validate_response_format(output_invalid))  # Should return False
