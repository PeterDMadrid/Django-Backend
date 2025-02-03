from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, ProfilePicture, Score
from .serializers import UserSerializer, ProfilePictureSerializer
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser 

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
        # Detailed logging
        print("Request Data:", request.data)
        print("User:", request.user)
        
        username = request.data.get('username')
        signing_score = request.data.get('signing_score')

        try:
            # Use request.user instead of fetching by username
            user = request.user
            
            # Create score if not exists
            score_obj, created = Score.objects.get_or_create(
                user=user, 
                defaults={'signing': signing_score}
            )
            
            # Update score
            score_obj.signing = signing_score
            score_obj.save()

            return Response({
                'status': 'success', 
                'message': 'Score saved successfully',
                'data': {
                    'username': user.username,
                    'score': signing_score
                }
            })

        except Exception as user_error:
            print(f"User processing error: {user_error}")
            return Response({
                'error': 'User processing failed', 
                'details': str(user_error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        # Comprehensive error logging
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
        username = request.data.get('username')
        recognition_score = request.data.get('recognition_score')

        user = request.user
        
        # Create score if not exists
        score_obj, created = Score.objects.get_or_create(
            user=user, 
            defaults={'recognition': recognition_score}
        )
        
        # Update score
        score_obj.recognition = recognition_score
        score_obj.save()

        return Response({
            'status': 'success', 
            'message': 'Recognition score saved successfully',
            'data': {
                'username': user.username,
                'score': recognition_score
            }
        })

    except Exception as e:
        return Response({
            'error': 'Internal server error', 
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    