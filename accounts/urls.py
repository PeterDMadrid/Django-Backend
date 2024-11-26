from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('profile-pictures/', views.get_profile_pictures, name='profile-pictures'),
    path('update-profile-picture/', views.update_profile_picture, name='update-profile-picture'),
    path('check-authentication/', views.check_authentication, name='check-authentication'),
    path('logout-user/', views.logout_user, name='logout-user')
]
