from pyswip import Prolog

prolog = Prolog()
prolog.consult("advisor.pl")

def get_advice(cgpa, courses):
    """
    Get comprehensive academic advice based on CGPA and course plan
    """
    credits = sum([c['credits'] for c in courses])
    
    # Count difficulty levels
    hard_count = len([c for c in courses if c['difficulty'] == 'Challenging'])
    easy_count = len([c for c in courses if c['difficulty'] == 'Easy'])
    balanced_count = len([c for c in courses if c['difficulty'] == 'Balanced'])
    
    advice = []
    warnings = []
    
    # Check critical warnings
    q = list(prolog.query(f"warn({cgpa},{credits})"))
    if q:
        warnings.append("⚠️ HIGH RISK: Low CGPA + Heavy credit load")
        advice.append("Consider reducing to 12-15 credits")
    
    # Check moderate warnings
    q = list(prolog.query(f"warn_moderate({cgpa},{credits})"))
    if q:
        warnings.append("⚠️ MODERATE RISK: CGPA below 3.0 with heavy load")
        advice.append("Monitor workload carefully")
    
    # Check difficulty warnings
    q = list(prolog.query(f"warn_difficulty({cgpa},{hard_count})"))
    if q:
        warnings.append("⚠️ TOO MANY CHALLENGING COURSES")
        advice.append(f"Limit challenging courses to 3-4 (currently {hard_count})")
    
    # Recommendations
    q = list(prolog.query(f"recommend_reduce({cgpa},{credits})"))
    if q and not warnings:
        advice.append(f"💡 Recommend reducing to 12-15 credits given CGPA {cgpa}")
    
    q = list(prolog.query(f"recommend_limit_hard({cgpa},{hard_count})"))
    if q and not warnings:
        advice.append(f"💡 Consider limiting challenging courses (currently {hard_count})")
    
    q = list(prolog.query(f"recommend_increase({cgpa},{credits})"))
    if q:
        advice.append(f"✅ Good CGPA! You can handle more credits if desired")
    
    # General status
    if not warnings:
        if cgpa >= 3.0:
            warnings.append("✅ SAFE: Academic plan is appropriate")
        elif cgpa >= 2.5:
            warnings.append("✓ ACCEPTABLE: Plan is manageable")
    
    return {
        'warnings': warnings,
        'advice': advice,
        'stats': {
            'total_credits': credits,
            'easy_courses': easy_count,
            'balanced_courses': balanced_count,
            'challenging_courses': hard_count,
            'cgpa': cgpa
        }
    }
