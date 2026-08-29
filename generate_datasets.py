import os
import csv
import json

DATASETS_DIR = "datasets"
JD_DIR = os.path.join(DATASETS_DIR, "job_descriptions")
os.makedirs(JD_DIR, exist_ok=True)

# 1. USERS DATASET
users = [
    {
        "username": "sivasubramaniyan",
        "name": "Dr. Sivasubramaniyan",
        "role": "admin",
        "email": "placement.head@college.edu",
        "password_raw": "sivu@12345",
        "active": "true"
    },
    {
        "username": "jeyakannan",
        "name": "Prof. Jeyakannan",
        "role": "manager",
        "email": "placement.mgr@college.edu",
        "password_raw": "jk@12345",
        "active": "true"
    }
]

for i in range(1, 11):
    users.append({
        "username": f"lead-{i}",
        "name": f"Student Placement Lead {i}",
        "role": "lead",
        "email": f"lead{i}@college.edu",
        "password_raw": f"lead{i}@12345",
        "active": "true"
    })

with open(os.path.join(DATASETS_DIR, "users.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["username", "name", "role", "email", "password_raw", "active"])
    writer.writeheader()
    writer.writerows(users)

# 2. 50 REALISTIC STUDENTS
first_names = [
    "Karthikeyan", "Arun", "Priya", "Sanjay", "Deepika", "Vignesh", "Ananya", "Rahul", "Sneha", "Gokul",
    "Divya", "Praveen", "Meena", "Harish", "Pavithra", "Manoj", "Keerthana", "Surya", "Naveen", "Abinaya",
    "Santhosh", "Kavitha", "Dinesh", "Swetha", "Vijay", "Aishwarya", "Balaji", "Gayathri", "Ajay", "Kavya",
    "Senthil", "Nandhini", "Ranjith", "Monisha", "Manikandan", "Preethi", "Ganesh", "Sandhya", "Subash", "Lavanya",
    "Madhan", "Reshma", "Vasanth", "Shalini", "Kishore", "Mythili", "Gopinath", "Harini", "Ashok", "Sujitha"
]

last_names = [
    "T", "Kumar", "Dharshini", "R", "S", "M", "V", "Sundaram", "Natarajan", "Selvam",
    "Babu", "Moorthy", "Krishnan", "Raj", "Pandian", "Ganesan", "Chandar", "Venkatesh", "Prasad", "Balan"
]

departments = ["CSE", "IT", "AI&DS", "ECE", "EEE", "MECH"]
genders = ["Male", "Female"]
student_types = ["Day Scholar", "Hosteller"]

students = []

# Curated set of high quality portrait photos
avatars = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop&q=80"
]

placed_companies_pool = [
    ("Zoho Corporation", 8.4),
    ("Amazon Development Centre", 24.0),
    ("Freshworks", 12.5),
    ("Cognizant", 6.5),
    ("TCS Digital & Ninja", 7.2),
    ("Infosys Ltd", 9.0),
    ("Kaar Technologies", 8.0),
    ("Accenture India", 6.5),
    ("Solartis Technology Services", 6.0),
    ("Hexaware Technologies", 5.5)
]

for idx in range(50):
    fn = first_names[idx % len(first_names)]
    ln = last_names[idx % len(last_names)]
    name = f"{fn} {ln}"
    dept = departments[idx % len(departments)]
    year_prefix = "23" if idx < 30 else "22"
    reg_no = f"{year_prefix}{dept[:2].upper()}{str(idx+1).zfill(3)}"
    gender = "Female" if idx % 3 == 0 else "Male"
    s_type = student_types[idx % 2]
    phone = f"98{str(idx+10).zfill(2)}5432{str(idx%10)}{str((idx+3)%10)}"
    email = f"{fn.lower()}.{ln.lower()}{idx+1}@college.edu"
    
    # Academic %
    sslc = round(80.0 + (idx * 0.37) % 19.5, 1)
    hsc = round(78.0 + (idx * 0.41) % 21.0, 1)
    ug = round(72.0 + (idx * 0.53) % 24.5, 2)
    pg = round(75.0 + (idx * 0.3) % 20.0, 2) if idx % 5 == 0 else ""
    
    # Status distribution: 18 PLACED, 24 YTPP, 8 UNENROLLED
    if idx < 18:
        p_status = "PLACED"
        comp_info = placed_companies_pool[idx % len(placed_companies_pool)]
        p_comp = comp_info[0]
        p_ctc = comp_info[1]
    elif idx < 42:
        p_status = "YTPP"
        p_comp = "YTPP"
        p_ctc = ""
    else:
        p_status = "UNENROLLED"
        p_comp = "Unenrolled"
        p_ctc = ""
        
    student = {
        "reg_number": reg_no,
        "name": name,
        "department": dept,
        "gender": gender,
        "student_type": s_type,
        "phone": phone,
        "email": email,
        "sslc_percentage": sslc,
        "hsc_percentage": hsc,
        "ug_percentage": ug,
        "pg_percentage": pg,
        "github_link": f"https://github.com/{fn.lower()}-{ln.lower()}",
        "linkedin_link": f"https://linkedin.com/in/{fn.lower()}-{ln.lower()}",
        "resume_url": f"https://example.com/resumes/{reg_no}_resume.pdf",
        "self_intro_link": f"https://youtu.be/intro_{reg_no}",
        "photo_url": avatars[idx % len(avatars)],
        "portfolio_link": f"https://{fn.lower()}portfolio.dev",
        "year_of_graduation": 2025 if year_prefix == "23" else 2024,
        "placement_status": p_status,
        "placed_company": p_comp,
        "ctc_lpa": p_ctc
    }
    students.append(student)

with open(os.path.join(DATASETS_DIR, "students.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(students[0].keys()))
    writer.writeheader()
    writer.writerows(students)

# 3. 25 REALISTIC COMPANIES
companies_raw = [
    ("Zoho Corporation", "Chennai", "https://zohocorp.com", "SaaS Enterprise Software & Cloud Suite", "9876500001", "hr.campus@zohocorp.com", "Estancia IT Park, Guduvanchery, Chennai", "APPROVED", "DRIVE_COMPLETED", "lead-1", "sivasubramaniyan", "2026-08-10", 6),
    ("Amazon Development Centre", "Chennai", "https://amazon.jobs", "E-Commerce, Cloud AWS & AI Solutions", "9876500002", "in-campus@amazon.com", "SP Infocity, Perungudi, Chennai", "APPROVED", "DRIVE_COMPLETED", "lead-2", "sivasubramaniyan", "2026-08-12", 2),
    ("Freshworks", "Chennai", "https://freshworks.com", "Customer Engagement & Helpdesk SaaS Solutions", "9876500003", "university-hiring@freshworks.com", "Global Infocity, Perungudi, Chennai", "APPROVED", "DRIVE_COMPLETED", "lead-1", "sivasubramaniyan", "2026-08-15", 3),
    ("Cognizant", "Coimbatore", "https://cognizant.com", "Global IT Consulting, Digital Engineering & AI", "9876500004", "campus.south@cognizant.com", "CHIL SEZ, Saravanampatti, Coimbatore", "APPROVED", "DRIVE_COMPLETED", "lead-3", "sivasubramaniyan", "2026-08-18", 4),
    ("TCS Digital & Ninja", "Chennai", "https://tcs.com", "Enterprise IT Services and Digital Solutions", "9876500005", "campus.tcs@tcs.com", "SIPCOT IT Park, Siruseri, Chennai", "APPROVED", "DRIVE_COMPLETED", "lead-4", "sivasubramaniyan", "2026-08-20", 3),
    ("Infosys Ltd", "Mysore", "https://infosys.com", "Next-Gen Digital Services and IT Consulting", "9876500006", "talent_acquisition@infosys.com", "Hebbal Industrial Area, Mysore", "APPROVED", "HOT", "lead-2", "sivasubramaniyan", "2026-09-05", 0),
    ("Kaar Technologies", "Chennai", "https://kaartech.com", "Global SAP Digital Transformation Consulting", "9876500007", "hr@kaartech.com", "Sholinganallur, OMR, Chennai", "APPROVED", "HOT", "lead-5", "sivasubramaniyan", "2026-09-08", 0),
    ("Solartis Technology Services", "Madurai", "https://solartis.com", "Insurance Automation Platform & SaaS", "9876500008", "madurai_recruitment@solartis.com", "ELCOT IT Park, Ilandhaikulam, Madurai", "APPROVED", "HOT", "lead-6", "sivasubramaniyan", "2026-09-12", 0),
    ("Hexaware Technologies", "Chennai", "https://hexaware.com", "Automation-led Digital IT Solutions", "9876500009", "campus@hexaware.com", "SIPCOT IT Park, Navalur, Chennai", "APPROVED", "HOT", "lead-3", "sivasubramaniyan", "2026-09-15", 0),
    ("Accenture India", "Bengaluru", "https://accenture.com", "Strategy, Consulting, Cloud & Technology", "9876500010", "accenture.campus@accenture.com", "Prestige Tech Park, Bengaluru", "APPROVED", "HOT", "lead-7", "sivasubramaniyan", "2026-09-20", 0),
    ("Wipro Technologies", "Bengaluru", "https://wipro.com", "Cognitive Computing and Cloud Services", "9876500011", "wipro.earlycareers@wipro.com", "Sarjapur Road, Bengaluru", "APPROVED", "WARM", "lead-8", "sivasubramaniyan", "", 0),
    ("HCL Technologies", "Chennai", "https://hcltech.com", "Supercharging Progress with Digital Solutions", "9876500012", "freshers@hcl.com", "Elcot SEZ, Sholinganallur, Chennai", "APPROVED", "WARM", "lead-1", "sivasubramaniyan", "", 0),
    ("Renault Nissan Technology", "Chennai", "https://rntbci.in", "Automotive Embedded Systems & Software", "9876500013", "careers@rntbci.in", "Ascendas Mahindra World City, Chengalpattu", "APPROVED", "WARM", "lead-9", "sivasubramaniyan", "", 0),
    ("L&T Technology Services", "Mysore", "https://ltts.com", "Engineering Research & Product Development", "9876500014", "talent@ltts.com", "KIADB Industrial Area, Hebbal, Mysore", "APPROVED", "WARM", "lead-10", "sivasubramaniyan", "", 0),
    ("BOSCH Global Software", "Coimbatore", "https://bosch.in", "Mobility Solutions & Embedded Software", "9876500015", "campus.bosch@in.bosch.com", "TIDEL Park, Peelamedu, Coimbatore", "APPROVED", "WARM", "lead-4", "sivasubramaniyan", "", 0),
    ("Cognitive Scale AI", "Hyderabad", "https://cognitivescale.com", "Applied Generative AI & Decision Intelligence", "9876500016", "hr@cognitivescale.com", "HITEC City, Madhapur, Hyderabad", "APPROVED", "COLD", "lead-5", "sivasubramaniyan", "", 0),
    ("Trimble Information", "Chennai", "https://trimble.com", "Geospatial Hardware, Software & Digital Twin", "9876500017", "india_recruitment@trimble.com", "TIDEL Park, Taramani, Chennai", "APPROVED", "COLD", "lead-6", "sivasubramaniyan", "", 0),
    ("Tiger Analytics", "Chennai", "https://tigeranalytics.com", "AI & Advanced Data Science Consulting", "9876500018", "careers@tigeranalytics.com", "Ascendas Tech Park, Taramani, Chennai", "PENDING", "COLD", "lead-2", "", "", 0),
    ("Chargebee Technologies", "Chennai", "https://chargebee.com", "Subscription Billing and Revenue Management", "9876500019", "talent@chargebee.com", "DLF IT Park, Ramapuram, Chennai", "PENDING", "COLD", "lead-7", "", "", 0),
    ("Kissflow Software", "Chennai", "https://kissflow.com", "Low-code Workflow & Digital Workplace Suite", "9876500020", "careers@kissflow.com", "World Trade Center, Perungudi, Chennai", "PENDING", "COLD", "lead-8", "", "", 0),
    ("Vuram Automation", "Trichy", "https://vuram.com", "Hyperautomation & Enterprise BPM Solutions", "9876500021", "bpm.hr@vuram.com", "ELCOT SEZ, Navalpattu, Trichy", "PENDING", "COLD", "lead-9", "", "", 0),
    ("LatentView Analytics", "Chennai", "https://latentview.com", "Decision Sciences and Business Analytics", "9876500022", "talent@latentview.com", "Ramanujan IT City, Taramani, Chennai", "PENDING", "COLD", "lead-10", "", "", 0),
    ("Apex Info Fake Corp", "Salem", "https://apexinvalidlink.org", "Unverified Third Party Contractor Agency", "9876500023", "fakehr@apexinvalidlink.org", "Near Old Bus Stand, Salem", "REJECTED", "COLD", "lead-3", "sivasubramaniyan", "", 0),
    ("Global Tech Solutions Pvt", "Erode", "https://nonexistentglob.co", "Third Party Consultancy with Registration Issue", "9876500024", "info@nonexistentglob.co", "Bhavani Road, Erode", "REJECTED", "COLD", "lead-4", "sivasubramaniyan", "", 0),
    ("Rapid Hiring Solutions", "Tirunelveli", "https://rapidhiringfake.net", "Unregistered Training & Placement Vendor", "9876500025", "contact@rapidhiringfake.net", "South Bypass Road, Tirunelveli", "REJECTED", "COLD", "lead-5", "sivasubramaniyan", "", 0)
]

companies = []
for c in companies_raw:
    companies.append({
        "company_name": c[0],
        "location": c[1],
        "website": c[2],
        "content": c[3],
        "hr_phone": c[4],
        "hr_email": c[5],
        "company_address": c[6],
        "approval_status": c[7],
        "placement_status": c[8],
        "submitted_by": c[9],
        "approved_by": c[10],
        "drive_date": c[11],
        "offers_count": c[12]
    })

with open(os.path.join(DATASETS_DIR, "companies.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(companies[0].keys()))
    writer.writeheader()
    writer.writerows(companies)

# 4. PLACEMENTS DATASET (Placed students)
placements = []
for s in students[:18]:
    placements.append({
        "reg_number": s["reg_number"],
        "student_name": s["name"],
        "department": s["department"],
        "company_name": s["placed_company"],
        "status": "PLACED",
        "ctc_lpa": s["ctc_lpa"],
        "drive_date": "2026-08-15",
        "offer_date": "2026-08-16"
    })

with open(os.path.join(DATASETS_DIR, "placements.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["reg_number", "student_name", "department", "company_name", "status", "ctc_lpa", "drive_date", "offer_date"])
    writer.writeheader()
    writer.writerows(placements)

# 5. NOTIFICATIONS DATASET
notifications = [
    {
        "sender": "lead-2",
        "receiver": "sivasubramaniyan",
        "type": "COMPANY_SUBMISSION",
        "company_name": "Tiger Analytics",
        "title": "New Company Sourced: Tiger Analytics",
        "message": "Lead-2 has submitted Tiger Analytics for Admin background verification.",
        "status": "UNREAD",
        "created_at": "2026-08-29 10:15:00"
    },
    {
        "sender": "lead-7",
        "receiver": "sivasubramaniyan",
        "type": "COMPANY_SUBMISSION",
        "company_name": "Chargebee Technologies",
        "title": "New Company Sourced: Chargebee Technologies",
        "message": "Lead-7 has submitted Chargebee Technologies for Admin background verification.",
        "status": "UNREAD",
        "created_at": "2026-08-29 11:30:00"
    },
    {
        "sender": "lead-8",
        "receiver": "sivasubramaniyan",
        "type": "COMPANY_SUBMISSION",
        "company_name": "Kissflow Software",
        "title": "New Company Sourced: Kissflow Software",
        "message": "Lead-8 has submitted Kissflow Software for Admin background verification.",
        "status": "UNREAD",
        "created_at": "2026-08-29 12:00:00"
    },
    {
        "sender": "sivasubramaniyan",
        "receiver": "lead-1",
        "type": "COMPANY_APPROVED",
        "company_name": "Zoho Corporation",
        "title": "Company Approved: Zoho Corporation",
        "message": "Company Zoho Corporation has been approved. Nice job! Keep going and connect with the next company.",
        "status": "READ",
        "created_at": "2026-08-10 14:20:00"
    },
    {
        "sender": "sivasubramaniyan",
        "receiver": "lead-2",
        "type": "COMPANY_APPROVED",
        "company_name": "Amazon Development Centre",
        "title": "Company Approved: Amazon Development Centre",
        "message": "Company Amazon Development Centre has been approved. Nice job! Keep going and connect with the next company.",
        "status": "READ",
        "created_at": "2026-08-12 16:00:00"
    },
    {
        "sender": "sivasubramaniyan",
        "receiver": "lead-3",
        "type": "COMPANY_REJECTED",
        "company_name": "Apex Info Fake Corp",
        "title": "Company Rejected: Apex Info Fake Corp",
        "message": "Company Apex Info Fake Corp was rejected during verification due to unverified registration and fake contact numbers.",
        "status": "READ",
        "created_at": "2026-08-25 09:30:00"
    }
]

with open(os.path.join(DATASETS_DIR, "notifications.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["sender", "receiver", "type", "company_name", "title", "message", "status", "created_at"])
    writer.writeheader()
    writer.writerows(notifications)

# 6. 10 JOB DESCRIPTIONS
jds = {
    "python_developer.txt": """Job Title: Python Backend Developer
Location: Chennai / Remote
Experience: 0-2 Years / Freshers
Required Skills: Python, Flask, Django, REST API, MongoDB, SQL, Git, Linux, Docker, Unit Testing
Role Overview:
We are looking for a passionate Python Developer to design and develop scalable backend APIs, database models, and web applications. You will collaborate with frontend teams and integrate third-party services like Cloudinary, Payment Gateways, and AI models.""",

    "data_analyst.txt": """Job Title: Data Analyst & Business Intelligence Specialist
Location: Bengaluru / Chennai
Experience: Freshers / 0-1 Year
Required Skills: Python, Pandas, NumPy, SQL, Tableau, Power BI, Excel, Data Visualization, Statistical Analysis
Role Overview:
Analyze large scale business datasets, generate insightful executive dashboards, run SQL queries, and deliver actionable placement and market insights.""",

    "ai_engineer.txt": """Job Title: AI / ML Engineer
Location: Hyderabad / Chennai
Experience: 0-2 Years
Required Skills: Python, PyTorch, TensorFlow, Scikit-learn, NLP, LLM, Computer Vision, Transformers, FastApi, REST API
Role Overview:
Build and deploy machine learning models, fine-tune open-source LLMs, develop Retrieval-Augmented Generation (RAG) pipelines, and integrate AI APIs into production web systems.""",

    "full_stack_developer.txt": """Job Title: Full Stack Web Developer (Python + React / Tailwind)
Location: Chennai / Coimbatore
Experience: 0-2 Years
Required Skills: HTML5, CSS3, Tailwind CSS, JavaScript, React, Python, Flask, MongoDB, RESTful APIs, Git
Role Overview:
Design end-to-end responsive web applications with interactive UI components, secure role-based authentication, and robust REST APIs.""",

    "backend_developer.txt": """Job Title: Backend API Engineer
Location: Bengaluru / Remote
Experience: 0-2 Years
Required Skills: Python, Node.js, Flask, PostgreSQL, MongoDB, Redis, Microservices, REST API, JWT Authentication
Role Overview:
Build high throughput backend services, implement caching, optimize database queries, and secure backend endpoints with RBAC.""",

    "frontend_developer.txt": """Job Title: Frontend UI/UX Developer
Location: Chennai
Experience: 0-1 Year
Required Skills: HTML5, Tailwind CSS, JavaScript ES6+, React, Responsive Design, Web Accessibility, Figma to Code
Role Overview:
Craft visually stunning, fast, and accessible user interfaces. Implement smooth micro-interactions, dark/light themes, and seamless API integrations.""",

    "ml_engineer.txt": """Job Title: Machine Learning Ops & Data Scientist
Location: Bengaluru
Experience: 0-2 Years
Required Skills: Python, Scikit-learn, MLflow, Docker, Pandas, Deep Learning, SQL, Kubernetes, Cloud Deployment
Role Overview:
Train and evaluate predictive models, build feature engineering pipelines, monitor model drift, and maintain production ML workflows.""",

    "java_developer.txt": """Job Title: Java Full Stack Developer
Location: Coimbatore / Chennai
Experience: 0-2 Years
Required Skills: Java, Spring Boot, Hibernate, MySQL, HTML5, JavaScript, REST APIs, Microservices, Maven
Role Overview:
Develop enterprise Java Spring Boot backend microservices and maintain secure, transactional business applications.""",

    "cloud_engineer.txt": """Job Title: Cloud & DevOps Engineer
Location: Chennai / Bengaluru
Experience: 0-2 Years
Required Skills: AWS, Docker, Kubernetes, Linux, Python, CI/CD, Terraform, GitHub Actions, Nginx
Role Overview:
Manage cloud infrastructure, containerize applications, configure serverless architectures on Vercel/AWS, and automate deployments.""",

    "data_scientist.txt": """Job Title: Data Scientist & Predictive Modeling Specialist
Location: Chennai
Experience: 0-2 Years
Required Skills: Python, R, Machine Learning, Deep Learning, Statistics, Scipy, Matplotlib, Seaborn, SQL
Role Overview:
Derive statistical hypotheses, build predictive scoring algorithms, conduct exploratory data analysis, and present findings to leadership."""
}

for filename, content in jds.items():
    with open(os.path.join(JD_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content.strip())

print("All datasets generated successfully in datasets/ directory!")
