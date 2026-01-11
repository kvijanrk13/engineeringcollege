# debug_structure.py
import os
import sys

print("Checking project structure...")
print(f"Current directory: {os.getcwd()}")

# Check if utils directory exists
utils_path = os.path.join("dashboard", "utils")
if os.path.exists(utils_path):
    print(f"✓ utils directory exists: {utils_path}")
else:
    print(f"✗ utils directory NOT found: {utils_path}")
    # Create it
    os.makedirs(utils_path, exist_ok=True)
    print(f"  Created utils directory")

# Check for cloudinary_utils.py
cloudinary_utils_path = os.path.join(utils_path, "cloudinary_utils.py")
if os.path.exists(cloudinary_utils_path):
    print(f"✓ cloudinary_utils.py exists: {cloudinary_utils_path}")
else:
    print(f"✗ cloudinary_utils.py NOT found: {cloudinary_utils_path}")

# Check for __init__.py in utils
init_path = os.path.join(utils_path, "__init__.py")
if os.path.exists(init_path):
    print(f"✓ __init__.py exists: {init_path}")
else:
    print(f"✗ __init__.py NOT found: {init_path}")
    # Create it
    with open(init_path, 'w') as f:
        f.write("# Package init\n")
    print(f"  Created __init__.py")

# Try to import
print("\nTrying to import...")
try:
    from dashboard.utils import cloudinary_utils
    print("✓ Successfully imported cloudinary_utils")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")