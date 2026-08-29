import re
import pypdf
import io
import urllib.request

# Standard skill sets to look for
SKILL_KEYWORDS = {
    "python": ["python", "django", "flask", "fastapi", "numpy", "pandas", "pytorch", "tensorflow", "scikit-learn"],
    "frontend": ["react", "vue", "angular", "tailwind", "html", "css", "javascript", "js", "typescript", "figma"],
    "database": ["mongodb", "sql", "postgresql", "mysql", "redis", "nosql", "sqlite"],
    "java": ["java", "spring", "springboot", "hibernate", "maven"],
    "devops": ["docker", "kubernetes", "aws", "cloud", "git", "github", "linux", "nginx", "jenkins", "devops"]
}

def extract_text_from_pdf(file_storage) -> str:
    """
    Extracts text content from an uploaded PDF file stream.
    """
    try:
        pdf_file = io.BytesIO(file_storage.read())
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_url(url: str) -> str:
    """
    Downloads and extracts text from a URL (supports PDFs and plain text files).
    """
    if not url:
        return ""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Match signature of PDF files (%PDF) or extension
            if 'application/pdf' in content_type or url.lower().endswith('.pdf') or data.startswith(b'%PDF'):
                pdf_file = io.BytesIO(data)
                reader = pypdf.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
                return text
            else:
                return data.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching/extracting URL {url}: {e}")
        return ""

def extract_skills_from_text(text):
    """
    Scans text for known skills and returns a set of matched skills.
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    matched = set()
    
    for category, skills in SKILL_KEYWORDS.items():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                matched.add(skill)
                
    return matched

def match_resume_and_jd(jd_text, student_data, custom_resume_text=None):
    """
    Calculates a match score between a Job Description and student's profile/custom resume text.
    """
    jd_skills = extract_skills_from_text(jd_text)
    if not jd_skills:
        # Fallback to some default target skills from JD words
        words = set(re.findall(r'\b\w{3,15}\b', jd_text.lower()))
        jd_skills = words.intersection({"python", "java", "sql", "git", "cloud", "web", "data", "react", "html"})
        
    if not jd_skills:
        return 50, "51-60", [], []

    # If custom resume text is provided, extract skills from it
    if custom_resume_text:
        student_skills = extract_skills_from_text(custom_resume_text)
    else:
        # Assemble student's skill portfolio based on department, projects, and career links
        student_skills = set()
        dept = student_data.get("department", "").upper()
        
        # Department defaults
        if dept == "CSE" or dept == "IT" or dept == "AI&DS":
            student_skills.update(["git", "github", "linux", "sql", "html", "css", "javascript"])
            
        if dept == "CSE":
            student_skills.update(["python", "flask", "mongodb", "java"])
        elif dept == "IT":
            student_skills.update(["react", "tailwind", "js", "postgresql", "docker"])
        elif dept == "AI&DS":
            student_skills.update(["python", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn"])
        elif dept == "ECE":
            student_skills.update(["c", "matlab", "embedded", "iot"])
        elif dept == "EEE":
            student_skills.update(["matlab", "embedded", "arduino"])
            
        # Extract any skills from resume URL name or portfolio link
        all_links = (student_data.get("portfolio_link", "") + " " + 
                     student_data.get("github_link", "") + " " + 
                     student_data.get("resume_url", "")).lower()
                     
        url_skills = extract_skills_from_text(all_links)
        student_skills.update(url_skills)

        # Variance based on student registration number/grades
        reg_num_int = sum(ord(c) for c in student_data.get("reg_number", "00"))
        if reg_num_int % 3 == 0:
            student_skills.update(["docker", "aws"])
        if reg_num_int % 4 == 0:
            student_skills.update(["springboot", "hibernate"])
        if reg_num_int % 5 == 0:
            student_skills.update(["fastapi", "redis"])
        
    # Calculate matches
    matched_skills = jd_skills.intersection(student_skills)
    missing_skills = jd_skills.difference(student_skills)
    
    match_count = len(matched_skills)
    total_count = len(jd_skills)
    
    ratio = match_count / total_count if total_count > 0 else 0.5
    
    # Weight academic performance
    ug_pct = student_data.get("ug_percentage", 75.0) if student_data else 75.0
    academic_factor = (ug_pct - 60) / 40.0  # Scale 60%-100% to 0-1
    academic_factor = max(0.0, min(1.0, academic_factor))
    
    score = int((ratio * 80) + (academic_factor * 20))
    score = max(10, min(100, score))
    
    # Determine range
    if score >= 91:
        score_range = "91-100"
    elif score >= 81:
        score_range = "81-90"
    elif score >= 71:
        score_range = "71-80"
    elif score >= 61:
        score_range = "61-70"
    elif score >= 51:
        score_range = "51-60"
    else:
        score_range = "0-50"
        
    return score, score_range, list(matched_skills), list(missing_skills)
