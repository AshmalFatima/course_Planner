risk(CGPA) :- CGPA < 2.5.
overload(C) :- C > 18.

warn(CGPA, Credits) :-
    risk(CGPA),
    overload(Credits).
