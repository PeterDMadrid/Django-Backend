from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password

class CustomUserManager(BaseUserManager):
    def create_user(self, username, profile_picture=None):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username)
        if profile_picture:
            user.profile_picture = profile_picture
        user.save(using=self._db)
        
        score = Score.objects.create(recognition=0, signing=0,user=user)  # Initialize signing score
        user.save(using=self._db) 
        return user
    
    def create_superuser(self, username, password=None):
        user = self.create_user(username=username)
        user.is_staff = True
        user.is_superuser = True
        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user

class ProfilePicture(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_pictures/') 

    def __str__(self):
        return self.name
    
class Score(models.Model):
    user = models.OneToOneField(
        'CustomUser', 
        on_delete=models.CASCADE, 
        related_name='user_score_profile', 
        null=True
    )
    recognition = models.IntegerField(default=0)
    signing = models.IntegerField(default=0)
    
    def __str__(self):
        return f"User: {self.user.username if self.user else 'No User'}, Recognition: {self.recognition}, Signing: {self.signing}"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    profile_picture = models.ForeignKey(ProfilePicture, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.OneToOneField(Score, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profile')
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    password = models.CharField(max_length=128, null=True)
    is_right = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    