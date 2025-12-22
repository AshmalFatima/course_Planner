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

# Insert courses - Total 114 courses
courses = [
    # CS Courses (CS001-CS024)
    (1, "CS001", "Programming Fundamentals", "Introduction to programming concepts", 4, "Easy"),
    (2, "CS002", "Data Structures", "Arrays, linked lists, stacks, queues", 4, "Balanced"),
    (3, "CS003", "Algorithms", "Sorting, searching, and algorithm design", 4, "Challenging"),
    (4, "CS004", "Object-Oriented Programming", "Classes, inheritance, and polymorphism", 4, "Balanced"),
    (5, "CS005", "Database Design", "Relational databases and SQL", 4, "Balanced"),
    (6, "CS006", "Web Development", "HTML, CSS, JavaScript basics", 3, "Easy"),
    (7, "CS007", "Computer Networks", "Network protocols and architecture", 3, "Challenging"),
    (8, "CS008", "Operating Systems", "Process management and memory", 4, "Challenging"),
    (9, "CS009", "Software Engineering", "Development methodologies", 3, "Balanced"),
    (10, "CS010", "Artificial Intelligence", "Machine learning and AI fundamentals", 3, "Challenging"),
    (11, "CS011", "Computer Graphics", "Rendering and visualization", 4, "Challenging"),
    (12, "CS012", "Mobile Development", "iOS and Android development", 4, "Balanced"),
    (13, "CS013", "Cloud Computing", "AWS, Azure, Google Cloud", 3, "Balanced"),
    (14, "CS014", "Security Fundamentals", "Cryptography and cybersecurity", 3, "Challenging"),
    (15, "CS015", "Advanced Databases", "NoSQL and distributed databases", 4, "Challenging"),
    (16, "CS016", "Machine Learning", "Supervised and unsupervised learning", 4, "Challenging"),
    (17, "CS017", "Natural Language Processing", "Text analysis and NLP", 3, "Challenging"),
    (18, "CS018", "Blockchain Technology", "Crypto and distributed ledgers", 4, "Challenging"),
    (19, "CS019", "DevOps Engineering", "CI/CD pipelines and automation", 3, "Balanced"),
    (20, "CS020", "Advanced AI Systems", "Deep learning and neural networks", 4, "Challenging"),
    (21, "CS021", "Calculus I", "Limits, derivatives, and integrals", 2, "Balanced"),
    (22, "CS022", "Linear Algebra Basics", "Matrices, vectors, transformations", 2, "Balanced"),
    (23, "CS023", "Discrete Mathematics", "Logic, sets, graph theory", 2, "Balanced"),
    (24, "CS024", "Technical Writing", "Documentation and communication", 2, "Easy"),
    
    # EE Courses (EE001-EE018)
    (25, "EE001", "Circuit Analysis", "Voltage, current, and circuit laws", 4, "Balanced"),
    (26, "EE002", "Digital Electronics", "Logic gates and digital systems", 4, "Balanced"),
    (27, "EE003", "Signals and Systems", "Signal processing fundamentals", 3, "Challenging"),
    (28, "EE004", "Electromagnetics", "Electric and magnetic fields", 4, "Challenging"),
    (29, "EE005", "Control Systems", "Feedback and control theory", 4, "Challenging"),
    (30, "EE006", "Power Systems", "Generation, transmission, distribution", 4, "Balanced"),
    (31, "EE007", "Microprocessors", "CPU architecture and assembly", 4, "Challenging"),
    (32, "EE008", "Communications", "Modulation and wireless systems", 3, "Challenging"),
    (33, "EE009", "Antenna Theory", "Antenna design and radiation", 4, "Challenging"),
    (34, "EE010", "RF Engineering", "Radio frequency circuits", 4, "Challenging"),
    (35, "EE011", "Power Electronics", "Converters and inverters", 4, "Challenging"),
    (36, "EE012", "Embedded Systems", "Microcontroller programming", 3, "Balanced"),
    (37, "EE013", "Renewable Energy", "Solar and wind systems", 4, "Balanced"),
    (38, "EE014", "Smart Grids", "Intelligent power networks", 4, "Balanced"),
    (39, "EE015", "Advanced Circuits", "Network analysis and design", 4, "Challenging"),
    (40, "EE016", "Physics II", "Electricity and magnetism", 2, "Balanced"),
    (41, "EE017", "Differential Equations", "ODE and PDE solutions", 2, "Challenging"),
    (42, "EE018", "Engineering Lab I", "Hands-on electrical experiments", 2, "Balanced"),
    
    # ME Courses (ME001-ME018)
    (43, "ME001", "Thermodynamics", "Heat and energy fundamentals", 4, "Challenging"),
    (44, "ME002", "Fluid Mechanics", "Flow and pressure analysis", 4, "Challenging"),
    (45, "ME003", "Mechanics of Materials", "Stress and strain analysis", 4, "Challenging"),
    (46, "ME004", "Machine Design", "Component and system design", 4, "Balanced"),
    (47, "ME005", "Heat Transfer", "Conduction, convection, radiation", 3, "Challenging"),
    (48, "ME006", "Manufacturing Processes", "Machining and fabrication", 4, "Balanced"),
    (49, "ME007", "Robotics", "Robot kinematics and control", 4, "Challenging"),
    (50, "ME008", "CAD Systems", "3D modeling and simulation", 3, "Easy"),
    (51, "ME009", "Aerodynamics", "Lift, drag, and flight dynamics", 4, "Challenging"),
    (52, "ME010", "Combustion", "Fuel burning and emissions", 4, "Challenging"),
    (53, "ME011", "Vibration Analysis", "Natural frequencies and damping", 4, "Challenging"),
    (54, "ME012", "Control of Mechanical Systems", "Actuators and feedback", 4, "Challenging"),
    (55, "ME013", "Computational Fluid Dynamics", "CFD simulation and analysis", 4, "Challenging"),
    (56, "ME014", "Energy Conversion", "Power generation systems", 4, "Balanced"),
    (57, "ME015", "Engineering Optimization", "Design optimization methods", 3, "Challenging"),
    (58, "ME016", "Applied Physics", "Mechanics and kinematics", 2, "Balanced"),
    (59, "ME017", "Engineering Drawing", "Technical sketching", 2, "Easy"),
    (60, "ME018", "Workshop Lab", "Hands-on manufacturing", 2, "Balanced"),
    
    # CE Courses (CE001-CE018)
    (61, "CE001", "Engineering Mechanics", "Statics and dynamics", 4, "Balanced"),
    (62, "CE002", "Concrete Design", "Reinforced concrete structures", 4, "Challenging"),
    (63, "CE003", "Structural Analysis", "Force and moment analysis", 4, "Challenging"),
    (64, "CE004", "Foundation Engineering", "Soil mechanics and footings", 4, "Challenging"),
    (65, "CE005", "Transportation Engineering", "Roads and traffic design", 3, "Balanced"),
    (66, "CE006", "Surveying", "Land measurement and mapping", 3, "Easy"),
    (67, "CE007", "Building Construction", "Materials and methods", 3, "Balanced"),
    (68, "CE008", "Water Resources", "Hydraulics and water systems", 4, "Challenging"),
    (69, "CE009", "Steel Design", "Steel structures and connections", 4, "Challenging"),
    (70, "CE010", "Environmental Engineering", "Pollution and treatment", 4, "Challenging"),
    (71, "CE011", "Pavement Design", "Road pavement systems", 3, "Balanced"),
    (72, "CE012", "Bridge Engineering", "Bridge design and analysis", 4, "Challenging"),
    (73, "CE013", "Earthquake Engineering", "Seismic design", 4, "Challenging"),
    (74, "CE014", "Project Management", "Planning and control", 3, "Balanced"),
    (75, "CE015", "Urban Planning", "City planning", 3, "Balanced"),
    (76, "CE016", "Engineering Geology", "Rock properties", 2, "Balanced"),
    (77, "CE017", "CAD for Civil Engineering", "AutoCAD", 2, "Easy"),
    (78, "CE018", "Site Inspection", "Field work", 2, "Balanced"),
    
    # BBA Courses (BBA001-BBA018)
    (79, "BBA001", "Financial Accounting", "Accounting principles", 3, "Balanced"),
    (80, "BBA002", "Corporate Finance", "Capital budgeting", 4, "Challenging"),
    (81, "BBA003", "Business Management", "Organizational behavior", 3, "Easy"),
    (82, "BBA004", "Marketing Management", "Product and promotion", 3, "Balanced"),
    (83, "BBA005", "Human Resource Management", "Recruitment and development", 3, "Easy"),
    (84, "BBA006", "Operations Management", "Production and supply chain", 4, "Balanced"),
    (85, "BBA007", "Business Economics", "Micro and macroeconomics", 4, "Challenging"),
    (86, "BBA008", "Business Law", "Contracts and law", 3, "Balanced"),
    (87, "BBA009", "Entrepreneurship", "Business planning", 3, "Easy"),
    (88, "BBA010", "Digital Marketing", "Online marketing", 3, "Balanced"),
    (89, "BBA011", "Strategic Management", "Business strategy", 4, "Challenging"),
    (90, "BBA012", "International Business", "Global commerce", 3, "Balanced"),
    (91, "BBA013", "Risk Management", "Insurance and hedging", 3, "Balanced"),
    (92, "BBA014", "Investment Analysis", "Valuation", 4, "Challenging"),
    (93, "BBA015", "Organizational Development", "Change management", 3, "Balanced"),
    (94, "BBA016", "Business Statistics", "Data analysis", 2, "Balanced"),
    (95, "BBA017", "Ethics in Business", "Corporate ethics", 2, "Easy"),
    (96, "BBA018", "Public Relations", "Communications", 2, "Easy"),
    
    # SE Courses (SE001-SE018)
    (97, "SE001", "Software Design Patterns", "Design patterns", 4, "Challenging"),
    (98, "SE002", "Software Testing", "Testing and QA", 4, "Balanced"),
    (99, "SE003", "Agile Development", "Scrum and agile", 3, "Easy"),
    (100, "SE004", "DevOps Fundamentals", "CI/CD", 4, "Balanced"),
    (101, "SE005", "System Architecture", "System design", 4, "Challenging"),
    (102, "SE006", "Code Quality", "Refactoring", 3, "Balanced"),
    (103, "SE007", "Requirements Analysis", "Requirements gathering", 3, "Balanced"),
    (104, "SE008", "Database Systems", "Advanced database", 4, "Challenging"),
    (105, "SE009", "Web Application Security", "Security", 4, "Challenging"),
    (106, "SE010", "Microservices Architecture", "Microservices", 4, "Challenging"),
    (107, "SE011", "Cloud Architecture", "Cloud design", 4, "Challenging"),
    (108, "SE012", "Machine Learning Engineering", "ML systems", 4, "Challenging"),
    (109, "SE013", "API Design", "API design", 3, "Balanced"),
    (110, "SE014", "Performance Optimization", "Performance tuning", 4, "Challenging"),
    (111, "SE015", "Software Documentation", "Technical writing", 3, "Easy"),
    (112, "SE016", "Software Metrics", "Quality metrics", 2, "Balanced"),
    (113, "SE017", "Project Management", "Project planning", 2, "Balanced"),
    (114, "SE018", "Team Leadership", "Team management", 2, "Easy"),
]

