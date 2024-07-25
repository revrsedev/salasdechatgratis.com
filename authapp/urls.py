# authapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('auth/profile/', views.profile_view, name='profile'),  # This should match the view function name
    path('login/', auth_views.LoginView.as_view(template_name='authapp/login.html'), name='login'),
    path('auth/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('auth/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('avatars/<str:username>/', views.avatar_view, name='avatar'),
]
