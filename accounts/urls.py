from django.urls import path
from . import views
from .views import UserDetailView

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('profile-pictures/', views.get_profile_pictures, name='profile-pictures'),
    path('update-profile-picture/', views.update_profile_picture, name='update-profile-picture'),
    path('check-authentication/', views.check_authentication, name='check-authentication'),
    path('logout-user/', views.logout_user, name='logout-user'),
    path('save_score/', views.save_score_view, name='save_score'),  # Ensure this matches your Flutter app
    path('save_recognition_score/', views.save_recognition_score_view, name='save_recognition_score'),
    path('user-scores/', views.get_user_scores, name='user_scores'),
    path('save_challenge_score/', views.save_challenge_score_view, name='save_challenge_score'),
    path('update-intro-progress/', views.update_introduction_progress, name='update_intro_progress'),
    path('update-two-digits-progress/', views.update_two_digits_progress, name='update_two_digits_progress'),
    path('get-user-progress/', views.get_user_progress, name='get_user_progress'),
    path('users/by-username/<str:username>/', UserDetailView.as_view(), name='user-by-username'),
]
