import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.core.exceptions import PermissionDenied

from .models import ResumeAnalysis, UserProfile
from .engine import parse_resume_file, analyze_resume
from .reports import generate_pdf_report

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = ['.pdf', '.docx']

def landing_page(request):
    latest_analysis = None
    if request.user.is_authenticated:
        latest_analysis = ResumeAnalysis.objects.filter(user=request.user).first()
    return render(request, 'landing.html', {'latest_analysis': latest_analysis})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', 'jobseeker')
        target_job = request.POST.get('target_job_title', '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'register.html')
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role=role, target_job_title=target_job)
        login(request, user)
        messages.success(request, f"Welcome to ResumeAI, {user.username}!")
        return redirect('dashboard')
    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        target_job = request.POST.get('target_job_title', '').strip()
        role = request.POST.get('role', profile.role)
        
        request.user.email = email
        request.user.save()
        profile.target_job_title = target_job
        profile.role = role
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'profile.html', {'profile': profile})

@login_required
def upload_resume_view(request):
    if request.method != 'POST':
        return redirect('landing')
    
    resume_file = request.FILES.get('resume_file')
    job_description = request.POST.get('job_description', '').strip()
    
    if not resume_file:
        messages.error(request, "No resume file was uploaded.")
        return redirect('landing')
        
    ext = os.path.splitext(resume_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        messages.error(request, f"Invalid file format ({ext}). Only PDF and DOCX files are allowed.")
        return redirect('landing')
        
    if resume_file.size > MAX_UPLOAD_SIZE:
        messages.error(request, f"File size exceeds 10MB limit ({resume_file.size / (1024*1024):.1f}MB).")
        return redirect('landing')

    analysis = ResumeAnalysis.objects.create(
        user=request.user,
        original_filename=resume_file.name,
        file=resume_file,
        file_type=ext.replace('.', ''),
        file_size_bytes=resume_file.size,
        target_job_description=job_description
    )

    try:
        extracted_text = parse_resume_file(analysis.file.path, ext)
        res = analyze_resume(extracted_text, file_type=analysis.file_type, jd_text=job_description)
        
        analysis.extracted_text = extracted_text
        analysis.skills_score = res['skills_score']
        analysis.experience_score = res['experience_score']
        analysis.education_score = res['education_score']
        analysis.formatting_score = res['formatting_score']
        analysis.keywords_score = res['keywords_score']
        analysis.overall_score = res['overall_score']
        analysis.ats_compatibility = res['ats_compatibility']
        analysis.skills_found = res['skills']
        analysis.missing_skills = res['missing_skills']
        analysis.sections_detected = res['sections']
        analysis.ats_checks = res['ats_checks']
        analysis.recommendations = res['recommendations']
        analysis.save()
        
        messages.success(request, f"Resume '{analysis.original_filename}' successfully evaluated!")
        return redirect('dashboard_detail', analysis_id=analysis.id)
    except Exception as e:
        analysis.delete()
        messages.error(request, f"Error parsing resume: {str(e)}")
        return redirect('landing')

@login_required
def dashboard_view(request, analysis_id=None):
    if analysis_id:
        analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, user=request.user)
    else:
        analysis = ResumeAnalysis.objects.filter(user=request.user).first()
        
    recent_analyses = ResumeAnalysis.objects.filter(user=request.user)[:5]
    return render(request, 'dashboard.html', {
        'analysis': analysis,
        'recent_analyses': recent_analyses
    })

@login_required
def history_view(request):
    analyses = ResumeAnalysis.objects.filter(user=request.user)
    return render(request, 'history.html', {'analyses': analyses})

@login_required
def download_report_view(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)
    # Per-user file access security check (or staff)
    if analysis.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to access this report.")
        
    pdf_content = generate_pdf_report(analysis)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    filename = f"ResumeAI_Report_{analysis.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def delete_analysis_view(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, user=request.user)
    if request.method == 'POST':
        if analysis.file:
            try:
                os.remove(analysis.file.path)
            except Exception:
                pass
        analysis.delete()
        messages.info(request, "Analysis deleted successfully.")
    return redirect('history')
