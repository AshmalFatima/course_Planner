def fitness(course, preference):
    difficulty = course[3]

    if preference == "Easy":
        return -difficulty
    elif preference == "Balanced":
        return 5 - abs(5 - difficulty)
    else:
        return difficulty

def optimize(courses, preference):
    scored = []

    for c in courses:
        scored.append((fitness(c, preference), c))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [x[1] for x in scored[:4]]
