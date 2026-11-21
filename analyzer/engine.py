import re
import fitz # PyMuPDF
import docx

COMMON_TECH_SKILLS = [
    'Python', 'Django', 'Flask', 'FastAPI', 'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
    'HTML5', 'CSS3', 'Bootstrap', 'Tailwind', 'Node.js', 'Express', 'SQL', 'PostgreSQL', 'MySQL',
    'SQLite', 'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'GitHub',
    'GitLab', 'CI/CD', 'REST API', 'GraphQL', 'Linux', 'Machine Learning', 'Deep Learning',
    'Data Analysis', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'NLP', 'Computer Vision',
    'Agile', 'Scrum', 'Jira', 'Unit Testing', 'Pytest', 'Microservices', 'Celery', 'Kafka',
    'C++', 'Java', 'C#', '.NET', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'Next.js'
]

COMMON_SOFT_SKILLS = [
    'Leadership', 'Communication', 'Problem Solving', 'Teamwork', 'Critical Thinking',
    'Project Management', 'Time Management', 'Adaptability', 'Collaboration', 'Mentorship'
]

ALL_SKILLS_REF = COMMON_TECH_SKILLS + COMMON_SOFT_SKILLS

SECTION_PATTERNS = {
    'contact': [r'contact', r'phone', r'email', r'linkedin', r'github', r'address'],
    'summary': [r'summary', r'professional summary', r'about me', r'profile', r'objective'],
    'experience': [r'experience', r'work experience', r'employment history', r'professional experience', r'internships'],
    'education': [r'education', r'academic background', r'qualifications', r'degrees'],
    'skills': [r'skills', r'technical skills', r'core competencies', r'technologies', r'tools'],
    'projects': [r'projects', r'personal projects', r'academic projects', r'key projects'],
    'certifications': [r'certifications', r'certificates', r'licenses', r'achievements', r'awards']
}

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text.strip()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                full_text.append(" | ".join(row_text))
    return "\n".join(full_text)

def parse_resume_file(file_path, file_extension):
    ext = file_extension.lower().replace('.', '')
    if ext == 'pdf':
        text = extract_text_from_pdf(file_path)
    elif ext in ['docx', 'doc']:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDF and DOCX are allowed.")
    
    if not text or len(text.strip()) < 50:
        raise ValueError("Could not extract sufficient text from this document. Please ensure it is not an image-only scanned document.")
    return text

def extract_sections(text):
    text_lower = text.lower()
    sections = {}
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for sec_name, keywords in SECTION_PATTERNS.items():
        found = False
        for kw in keywords:
            for line in lines:
                clean_line = re.sub(r'[^a-zA-Z\s]', '', line.lower()).strip()
                if clean_line == kw or clean_line.startswith(kw + ' ') or clean_line.endswith(' ' + kw):
                    found = True
                    break
            if found:
                break
        sections[sec_name] = found
    return sections

def extract_skills(text):
    found_skills = []
    text_lower = text.lower()
    
    for skill in ALL_SKILLS_REF:
        pattern = r'(?<![a-zA-Z0-9_])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9_])'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
            
    return list(dict.fromkeys(found_skills))

def extract_jd_keywords(jd_text):
    if not jd_text:
        return []
    jd_skills = []
    jd_lower = jd_text.lower()
    for skill in ALL_SKILLS_REF:
        pattern = r'(?<![a-zA-Z0-9_])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9_])'
        if re.search(pattern, jd_lower):
            jd_skills.append(skill)
    return list(dict.fromkeys(jd_skills))

