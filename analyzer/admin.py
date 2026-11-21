from django.contrib import admin
from .models import UserProfile, ResumeAnalysis

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'target_job_title', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'target_job_title')

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'overall_score', 'ats_compatibility', 'file_type', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('original_filename', 'user__username', 'extracted_text')
    readonly_fields = ('created_at',)