cur.executemany("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)", courses)

# Function to assign courses to programs (each semester gets 12-13 courses)
# IMPORTANT: Ensure each semester of each program has 2, 3, and 4-credit courses
def create_program_mappings():
    mappings = []
    
    # Define credit categories by discipline (based on actual course definitions)
    credit_categories = {
        "CS": {
            "2": [21, 22, 23, 24],
            "3": [6, 7, 9, 10, 13, 14, 17, 19],
            "4": [1, 2, 3, 4, 5, 8, 11, 12, 15, 16, 18, 20]
        },
        "EE": {
            "2": [40, 41, 42],
            "3": [27, 32, 36],
            "4": [25, 26, 28, 29, 30, 31, 33, 34, 35, 37, 38, 39]
        },
        "ME": {
            "2": [58, 59, 60],
            "3": [47, 50, 57],
            "4": [43, 44, 45, 46, 48, 49, 51, 52, 53, 54, 55, 56]
        },
        "CE": {
            "2": [76, 77, 78],
            "3": [65, 66, 67, 71, 74, 75],
            "4": [61, 62, 63, 64, 68, 69, 70, 72, 73]
        },
        "BBA": {
            "2": [94, 95, 96],
            "3": [79, 81, 82, 83, 86, 87, 88, 90, 91, 93],
            "4": [80, 84, 85, 89, 92]
        },
        "SE": {
            "2": [112, 113, 114],
            "3": [99, 102, 103, 109, 111],
            "4": [97, 98, 100, 101, 104, 105, 106, 107, 108, 110]
        }
    }
    
    # Discipline to course range mapping
    discipline_ranges = {
        "CS": (1, 24, list(range(1, 6))),
        "EE": (25, 42, list(range(6, 10))),
        "ME": (43, 60, list(range(10, 14))),
        "CE": (61, 78, list(range(14, 18))),
        "BBA": (79, 96, list(range(18, 23))),
        "SE": (97, 114, list(range(23, 27)))
    }
    
    # For each discipline
    for discipline, (start_id, end_id, prog_ids) in discipline_ranges.items():
        creds_2 = credit_categories[discipline]["2"]
        creds_3 = credit_categories[discipline]["3"]
        creds_4 = credit_categories[discipline]["4"]
        
        # For each program in discipline
        for prog_id in prog_ids:
            # For each semester
            for sem in range(1, 9):
                num_courses = 12 if sem % 2 == 0 else 13
                selected = set()
                
                # GUARANTEED: Always include at least one from each credit category
                # Using different indices to get variety across semesters
                selected.add(creds_2[(sem - 1) % len(creds_2)])
                selected.add(creds_3[(sem) % len(creds_3)])
                selected.add(creds_4[(sem + 1) % len(creds_4)])
                
                # Fill remaining with other courses (prioritizing missing credit types later)
                all_courses = list(range(start_id, end_id + 1))
                remaining = num_courses - len(selected)
                available = [c for c in all_courses if c not in selected]
                
                # Add remaining courses
                for i in range(remaining):
                    if i < len(available):
                        idx = (sem * i + prog_id * 3 + i) % len(available)
                        selected.add(available[idx])
                
                # Final safety check - ensure all credit types are present
                has_2 = any(c in creds_2 for c in selected)
                has_3 = any(c in creds_3 for c in selected)
                has_4 = any(c in creds_4 for c in selected)
                
                # If any missing, add them
                if not has_2:
                    selected.add(creds_2[(sem - 1) % len(creds_2)])
                if not has_3:
                    selected.add(creds_3[(sem) % len(creds_3)])
                if not has_4:
                    selected.add(creds_4[(sem + 1) % len(creds_4)])
                
                # Add to mappings with prerequisites
                for course_id in selected:
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
print(f"   CS-AI Semester 1: {sem1_count} courses")
print(f"   Avg per program: {mappings_count / 26:.1f} courses per semester")
