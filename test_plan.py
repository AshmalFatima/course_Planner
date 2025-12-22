import sqlite3
from app import get_courses_for_semester, generate_plans

# Get courses for program 2, semester 6
courses = get_courses_for_semester(2, 6)
print(f"Found {len(courses)} total courses for program 2, semester 6:")
for c in courses:
    print(f"  {c['code']}: {c['name']} ({c['credits']} credits)")

# Filter completed courses (matching what the API does)
completed_courses = ['CS002', 'CS003', 'CS005', 'CS007', 'CS009', 'CS011', 'CS013', 'CS015', 'CS017', 'CS019', 'CS021', 'CS022', 'CS024']
completed_set = set(completed_courses)
available_courses = [c for c in courses if c['code'] not in completed_set]

print(f"\nAfter filtering completed courses: {len(available_courses)} courses")
for c in available_courses:
    print(f"  {c['code']}: {c['name']} ({c['credits']} credits)")

# Try to generate a plan
print(f"\nGenerating plan with target_credits=17, preference=easy...")
try:
    plans = generate_plans(available_courses, 17, 'easy')
    print(f"Generated {len(plans)} plans")
    if plans:
        print(f"Plan 1 has {len(plans[0]['courses'])} courses, total {plans[0]['total_credits']} credits")
except Exception as e:
    print(f"Error generating plans: {e}")
    import traceback
    traceback.print_exc()
