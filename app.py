from flask import Flask, render_template, request, jsonify
import sqlite3
from itertools import combinations

app = Flask(__name__)

def get_departments():
    """Get all departments"""
    conn = sqlite3.connect("university.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM departments")
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return data

def get_programs(dept_id):
    """Get programs for a department"""
    conn = sqlite3.connect("university.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM programs WHERE department_id = ?", (dept_id,))
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return data

def get_courses_for_semester(program_id, semester):
    """Get all courses for a program and semester"""
    conn = sqlite3.connect("university.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.code, c.name, c.description, c.credits, c.difficulty,
               pc.prerequisites
        FROM courses c
        JOIN program_courses pc ON c.id = pc.course_id
        WHERE pc.program_id = ? AND pc.semester = ? 
        ORDER BY c.code
    """, (program_id, semester))
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return data

def generate_plans(courses, target_credits, preference):
    """
    Generate multiple course plans matching the target credits exactly
    Credit hours remain the same regardless of difficulty preference
    Ensures total credits stay within 11-24 range
    """
    
    # Use exact target credits - no adjustment based on preference
    target_credits = max(11, min(24, target_credits))
    
    # Generate all combinations that match or are close to target
    plans = []
    for r in range(len(courses) + 1):
        for combo in combinations(courses, r):
            total = sum(c['credits'] for c in combo)
            # Accept plans within ±1 credit of target
            if target_credits - 1 <= total <= target_credits + 1:
                # Filter by difficulty if specified
                if preference == 'easy':
                    difficulty_match = sum(1 for c in combo if c['difficulty'] == 'Easy')
                elif preference == 'balanced':
                    difficulty_match = sum(1 for c in combo if c['difficulty'] == 'Balanced')
                else:  # challenging
                    difficulty_match = sum(1 for c in combo if c['difficulty'] == 'Challenging')
                
                plans.append({
                    'courses': list(combo),
                    'total_credits': total,
                    'course_count': len(combo),
                    'difficulty_match': difficulty_match
                })
    
    # Sort by: 1) closeness to target, 2) difficulty match, 3) prefer exact target
    plans.sort(key=lambda x: (abs(x['total_credits'] - target_credits), -x['difficulty_match'], -x['total_credits']))
    
    return plans[:5]  # Return top 5 plans

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/academic-history")
def academic_history():
    return render_template("academic_history.html")

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/api/departments", methods=["GET"])
def api_departments():
    return jsonify({'departments': get_departments()})

@app.route("/api/programs/<int:dept_id>", methods=["GET"])
def api_programs(dept_id):
    return jsonify({'programs': get_programs(dept_id)})

@app.route("/api/all-courses/<int:program_id>", methods=["GET"])
def api_all_courses(program_id):
    """Get all courses for a program across all semesters"""
    try:
        conn = sqlite3.connect("university.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.id, c.code, c.name, c.description, c.credits, c.difficulty,
                   pc.semester, pc.prerequisites
            FROM courses c
            JOIN program_courses pc ON c.id = pc.course_id
            WHERE pc.program_id = ?
            ORDER BY pc.semester, c.code
        """, (program_id,))
        data = [dict(row) for row in cur.fetchall()]
        conn.close()
        return jsonify({'courses': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/plan", methods=["POST"])
def api_plan():
    try:
        data = request.get_json()
        
        # Log received data for debugging
        print(f"DEBUG: Received data: {data}")
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        program_id = data.get('program_id')
        semester = data.get('semester')
        target_credits = data.get('max_credits')
        preference = data.get('preference', 'balanced').lower()
        completed_courses = data.get('completed_courses', [])  # List of course codes
        
        print(f"DEBUG: program_id={program_id}, semester={semester}, target_credits={target_credits}, preference={preference}")
        
        if not program_id:
            print(f"ERROR: program_id missing")
            return jsonify({'error': 'Program is required'}), 400
        if semester is None:
            print(f"ERROR: semester missing")
            return jsonify({'error': 'Semester is required'}), 400
        if not target_credits:
            print(f"ERROR: target_credits missing: {target_credits}")
            return jsonify({'error': 'Credit hours are required'}), 400
        
        # Convert to proper types
        try:
            program_id = int(program_id)
            semester = int(semester)
            target_credits = int(target_credits)
        except (ValueError, TypeError) as e:
            print(f"ERROR: Conversion failed: {str(e)}")
            return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
        
        # Validate ranges
        if not 1 <= semester <= 8:
            print(f"ERROR: Semester out of range: {semester}")
            return jsonify({'error': 'Semester must be 1-8'}), 400
        if not 11 <= target_credits <= 24:
            print(f"ERROR: Credits out of range: {target_credits}")
            return jsonify({'error': 'Credits must be 11-24'}), 400
        
        # Get courses for this semester and program
        print(f"DEBUG: Getting courses for program {program_id}, semester {semester}")
        courses = get_courses_for_semester(program_id, semester)
        print(f"DEBUG: Found {len(courses) if courses else 0} courses")
        
        if not courses:
            print(f"ERROR: No courses available")
            return jsonify({'error': 'No courses available for this semester'}), 404
        
        # Filter out completed courses
        completed_set = set(completed_courses)
        available_courses = [c for c in courses if c['code'] not in completed_set]
        print(f"DEBUG: Available courses after filtering: {len(available_courses)}")
        
        if not available_courses:
            print(f"ERROR: All courses completed")
            return jsonify({'error': 'All courses in this semester have been completed'}), 400
        
        # Generate plans based on preference
        print(f"DEBUG: Generating plans with target={target_credits}, preference={preference}")
        plans = generate_plans(available_courses, target_credits, preference)
        print(f"DEBUG: Generated {len(plans) if plans else 0} plans")
        
        if not plans:
            # Calculate max possible credits with available courses
            max_possible = sum(c['credits'] for c in available_courses)
            error_msg = f'Not enough courses available. You have {len(available_courses)} course(s) with {max_possible} total credits, but need {target_credits} credits. Try selecting fewer completed courses or choose a different semester.'
            print(f"ERROR: Could not generate plans. {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Return plans with all course details
        response = {
            'success': True,
            'completed_courses': completed_courses,
            'plans': [
                {
                    'total_credits': plan['total_credits'],
                    'course_count': plan['course_count'],
                    'courses': [
                        {
                            'code': c['code'],
                            'name': c['name'],
                            'description': c['description'],
                            'credits': c['credits'],
                            'difficulty': c['difficulty'],
                            'semester': semester,
                            'prerequisites': c['prerequisites']
                        }
                        for c in plan['courses']
                    ]
                }
                for plan in plans
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"ERROR: Exception in api_plan: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route("/api/validate-prerequisites", methods=["POST"])
def api_validate_prerequisites():
    """Check if student has passed prerequisites"""
    try:
        data = request.get_json()
        completed_courses = data.get('completed_courses', [])
        courses_in_plan = data.get('courses_in_plan', [])
        
        issues = []
        for course in courses_in_plan:
            prereqs = course.get('prerequisites', '').strip()
            if prereqs and prereqs != '':
                needed = set(p.strip() for p in prereqs.split(','))
                completed = set(completed_courses)
                missing = needed - completed
                if missing:
                    issues.append({
                        'course': course['code'],
                        'missing_prereqs': list(missing)
                    })
        
        return jsonify({
            'valid': len(issues) == 0,
            'issues': issues
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
