from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('upload/', views.upload_resume_view, name='upload_resume'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/<int:analysis_id>/', views.dashboard_view, name='dashboard_detail'),
    path('history/', views.history_view, name='history'),
    path('download-report/<int:analysis_id>/', views.download_report_view, name='download_report'),
    path('delete/<int:analysis_id>/', views.delete_analysis_view, name='delete_analysis'),
]
