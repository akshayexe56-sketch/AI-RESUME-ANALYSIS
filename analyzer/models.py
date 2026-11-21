import os
from django.db import models
from django.contrib.auth.models import User

def resume_upload_path(instance, filename):
    return f'resumes/user_{instance.user.id}/{filename}'

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Administrator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    target_job_title = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=resume_upload_path)
    file_type = models.CharField(max_length=10)
    file_size_bytes = models.PositiveIntegerField(default=0)
    
    extracted_text = models.TextField(blank=True, default='')
    target_job_description = models.TextField(blank=True, default='')
    
    # Weighted Component Scores (0 to 100)
    skills_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    formatting_score = models.FloatField(default=0.0)
    keywords_score = models.FloatField(default=0.0)
    
    # Overall Advisory Scores
    overall_score = models.IntegerField(default=0)
    ats_compatibility = models.IntegerField(default=0)
    
    # Extracted data (stored in JSON)
    skills_found = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    sections_detected = models.JSONField(default=dict)
    ats_checks = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    is_advisory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} - {self.overall_score}/100 ({self.user.username})"
