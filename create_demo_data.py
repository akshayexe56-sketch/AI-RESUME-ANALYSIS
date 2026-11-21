import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resumeai_project.settings')
django.setup()

from django.contrib.auth.models import User
from analyzer.models import UserProfile, ResumeAnalysis
from analyzer.engine import analyze_resume

if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@resumeai.io', 'admin123')
    UserProfile.objects.create(user=admin_user, role='admin', target_job_title='Chief Technology Officer')
    print("Created superuser: admin / admin123")

if not User.objects.filter(username='demo_user').exists():
    demo = User.objects.create_user('demo_user', 'demo@resumeai.io', 'demo12345')
    UserProfile.objects.create(user=demo, role='jobseeker', target_job_title='Full Stack Developer')
    print("Created demo user: demo_user / demo12345")
    
    # Pre-populate sample evaluation for demo user
    sample_text = """
    Alex Rivera
    alex.rivera@example.com | (555) 345-6789 | Austin, TX
    
    Professional Summary
    Senior Full Stack Engineer with 6+ years of experience designing scalable microservices and responsive user interfaces using Python, Django, React, and AWS.
    
    Experience
    Senior Software Engineer - TechVanguard (2021 - Present)
    - Architected and deployed microservices using Django, PostgreSQL, and Redis, improving system throughput by 42%.
    - Built responsive frontend applications with React, TypeScript, and Bootstrap for over 250,000 monthly active users.
    - Led CI/CD automation pipelines on AWS with Docker and Kubernetes.
    
    Full Stack Developer - CloudWave Solutions (2018 - 2021)
    - Developed backend REST APIs in Python and Django.
    - Improved database query performance by 35% through indexing and query caching.
    
    Education
    Bachelor of Science in Computer Science - University of Texas at Austin (2014 - 2018)
    
    Skills
    Python, Django, React, TypeScript, JavaScript, SQL, PostgreSQL, Redis, Docker, Kubernetes, AWS, REST API, Git, Machine Learning
    """
    
    res = analyze_resume(sample_text, file_type='pdf', jd_text='Looking for Python, Django, React, AWS, Docker, Kubernetes, and GraphQL.')
    ResumeAnalysis.objects.create(
        user=demo,
        original_filename='Alex_Rivera_Senior_FullStack_Resume.pdf',
        file_type='pdf',
        file_size_bytes=248000,
        extracted_text=sample_text,
        target_job_description='Looking for Python, Django, React, AWS, Docker, Kubernetes, and GraphQL.',
        skills_score=res['skills_score'],
        experience_score=res['experience_score'],
        education_score=res['education_score'],
        formatting_score=res['formatting_score'],
        keywords_score=res['keywords_score'],
        overall_score=res['overall_score'],
        ats_compatibility=res['ats_compatibility'],
        skills_found=res['skills'],
        missing_skills=res['missing_skills'],
        sections_detected=res['sections'],
        ats_checks=res['ats_checks'],
        recommendations=res['recommendations'],
        is_advisory=True
    )
    print("Created demo sample resume analysis.")
