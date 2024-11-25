from rest_framework import serializers
from .models import CustomUser, ProfilePicture

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ('id', 'name', 'image')

class UserSerializer(serializers.ModelSerializer):
    profile_picture = ProfilePictureSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'profile_picture', 'level')
