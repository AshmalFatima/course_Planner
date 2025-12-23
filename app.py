from flask import Flask, render_template, request, jsonify
import sqlite3
from csp import csp_filter, check_prerequisites
from ga import optimize
from prolog_interface import get_advice

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

def get_completed_courses_from_previous_semesters(program_id, current_semester):
    """
    Get all courses from previous semesters for prerequisite checking
    Assumes student has completed all courses from earlier semesters
    """
    if current_semester <= 1:
        return []
    
    conn = sqlite3.connect("university.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get all courses from semesters 1 to (current_semester - 1)
    cur.execute("""
        SELECT DISTINCT c.id, c.code, c.name, c.description, c.credits, c.difficulty,
               pc.semester, pc.prerequisites
        FROM courses c
        JOIN program_courses pc ON c.id = pc.course_id
        WHERE pc.program_id = ? AND pc.semester < ?
        ORDER BY pc.semester, c.code
    """, (program_id, current_semester))
    
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

@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/planner")
def planner():
    return render_template("planner.html")

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/api/departments", methods=["GET"])
def api_departments():
    return jsonify({'departments': get_departments()})

@app.route("/api/programs/<int:dept_id>", methods=["GET"])
def api_programs(dept_id):
    return jsonify({'programs': get_programs(dept_id)})

@app.route("/api/plan", methods=["POST"])
def api_plan():
    """
    Generate course plans using CSP + GA + Prolog pipeline
    No academic history needed - prerequisites checked automatically
    """
    try:
        data = request.get_json()
        
        print(f"DEBUG: Received data: {data}")
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        program_id = data.get('program_id')
        semester = data.get('semester')
        target_credits = data.get('max_credits')
        preference = data.get('preference', 'balanced').lower()
        cgpa = data.get('cgpa', 3.0)  # Default CGPA for semester 1
        
        print(f"DEBUG: program_id={program_id}, semester={semester}, target_credits={target_credits}, preference={preference}, cgpa={cgpa}")
        
        if not program_id:
            return jsonify({'error': 'Program is required'}), 400
        if semester is None:
            return jsonify({'error': 'Semester is required'}), 400
        if not target_credits:
            return jsonify({'error': 'Credit hours are required'}), 400
        
        # Convert to proper types
        try:
            program_id = int(program_id)
            semester = int(semester)
            target_credits = int(target_credits)
            cgpa = float(cgpa) if cgpa else 3.0
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
        
        # Validate ranges
        if not 1 <= semester <= 8:
            return jsonify({'error': 'Semester must be 1-8'}), 400
        if not 11 <= target_credits <= 24:
            return jsonify({'error': 'Credits must be 11-24'}), 400
        if cgpa and not 0.0 <= cgpa <= 4.0:
            return jsonify({'error': 'CGPA must be 0.0-4.0'}), 400
        
        # STEP 1: Get courses for this semester
        print(f"DEBUG: Getting courses for program {program_id}, semester {semester}")
        courses = get_courses_for_semester(program_id, semester)
        print(f"DEBUG: Found {len(courses) if courses else 0} courses")
        
        if not courses:
            return jsonify({'error': 'No courses available for this semester'}), 404
        
        # STEP 2: Get completed courses (all from previous semesters)
        completed_courses = get_completed_courses_from_previous_semesters(program_id, semester)
        print(f"DEBUG: Completed courses: {len(completed_courses)}")
        
        # STEP 3: Apply CSP - Filter by constraints (prerequisites, credits)
        print(f"DEBUG: Applying CSP filter with target={target_credits}")
        valid_plans = csp_filter(courses, target_credits, 11, 24, completed_courses)
        print(f"DEBUG: CSP generated {len(valid_plans)} valid plans")
        
        if not valid_plans:
            # Calculate available credits
            total_available = sum(c['credits'] for c in courses)
            return jsonify({
                'error': f'Cannot generate plan with EXACTLY {target_credits} credits. Available courses provide {total_available} total credits. The system requires exact credit match - no combinations of these courses equal {target_credits} credits. Try a different credit amount (11-24).'
            }), 400
        
        # STEP 4: Apply GA - Optimize plans based on preference
        print(f"DEBUG: Applying GA optimization with preference={preference}")
        optimized_plans = optimize(valid_plans, preference, target_credits)
        print(f"DEBUG: GA selected {len(optimized_plans)} optimal plans")
        
        if not optimized_plans:
            return jsonify({'error': 'Could not optimize plans'}), 400
        
        # STEP 5: Apply Prolog Expert System - Get advice for each plan
        print(f"DEBUG: Getting Prolog advice for each plan")
        final_plans = []
        
        for plan in optimized_plans:
            # Verify exact credit match (should always be true)
            if plan['total_credits'] != target_credits:
                print(f"WARNING: Plan has {plan['total_credits']} credits, expected {target_credits}")
                continue  # Skip plans that don't match exactly
            
            advice = get_advice(cgpa, plan['courses'])
            
            # Add prerequisite warning if any violations exist
            if not plan.get('all_prereqs_met', True):
                violations = plan.get('constraint_violations', 0)
                prereq_warning = f"⚠️ NOTE: {violations} course(s) in this plan have unmet prerequisites. Alternative courses were selected to meet your EXACT {target_credits} credit requirement."
                if 'warnings' not in advice:
                    advice['warnings'] = []
                advice['warnings'].insert(0, prereq_warning)
            else:
                # Add confirmation that credits are exact
                if 'advice' not in advice:
                    advice['advice'] = []
                advice['advice'].insert(0, f"✓ This plan provides EXACTLY {target_credits} credits as requested")
            
            final_plans.append({
                'total_credits': plan['total_credits'],
                'course_count': len(plan['courses']),
                'all_prereqs_met': plan.get('all_prereqs_met', True),
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
                ],
                'expert_advice': advice  # Prolog-based advice
            })
        
        response = {
            'success': True,
            'semester': semester,
            'cgpa': cgpa,
            'plans': final_plans,
            'method': 'CSP + GA + Prolog Expert System'
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"ERROR: Exception in api_plan: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)
