import os
import io
import fitz # PyMuPDF
import docx
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from analyzer.models import ResumeAnalysis, UserProfile
from analyzer.engine import analyze_resume, parse_resume_file
from analyzer.reports import generate_pdf_report

class ResumeEngineTests(TestCase):
    def setUp(self):
        self.sample_text = """
        John Doe
        john.doe@example.com | (555) 123-4567 | San Francisco, CA

        Professional Summary
        Results-oriented Full Stack Engineer with 5+ years of experience building scalable applications using Python, Django, React, and PostgreSQL.

        Experience
        Senior Software Engineer - Tech Solutions (2020 - 2024)
        - Developed REST APIs and microservices using Django and PostgreSQL, improving transaction speed by 35%.
        - Led a team of 5 developers and collaborated on CI/CD pipelines with Docker and AWS.
        - Designed interactive web portals using React and JavaScript for 100,000+ active users.

        Education
        Bachelor of Science in Computer Science - University of California (2016 - 2020)

        Skills
        Python, Django, React, JavaScript, HTML5, CSS3, PostgreSQL, Docker, AWS, Git, REST API, Machine Learning
        """

    def test_analyze_resume_scores(self):
        res = analyze_resume(self.sample_text, file_type='pdf', jd_text='Looking for Python, Django, React, and Kubernetes.')
        self.assertGreater(res['overall_score'], 70)
        self.assertGreater(res['ats_compatibility'], 70)
        self.assertIn('Python', res['skills'])
        self.assertIn('Django', res['skills'])
        self.assertIn('Kubernetes', res['missing_skills'])
        self.assertTrue(any(c['title'] == 'Contact Information Parsing' and c['passed'] for c in res['ats_checks']))

class ResumeAIViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testcandidate', password='SecretPassword123', email='candidate@test.com')
        self.profile = UserProfile.objects.create(user=self.user, role='jobseeker')

    def test_landing_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Get Expert Feedback on your")
        self.assertContains(response, "Drop your resume here or choose a file")

    def test_user_registration_and_login(self):
        res = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Password999',
            'password2': 'Password999',
            'role': 'jobseeker'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_resume_upload_and_pdf_generation(self):
        self.client.login(username='testcandidate', password='SecretPassword123')
        
        # Create a small valid PDF in memory using fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "Jane Smith\njane@test.com | 555-987-6543\nExperience\nDeveloped Python Django apps 2021-2023.\nEducation\nBachelor Degree\nSkills\nPython, Django, SQL, Docker")
        pdf_bytes = doc.tobytes()
        doc.close()
        
        uploaded = SimpleUploadedFile("sample_resume.pdf", pdf_bytes, content_type="application/pdf")
        upload_resp = self.client.post('/upload/', {'resume_file': uploaded, 'job_description': 'Python Django AWS'}, follow=True)
        self.assertEqual(upload_resp.status_code, 200)
        
        analysis = ResumeAnalysis.objects.filter(user=self.user).first()
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.file_type, 'pdf')
        self.assertTrue(analysis.is_advisory)

        # Test PDF Report Download
        report_resp = self.client.get(f'/download-report/{analysis.id}/')
        self.assertEqual(report_resp.status_code, 200)
        self.assertEqual(report_resp['Content-Type'], 'application/pdf')
        self.assertTrue(len(report_resp.content) > 1000)
