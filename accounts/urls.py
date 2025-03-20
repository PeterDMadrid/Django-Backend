from django.urls import path
from . import views

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
]
