from pyswip import Prolog

prolog = Prolog()
prolog.consult("advisor.pl")

def get_advice(cgpa, courses):
    credits = sum([c[2] for c in courses])
    q = list(prolog.query(f"warn({cgpa},{credits})"))

    if q:
        return "⚠️ High risk: Reduce course load."
    else:
        return "✅ Academic plan is safe."
