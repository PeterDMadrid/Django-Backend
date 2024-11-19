from django.contrib import admin
from .models import CustomUser, ProfilePicture

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'level', 'is_staff', 'profile_picture')
    list_filter = ('is_staff', 'level')
    search_fields = ('username',)

@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')