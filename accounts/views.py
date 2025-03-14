from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, ProfilePicture, Score
from .serializers import UserSerializer, ProfilePictureSerializer
from rest_framework.authtoken.models import Token

@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_pictures(request):
    pictures = ProfilePicture.objects.all()
    serializer = ProfilePictureSerializer(pictures, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    profile_picture_id = request.data.get('profile_picture_id')

    if not username:
        return Response(
            {'error': 'Username is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if CustomUser.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    user = CustomUser.objects.create_user(username=username)

    if profile_picture_id:
        try:
            profile_picture = ProfilePicture.objects.get(id=profile_picture_id)
            user.profile_picture = profile_picture
            user.save()
        except ProfilePicture.DoesNotExist:
            pass

    Token.objects.filter(user=user).delete()
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'user': UserSerializer(user).data,
        'token': token.key
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')

    try:
        user = CustomUser.objects.get(username=username)
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_picture(request):
    profile_picture_id = request.data.get('profile_picture_id')
    
    if not profile_picture_id:
        return Response(
            {'error': 'Profile picture ID is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        profile_picture = ProfilePicture.objects.get(id=profile_picture_id)
        request.user.profile_picture = profile_picture
        request.user.save()
        return Response(UserSerializer(request.user).data)
    except ProfilePicture.DoesNotExist:
        return Response(
            {'error': 'Profile picture not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_authentication(request):
    return Response({'authenticated': True, 'username': request.user.username})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    Token.objects.filter(user=request.user).delete()
    return Response(
        {'message': 'Successfully logged out'},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_score_view(request):
    try:
        print("Request Data:", request.data)
        print("User:", request.user)
        
        signing_score = request.data.get('signing_score')
        user = request.user

        # Get or create score object
        score_obj, created = Score.objects.get_or_create(
            user=user,
            defaults={'signing': signing_score}
        )
        
        # Only update if the new score is higher or if this is a new score
        if created or signing_score > score_obj.signing:
            score_obj.signing = signing_score
            score_obj.save()
            message = 'New high score saved successfully!'
        else:
            message = 'Score not saved - existing score is higher'

        return Response({
            'status': 'success',
            'message': message,
            'data': {
                'username': user.username,
                'score': signing_score,
                'high_score': score_obj.signing
            }
        })

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_recognition_score_view(request):
    try:
        recognition_score = request.data.get('recognition_score')
        user = request.user
        
        # Get or create score object
        score_obj, created = Score.objects.get_or_create(
            user=user,
            defaults={'recognition': recognition_score}
        )
        
        # Only update if the new score is higher or if this is a new score
        if created or recognition_score > score_obj.recognition:
            score_obj.recognition = recognition_score
            score_obj.save()
            message = 'New high score saved successfully!'
        else:
            message = 'Score not saved - existing score is higher'

        return Response({
            'status': 'success',
            'message': message,
            'data': {
                'username': user.username,
                'score': recognition_score,
                'high_score': score_obj.recognition
            }
        })

    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_scores(request):
    try:
        score = request.user.user_score_profile
        challenge_scores = score.challenge_scores if score.challenge_scores else []
        return Response({
            'recognition': score.recognition,
            'signing': score.signing,
            'challenge_scores': challenge_scores,
        })
    except Score.DoesNotExist:
        return Response({'error': 'Score not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_challenge_score_view(request):
    try:
        score = request.data.get('score')
        level = request.data.get('level')
        user = request.user
        
        # Validate incoming data
        if score is None:
            return Response({
                'error': 'score is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if level is None:
            return Response({
                'error': 'level is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert to integers if needed
        try:
            score = int(score)
            level = int(level)
        except (ValueError, TypeError):
            return Response({
                'error': 'score and level must be valid integers'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create score object
        score_obj, created = Score.objects.get_or_create(
            user=user,
            defaults={'challenge_scores': [0] * 12}  # Initialize with zeros for all levels
        )
        
        # Ensure the challenge_scores field exists and is properly initialized
        if not hasattr(score_obj, 'challenge_scores') or score_obj.challenge_scores is None:
            score_obj.challenge_scores = [0] * 12  # Space for 12 levels
        
        # Make sure the array is large enough
        while len(score_obj.challenge_scores) <= level:
            score_obj.challenge_scores.append(0)
        
        # Only update if the new score is higher for the specific level
        if score > score_obj.challenge_scores[level]:
            score_obj.challenge_scores[level] = score
            score_obj.save()
            message = f'New high score saved for level {level}!'
        else:
            message = f'Score not saved for level {level} - existing score is higher'

        return Response({
            'status': 'success',
            'message': message,
            'data': {
                'username': user.username,
                'level': level,
                'score': score,
                'high_score': score_obj.challenge_scores[level],
                'all_scores': score_obj.challenge_scores
            }
        })

    except IndexError as e:
        return Response({
            'error': 'Index error',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)