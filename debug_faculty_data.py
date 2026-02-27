# debug_faculty_data.py
import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineeringcollege.settings')
django.setup()

# Now import models after setup
from dashboard.models import Faculty

def debug_faculty_complete(faculty_id=7001):
    try:
        faculty = Faculty.objects.get(employee_code=str(faculty_id))
        
        print(f"\n{'='*60}")
        print(f"COMPLETE FACULTY DATA FOR: {faculty.staff_name} (Code: {faculty.employee_code})")
        print(f"{'='*60}\n")
        
        # Rest of your code...
        # (keep the rest of the code as before)
        
    except Faculty.DoesNotExist:
        print(f"Faculty with employee_code {faculty_id} not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_faculty_complete(7001)