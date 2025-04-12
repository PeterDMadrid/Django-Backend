from django.contrib import admin
from .models import CustomUser, ProfilePicture, Progress

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'level', 'is_staff', 'profile_picture','is_right','progress')
    list_filter = ('is_staff', 'level')
    search_fields = ('username',)

@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('introduction', 'twodigit', 'mathlesson')
