def fitness(plan, preference, target_credits):
    """
    Calculate fitness score for a complete plan
    Higher score = better plan
    
    Factors:
    1. Prerequisite satisfaction (CRITICAL - highest priority)
    2. Credit EXACT match (must be exact, severe penalty otherwise)
    3. Difficulty match with preference
    4. Difficulty balance (not all hard or all easy)
    5. Course count (prefer fewer courses for same credits)
    """
    courses = plan['courses']
    total_credits = plan['total_credits']
    
    # Factor 0: Prerequisite satisfaction (CRITICAL)
    # Plans with all prerequisites met get massive bonus
    prereq_bonus = 0
    if plan.get('all_prereqs_met', True):
        prereq_bonus = 100
    else:
        # Heavy penalty for each violation
        violations = plan.get('constraint_violations', 0)
        prereq_bonus = -violations * 50
    
    # Factor 1: Credit exactness (must be EXACT - heavy penalty for any deviation)
    if total_credits != target_credits:
        # This should never happen if CSP works correctly, but severe penalty if it does
        credit_penalty = abs(total_credits - target_credits) * 1000
    else:
        credit_penalty = 0  # Perfect match
    
    # Factor 2: Difficulty preference match
    difficulty_score = 0
    difficulty_counts = {'Easy': 0, 'Balanced': 0, 'Challenging': 0}
    
    for c in courses:
        difficulty = c['difficulty']
        difficulty_counts[difficulty] += 1
        
        if preference == "Easy":
            if difficulty == "Easy":
                difficulty_score += 3
            elif difficulty == "Balanced":
                difficulty_score += 1
        elif preference == "Balanced":
            if difficulty == "Balanced":
                difficulty_score += 3
            elif difficulty in ["Easy", "Challenging"]:
                difficulty_score += 2
        else:  # Challenging
            if difficulty == "Challenging":
                difficulty_score += 3
            elif difficulty == "Balanced":
                difficulty_score += 1
    
    # Factor 3: Balance bonus (reward having mix of difficulties)
    unique_difficulties = len([v for v in difficulty_counts.values() if v > 0])
    balance_bonus = unique_difficulties * 2
    
    # Factor 4: Efficiency bonus (prefer fewer courses)
    efficiency_bonus = (20 - len(courses)) * 0.5
    
    # Total fitness (prerequisite satisfaction dominates)
    total_fitness = prereq_bonus + difficulty_score - credit_penalty + balance_bonus + efficiency_bonus
    
    return total_fitness

def optimize(plans, preference, target_credits):
    """
    Optimize and rank plans using GA-inspired fitness function
    Returns top 5 plans sorted by fitness
    """
    if not plans:
        return []
    
    # Score each plan
    scored_plans = []
    for plan in plans:
        score = fitness(plan, preference, target_credits)
        scored_plans.append({
            'plan': plan,
            'fitness': score
        })
    
    # Sort by fitness (descending)
    scored_plans.sort(key=lambda x: x['fitness'], reverse=True)
    
    # Return top 5 plans
    return [sp['plan'] for sp in scored_plans[:5]]
