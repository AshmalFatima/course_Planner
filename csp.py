def csp_filter(courses, max_credits):
    valid = []
    total = 0

    for c in courses:
        if total + c[2] <= max_credits:
            valid.append(c)
            total += c[2]

    return valid
