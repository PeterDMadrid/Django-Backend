from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, username, profile_picture=None):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username)
        if profile_picture:
            user.profile_picture = profile_picture
            user.save(using=self._db)
            return user
    
    def create_superuser(self, username):
        user = self.create_user(username)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class ProfilePicture(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile_pictures/')

    def __str__(self):
        return self.name
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    profile_picture = models.ForeignKey(
        ProfilePicture,
        on_delete = models.SET_NULL,
        null=True,
        blank=True
    ) 
    level = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager ()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    password = None
