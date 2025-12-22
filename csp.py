def check_prerequisites(course, completed_courses):
    """Check if all prerequisites for a course are satisfied"""
    prereqs = course.get('prerequisites', '')
    if prereqs is None or not prereqs or prereqs == '':
        return True
    prereqs = prereqs.strip()
    if not prereqs:
        return True
    
    # Get list of prerequisite course codes
    prereq_list = [p.strip() for p in prereqs.split(',')]
    completed_codes = set(c['code'] for c in completed_courses)
    
    # Check if all prerequisites are in completed courses
    for prereq in prereq_list:
        if prereq not in completed_codes:
            return False
    
    return True

def csp_filter(courses, target_credits, min_credits=11, max_credits=24, completed_courses=None):
    """
    CSP-based course filtering with hard constraints:
    1. Total credits must EXACTLY equal target_credits (NO TOLERANCE)
    2. Total credits within min_credits and max_credits
    3. No duplicate courses
    4. Prerequisites checked but courses REPLACED if not satisfied (not removed)
    5. Each course appears only once
    
    STRATEGY: Replace courses with unmet prerequisites instead of removing them
    
    Returns list of valid course combinations
    """
    if completed_courses is None:
        completed_courses = []
    
    from itertools import combinations
    
    # Separate courses by prerequisite status
    prereq_satisfied = [c for c in courses if check_prerequisites(c, completed_courses)]
    prereq_not_satisfied = [c for c in courses if not check_prerequisites(c, completed_courses)]
    no_prereqs = [c for c in courses if not c.get('prerequisites') or (c.get('prerequisites') and c.get('prerequisites', '').strip() == '')]
    
    valid_combinations = []
    
    # STRATEGY 1: Build plans preferring courses with satisfied prerequisites or no prerequisites
    # Combine satisfied + no prereqs for best options (remove duplicates by course ID)
    preferred_course_ids = set()
    preferred_courses = []
    for c in prereq_satisfied + no_prereqs:
        if c['id'] not in preferred_course_ids:
            preferred_course_ids.add(c['id'])
            preferred_courses.append(c)
    
    if len(preferred_courses) > 0:
        for r in range(1, len(preferred_courses) + 1):
            for combo in combinations(preferred_courses, r):
                total = sum(c['credits'] for c in combo)
                
                # Check if this meets our credit target - EXACT MATCH ONLY
                if total == target_credits:
                    if min_credits <= total <= max_credits:
                        valid_combinations.append({
                            'courses': list(combo),
                            'total_credits': total,
                            'constraint_violations': 0,
                            'all_prereqs_met': True
                        })
            
            # Stop if we have enough plans
            if len(valid_combinations) >= 50:
                break
    
    # STRATEGY 2: If not enough plans, include courses with unmet prerequisites
    # but mark them as having violations (to be replaced/warned)
    if len(valid_combinations) < 10:
        # Use ALL courses including those with unmet prerequisites
        all_courses = courses
        for r in range(1, min(len(all_courses) + 1, 16)):  # Limit to prevent explosion
            for combo in combinations(all_courses, r):
                total = sum(c['credits'] for c in combo)
                
                # Priority: Meet credit target EXACTLY
                if total == target_credits:
                    if min_credits <= total <= max_credits:
                        # Check how many have prerequisites met
                        prereq_met_count = sum(1 for c in combo if check_prerequisites(c, completed_courses))
                        all_met = prereq_met_count == len(combo)
                        
                        valid_combinations.append({
                            'courses': list(combo),
                            'total_credits': total,
                            'constraint_violations': len(combo) - prereq_met_count,
                            'all_prereqs_met': all_met
                        })
            
            # Stop if we have enough plans
            if len(valid_combinations) >= 50:
                break
    
    # Sort by: 1) All prerequisites met first, 2) Fewer violations, 3) Exact credit match
    valid_combinations.sort(key=lambda x: (
        not x['all_prereqs_met'],  # Prefer all prereqs met
        x['constraint_violations'],  # Fewer violations better
        abs(x['total_credits'] - target_credits)  # Exact match (should always be 0 now)
    ))
    
    return valid_combinations
