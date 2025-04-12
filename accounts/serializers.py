from rest_framework import serializers
from .models import CustomUser, ProfilePicture, Progress, Score

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ('id', 'name', 'image')

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['recognition', 'signing', 'challenge_scores']

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['introduction', 'twodigit', 'mathlesson']

class UserSerializer(serializers.ModelSerializer):
    profile_picture = ProfilePictureSerializer(read_only=True)
    user_score_profile = ScoreSerializer(read_only=True)
    progress_data = ProgressSerializer(source='progress', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'profile_picture', 'level', 'progress', 'progress_data', 'user_score_profile')

    def get_progress(self, obj):
        try:
            progress = obj.user_progress  # Use the related_name you defined
            return {
                'introduction': progress.introduction,
                'twodigit': progress.twodigit,
                'mathlesson': progress.mathlesson
            }
        except Progress.DoesNotExist:
            return {
                'introduction': False,
                'twodigit': False,
                'mathlesson': False
            }
