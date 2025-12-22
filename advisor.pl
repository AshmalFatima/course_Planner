% Risk assessment rules
risk(CGPA) :- CGPA < 2.5.
moderate_risk(CGPA) :- CGPA >= 2.5, CGPA < 3.0.
safe(CGPA) :- CGPA >= 3.0.

% Load assessment
overload(Credits) :- Credits > 18.
heavy_load(Credits) :- Credits >= 15, Credits =< 18.
moderate_load(Credits) :- Credits >= 12, Credits < 15.
light_load(Credits) :- Credits < 12.

% Difficulty assessment
too_many_hard(HardCount) :- HardCount > 4.
balanced_difficulty(HardCount, EasyCount) :- 
    HardCount =< 4, 
    EasyCount >= 2.

% Main warning rules
warn(CGPA, Credits) :-
    risk(CGPA),
    overload(Credits).

warn_moderate(CGPA, Credits) :-
    moderate_risk(CGPA),
    heavy_load(Credits).

warn_difficulty(CGPA, HardCount) :-
    risk(CGPA),
    too_many_hard(HardCount).

% Recommendations
recommend_reduce(CGPA, Credits) :-
    risk(CGPA),
    Credits > 15.

recommend_limit_hard(CGPA, HardCount) :-
    moderate_risk(CGPA),
    HardCount > 3.

recommend_increase(CGPA, Credits) :-
    safe(CGPA),
    light_load(Credits).

% Semester progression rules
can_take_advanced(CGPA) :- CGPA >= 2.5.
should_repeat(CGPA) :- CGPA < 2.0.
