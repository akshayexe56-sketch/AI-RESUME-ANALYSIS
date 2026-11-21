# ResumeAI - AI Resume Analyzer

ResumeAI is a production-quality, responsive web application engineered with **Python (Django)**, **PyMuPDF / python-docx**, **Bootstrap 5**, and **Chart.js**.

It replicates the modern blue-gradient hero mockup and provides weighted advisory evaluations, ATS compatibility checks, job description gap analysis, and instant downloadable PDF audit reports via ReportLab.

---

## 🚀 Key Features (FR-01 to FR-16)

1. **Authentication & User Profiles**:
   - Secure registration, password hashing, login/logout sessions.
   - Profile management with roles (`Job Seeker`, `Recruiter`, `Administrator`).
2. **Resume Parser & Upload Engine**:
   - Accepts `.pdf` and `.docx` documents up to 10MB.
   - PyMuPDF (`fitz`) and `python-docx` text extraction with error handling.
3. **5-Dimension Weighted Scoring (100% Advisory)**:
   - **Skills**: 25%
   - **Experience**: 25%
   - **Education**: 15%
   - **Formatting & Length**: 15%
   - **Keywords / Job Alignment**: 20%
4. **Target Job Description Matching**:
   - Compares resume text to a target job description and highlights missing keywords.
5. **Grounded AI Recommendations**:
   - Provides concrete improvement advice strictly grounded in the document without fabricating qualifications.
6. **Pixel-Accurate UI & Dark Mode**:
   - Custom floating glass navbar (`Home`, `Service`, `Blogs`, `About Us`, `Pricing`, `FAQ`).
   - Hero section with live drag-and-drop file upload.
   - Realistic laptop dashboard mockup with live interactive donut ring and metrics.
   - Global dark/light mode toggle.
7. **Downloadable PDF Reports**:
   - Generates executive PDF evaluation summaries using `ReportLab`.
8. **Role-Based Admin Panel**:
   - Full administration portal for managing users, profiles, and resume records.

---

## 🛠️ Quickstart Installation & Run

### 1. Requirements
Ensure Python 3.10+ is installed on your system.

### 2. Setup Virtual Environment & Dependencies
```bash
pip install django reportlab python-docx pymupdf
```

### 3. Database Migrations & Initial Setup
```bash
python manage.py makemigrations
python manage.py migrate
python create_demo_data.py
```

### 4. Run Unit Tests
```bash
python manage.py test
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

Access the application in your browser:
- **Application URL**: `http://127.0.0.1:8000/`
- **Admin Dashboard**: `http://127.0.0.1:8000/admin/`
- **Default Superuser**: `admin` / `admin123`
- **Default Demo User**: `demo_user` / `demo12345`

---

## 🔒 Security & Advisory Standards
- All scores are explicitly tagged as **Advisory** heuristic diagnostics.
- Secure CSRF token validation on all POST requests.
- Strict per-user file access isolation.