def analyze_resume(text, file_type='pdf', jd_text=''):
    sections = extract_sections(text)
    skills = extract_skills(text)
    words = re.findall(r'\b[A-Za-z0-9+#.-]+\b', text)
    word_count = len(words)
    
    # 1. Skills Score (25%)
    # Target: 8+ skills for top score
    skill_cnt = len(skills)
    if skill_cnt >= 12:
        raw_skills_score = 100
    elif skill_cnt >= 8:
        raw_skills_score = 85 + (skill_cnt - 8) * 3
    elif skill_cnt >= 4:
        raw_skills_score = 65 + (skill_cnt - 4) * 5
    elif skill_cnt >= 1:
        raw_skills_score = 40 + skill_cnt * 6
    else:
        raw_skills_score = 20
    skills_score = min(100, raw_skills_score)

    # 2. Experience Score (25%)
    raw_exp = 50
    if sections.get('experience'):
        raw_exp += 25
    year_matches = re.findall(r'\b(20[0-2][0-9]|199[0-9])\b', text)
    if len(year_matches) >= 4:
        raw_exp += 15
    elif len(year_matches) >= 2:
        raw_exp += 10
    action_verbs = ['developed', 'designed', 'led', 'managed', 'built', 'created', 'implemented', 'improved', 'optimized', 'engineered', 'launched', 'delivered']
    found_verbs = [v for v in action_verbs if re.search(r'\b' + v + r'\b', text.lower())]
    if len(found_verbs) >= 5:
        raw_exp += 10
    elif len(found_verbs) >= 2:
        raw_exp += 5
    experience_score = min(100, raw_exp)

    # 3. Education Score (15%)
    raw_edu = 40
    if sections.get('education'):
        raw_edu += 35
    edu_terms = ['bachelor', 'master', 'b.tech', 'm.tech', 'bsc', 'msc', 'phd', 'degree', 'university', 'college', 'institute']
    if any(re.search(r'\b' + term + r'\b', text.lower()) for term in edu_terms):
        raw_edu += 25
    education_score = min(100, raw_edu)

    # 4. Formatting Score (15%)
    raw_format = 60
    if 300 <= word_count <= 1200:
        raw_format += 20
    elif word_count > 150:
        raw_format += 10
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
        raw_format += 10
    if re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
        raw_format += 10
    formatting_score = min(100, raw_format)

    # 5. Keywords Score (20%)
    missing_skills = []
    if jd_text and len(jd_text.strip()) > 20:
        jd_skills = extract_jd_keywords(jd_text)
        if jd_skills:
            matched_jd = [s for s in jd_skills if s in skills]
            missing_skills = [s for s in jd_skills if s not in skills]
            raw_keywords = int((len(matched_jd) / len(jd_skills)) * 100)
        else:
            raw_keywords = 75
    else:
        raw_keywords = min(100, 50 + len(skills) * 4)
    keywords_score = min(100, raw_keywords)

    # Configurable weighted resume score:
    # skills 25%, experience 25%, education 15%, formatting 15%, keywords 20%
    overall_score = round(
        (skills_score * 0.25) +
        (experience_score * 0.25) +
        (education_score * 0.15) +
        (formatting_score * 0.15) +
        (keywords_score * 0.20)
    )

    # ATS Checks
    ats_checks = []
    
    # 1. Contact info
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    ats_checks.append({
        'title': 'Contact Information Parsing',
        'passed': has_email and has_phone,
        'details': 'Valid email and contact phone detected.' if (has_email and has_phone) else 'Missing explicit email or phone format in plain text header.'
    })

    # 2. Section Headers
    key_sections = ['experience', 'education', 'skills']
    sections_present = all(sections.get(s) for s in key_sections)
    ats_checks.append({
        'title': 'Standard Section Headings',
        'passed': sections_present,
        'details': 'Standard ATS headings (Experience, Education, Skills) recognized.' if sections_present else 'Some standard headings are non-standard or missing.'
    })

    # 3. File type friendly
    is_friendly_format = file_type.lower() in ['pdf', 'docx']
    ats_checks.append({
        'title': 'ATS Machine-Readable Format',
        'passed': is_friendly_format,
        'details': f'Format ({file_type.upper()}) is standard for ATS parsers.'
    })

    # 4. Length check
    good_length = 50 <= word_count <= 1500
    ats_checks.append({
        'title': 'Resume Length & Density',
        'passed': good_length,
        'details': f'Word count ({word_count} words) is optimal for ATS scanning.' if good_length else f'Word count ({word_count} words) may be too concise or overly lengthy.'
    })

    # 5. Measurable Impact
    has_metrics = bool(re.search(r'(\d+%\b|\$\d+|\b\d+\s*users\b|\b\d+\s*clients\b|\b\d+x\b|\bincreased\b|\breduced\b|\bimproving\b)', text.lower()))
    ats_checks.append({
        'title': 'Quantifiable Metrics & Accomplishments',
        'passed': has_metrics,
        'details': 'Includes measurable impact metrics (%) or quantified achievements.' if has_metrics else 'Consider adding numbers, percentages, and metrics to demonstrate impact.'
    })

    ats_passed_cnt = sum(1 for c in ats_checks if c['passed'])
    ats_compatibility = round((ats_passed_cnt / len(ats_checks)) * 100)

    # Grounded Recommendations (strict: never fabricate qualifications)
    recommendations = []
    if not sections.get('summary'):
        recommendations.append({
            'category': 'Structure',
            'severity': 'Medium',
            'text': 'Add a concise 3-4 sentence Professional Summary at the top to highlight your core strengths and career focus.'
        })
    if not sections.get('projects'):
        recommendations.append({
            'category': 'Content',
            'severity': 'Low',
            'text': 'Consider adding a dedicated "Projects" section detailing your hands-on achievements with live repository links.'
        })
    if len(skills) < 8:
        recommendations.append({
            'category': 'Skills',
            'severity': 'High',
            'text': 'Include more recognized technical and industry-specific tools you have practical experience with.'
        })
    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append({
            'category': 'Targeted Job Alignment',
            'severity': 'High',
            'text': f"Job Description keyword gap: The following relevant keywords from the job description are not mentioned: {', '.join(top_missing)}. If you possess these capabilities, explicitly highlight them in your Experience or Skills sections without fabricating."
        })
    if not has_metrics:
        recommendations.append({
            'category': 'Impact',
            'severity': 'Medium',
            'text': 'Enhance bullet points with action verbs and quantifiable results (e.g., "improved latency by 35%", "managed team of 6 engineers").'
        })
    if not has_email or not has_phone:
        recommendations.append({
            'category': 'Header',
            'severity': 'High',
            'text': 'Ensure your direct email address and accessible phone number are visible in the top header.'
        })
    if len(recommendations) < 3:
        recommendations.append({
            'category': 'Optimization',
            'severity': 'Low',
            'text': 'Your resume demonstrates solid structure! Tailor bullet points subtly for each application to mirror the employer’s priority competencies.'
        })

    return {
        'extracted_text': text,
        'skills': skills,
        'sections': sections,
        'missing_skills': missing_skills,
        'skills_score': skills_score,
        'experience_score': experience_score,
        'education_score': education_score,
        'formatting_score': formatting_score,
        'keywords_score': keywords_score,
        'overall_score': overall_score,
        'ats_compatibility': ats_compatibility,
        'ats_checks': ats_checks,
        'recommendations': recommendations
    }
