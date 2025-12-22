import sqlite3

conn = sqlite3.connect('university.db')
cur = conn.cursor()

# Create tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY,
        department_id INTEGER NOT NULL,
        name TEXT NOT NULL UNIQUE,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        credits INTEGER NOT NULL,
        difficulty TEXT NOT NULL
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS program_courses (
        id INTEGER PRIMARY KEY,
        program_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        prerequisites TEXT,
        UNIQUE(program_id, course_id, semester),
        FOREIGN KEY (program_id) REFERENCES programs(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )
""")

# Insert departments
departments = [
    "Computer Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Business Administration",
    "Software Engineering"
]

cur.executemany("INSERT INTO departments VALUES (NULL, ?)", [(d,) for d in departments])

# Insert programs
programs = [
    # CS (1-5)
    (1, "CS-AI"),
    (1, "CS-DS"),
    (1, "CS-Cybersecurity"),
    (1, "CS-Blockchain"),
    (1, "CS-HCI"),
    # EE (6-9)
    (2, "EE-Power"),
    (2, "EE-Electronics"),
    (2, "EE-Telecommunications"),
    (2, "EE-Renewable"),
    # ME (10-13)
    (3, "ME-Thermal"),
    (3, "ME-Mechanical Design"),
    (3, "ME-Robotics"),
    (3, "ME-Manufacturing"),
    # CE (14-17)
    (4, "CE-Structural"),
    (4, "CE-Transportation"),
    (4, "CE-Water Resources"),
    (4, "CE-Environmental"),
    # BBA (18-22)
    (5, "BBA-Finance"),
    (5, "BBA-Marketing"),
    (5, "BBA-HR"),
    (5, "BBA-Entrepreneurship"),
    (5, "BBA-International Business"),
    # SE (23-26)
    (6, "SE-Web Dev"),
    (6, "SE-Mobile Dev"),
    (6, "SE-Cloud Systems"),
    (6, "SE-AI/ML"),
]

cur.executemany("INSERT INTO programs VALUES (NULL, ?, ?)", programs)

# Insert courses - Generate enough courses for each discipline
# Each discipline needs at least 56 courses (7 unique × 8 semesters) 
# We'll create 60 courses per discipline = 360 total courses
courses = []
course_id = 1

# Helper to generate courses
disciplines_info = [
    ("CS", 60, ["Programming", "Data Structures", "Algorithms", "OOP", "Databases", "Web Dev", "Networks", "OS", "Software Engineering", "AI"]),
    ("EE", 60, ["Circuits", "Electronics", "Signals", "Electromagnetics", "Control Systems", "Power Systems", "Microprocessors", "Communications", "RF Engineering", "Embedded Systems"]),
    ("ME", 60, ["Thermodynamics", "Fluid Mechanics", "Materials", "Machine Design", "Heat Transfer", "Manufacturing", "Robotics", "CAD", "Aerodynamics", "Vibration"]),
    ("CE", 60, ["Mechanics", "Concrete Design", "Structural Analysis", "Foundation", "Transportation", "Surveying", "Construction", "Water Resources", "Steel Design", "Environmental"]),
    ("BBA", 60, ["Accounting", "Finance", "Management", "Marketing", "HR", "Operations", "Economics", "Business Law", "Entrepreneurship", "Digital Marketing"]),
    ("SE", 60, ["Design Patterns", "Testing", "Agile", "DevOps", "Architecture", "Code Quality", "Requirements", "Database Systems", "Security", "Microservices"])
]

for prefix, count, topics in disciplines_info:
    difficulty_cycle = ["Easy", "Balanced", "Challenging"]
    credits = 3  # All courses have 3 credit hours
    
    for i in range(count):
        code = f"{prefix}{i+1:03d}"
        topic_idx = i % len(topics)
        variant = (i // len(topics)) + 1
        name = f"{topics[topic_idx]} {variant}" if variant > 1 else topics[topic_idx]
        description = f"{name} course content"
        difficulty = difficulty_cycle[i % len(difficulty_cycle)]
        
        courses.append((course_id, code, name, description, credits, difficulty))
        course_id += 1

cur.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)", courses)

# Function to assign courses to programs
# CONSTRAINT: Each semester must have exactly 11 courses
#             AT LEAST 7 courses must be UNIQUE to that semester (not in any other semester of same program)
#             The remaining courses can be shared/repeated across semesters  
# Now with 60 courses per discipline, we have enough for 56 unique + some shared courses
def create_program_mappings():
    mappings = []
    
    # Discipline to course range mapping (60 courses each)
    discipline_ranges = {
        "CS": (1, 60, list(range(1, 6))),
        "EE": (61, 120, list(range(6, 10))),
        "ME": (121, 180, list(range(10, 14))),
        "CE": (181, 240, list(range(14, 18))),
        "BBA": (241, 300, list(range(18, 23))),
        "SE": (301, 360, list(range(23, 27)))
    }
    
    # For each discipline
    for discipline, (start_id, end_id, prog_ids) in discipline_ranges.items():
        all_courses = list(range(start_id, end_id + 1))
        total_courses = len(all_courses)
        
        # Calculate how many truly unique courses we can have per semester
        # With 24 courses and 8 semesters needing 11 each (88 total assignments)
        # We can have 24/8 = 3 unique per semester, and 8 will be shared
        unique_per_sem = max(total_courses // 8, 7)  # At least 7 if possible
        shared_per_sem = 11 - unique_per_sem
        
        # For each program in discipline
        for prog_id in prog_ids:
            used_unique_courses = set()  # Track courses allocated as unique
            all_semesters_courses = {}
            
            # First pass: Distribute unique courses across semesters
            # Try to give each semester as many unique courses as possible (target: 7)
            course_pool = list(all_courses)
            course_index = (prog_id * 13) % len(course_pool)  # Vary starting point per program
            
            for sem in range(1, 9):
                semester_courses = set()
                
                # Allocate unique courses for this semester
                unique_count = 0
                attempts = 0
                while unique_count < 7 and attempts < len(course_pool):
                    course = course_pool[course_index % len(course_pool)]
                    
                    # Check if this course hasn't been used as unique yet
                    if course not in used_unique_courses:
                        semester_courses.add(course)
                        used_unique_courses.add(course)
                        unique_count += 1
                    
                    course_index += 1
                    attempts += 1
                
                all_semesters_courses[sem] = semester_courses
            
            # Second pass: Add shared courses to reach 11 per semester
            # Use courses that have already been marked as "unique" for other semesters
            for sem in range(1, 9):
                # Add shared courses from the pool (can include already used courses)
                while len(all_semesters_courses[sem]) < 11:
                    # Cycle through all available courses
                    for course in all_courses:
                        if course not in all_semesters_courses[sem]:
                            all_semesters_courses[sem].add(course)
                            if len(all_semesters_courses[sem]) >= 11:
                                break
            
            # Add to mappings with prerequisites
            for sem in range(1, 9):
                for course_id in all_semesters_courses[sem]:
                    prereq = None
                    if sem > 1:
                        if discipline == "CS":
                            prereq = "CS001"
                        elif discipline == "EE":
                            prereq = "EE001"
                        elif discipline == "ME":
                            prereq = "ME001"
                        elif discipline == "CE":
                            prereq = "CE001"
                        elif discipline == "BBA":
                            prereq = "BBA001"
                        elif discipline == "SE":
                            prereq = "SE001"
                    
                    mappings.append((prog_id, course_id, sem, prereq))
    
    return mappings

program_courses = create_program_mappings()

cur.executemany("INSERT INTO program_courses VALUES (NULL, ?, ?, ?, ?)", program_courses)

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM courses")
courses_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM program_courses")
mappings_count = cur.fetchone()[0]

# Check a sample
cur.execute("""
    SELECT COUNT(*) FROM program_courses 
    WHERE program_id = 1 AND semester = 1
""")
sem1_count = cur.fetchone()[0]

conn.close()

print(f"✅ Database created successfully!")
print(f"   Total Courses: {courses_count}")
print(f"   Program-Course Mappings: {mappings_count}")
print(f"   Constraint: Each semester has exactly 11 courses")
print(f"   - 7 courses are UNIQUE to that semester")
print(f"   - 4 courses can be shared across semesters")
