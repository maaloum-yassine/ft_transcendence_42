from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from django.db.models import Q
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes , force_str
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from rest_framework.exceptions import ValidationError
from validators.user_validators import validate_password, validate_name, validate_username ,validate_email
from . import utils, models, serializers , redis_config
import json

class PasswordValidationError(Exception):
    pass



#************************************************HOME****************************************************************#


@api_view(['GET'])
def home(request:Request):
    if request.user.is_anonymous:
        return Response("Welcome To home 1337  page")
    return redirect('profile')

def generate_verification_token(user, flag):
    if flag is True:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
    else :
        uid = urlsafe_base64_encode(force_bytes(user.username))
    token = default_token_generator.make_token(user)
    return token, uid

def save_user_in_redis(user_data):
    user_key = f"user:{user_data['username']}"
    redis_config.redis_client.set(user_key, json.dumps(user_data), ex=3600)


#************************************************SIGN_UP****************************************************************#

@api_view(['POST', 'GET'])
def signup(request:Request):
    
    serializer = serializers.CustomUserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        hashed_password = make_password(password)
        validated_data['password'] = hashed_password
        fake_user = models.CustomUser(**validated_data)
        token , uid = generate_verification_token(fake_user, False)
        
        
        save_user_in_redis(validated_data)
        verification_link = f"https://{settings.IP_ADRESS}/verify?uid={uid}&token={token}/"
        html_message = render_to_string('verify_compte_template.html', {
            'reset_link': verification_link,
        })
        utils.send_email(validated_data['email'], html_message, False)
        return Response({"message": "Registration successful. Please check your email."}, status=status.HTTP_200_OK)
    errors = serializer.errors
    formatted_errors = list(errors.values())[0]
    return Response({"message": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def verify_account(request: Request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user_data = redis_config.redis_client.get(f"user:{uid}")
        if user_data is None:
            return Response("Utilisateur introuvable ou le lien a expiré.", status=status.HTTP_400_BAD_REQUEST)
        user_data = json.loads(user_data)
        fake_user = models.CustomUser(**user_data)
    except (TypeError, ValueError, OverflowError):
        return Response({"error": "Lien invalide ou corrompu."}, status=status.HTTP_400_BAD_REQUEST)
    if default_token_generator.check_token(fake_user, token):
        user_data['is_email_verified'] = True
        user_data['active_2fa'] = False
        models.CustomUser.objects.create(**user_data)
    
        redis_config.redis_client.delete(f"user:{uid}")
        html_message = render_to_string('registred.html', {
                'reset_link': None,
                })
        utils.send_email(user_data['email'], html_message, False)
        return Response({"message": "Votre e-mail a été vérifié avec succès et votre compte est enregistré."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Le lien de vérification est invalide ou a expiré."}, status=status.HTTP_400_BAD_REQUEST)

#**************************************************************************************************************#



#**************************************RESET_PASSWORD**************************************************************#

@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    try:
        user = models.CustomUser.objects.get(email=email)
        token , uid = generate_verification_token(user, True)
        
        reset_link = f"https://{settings.IP_ADRESS}/password_reset_confirm?uid={uid}&token={token}/"
        html_message = render_to_string('email_template.html', {
            'reset_link': reset_link,
        })
        utils.send_email(user.email, html_message, True)
        user.set_password_reset_token_expiration()
        user.save()
        return Response({"message": "A reset email has been sent."}, status=status.HTTP_200_OK)
    except models.CustomUser.DoesNotExist:
        return Response({"message": "This email does not exist"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def reset_password_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = models.CustomUser.objects.get(pk=uid)
        if user.password_reset_token_expires_at < timezone.now():
            return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            try:
                utils.validate_passwords(new_password, confirm_password)
                user.set_password(new_password)
                user.save()
                return Response({"message": "reset sucess"}, status=status.HTTP_200_OK)
            except utils.PasswordValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)
    except (models.CustomUser.DoesNotExist, ValueError, TypeError, utils.PasswordValidationError) as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
def update_passwod(request:Request):
    if request.data:
        user = request.user 
        new_pass = request.data.get("new_password")
        confirm_new_pass = request.data.get("confirm_password")
    
        if new_pass and confirm_new_pass:   
            try:
                utils.validate_passwords(new_pass ,confirm_new_pass)
                user.set_password(new_pass)
                user.save()
                return Response({"message": "reset sucess"}, status=status.HTTP_200_OK)
            except utils.PasswordValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Error update "}, status=status.HTTP_400_BAD_REQUEST)
#**************************************************************************************************************#

#*********************************************UPDATE**************************************************************#


@api_view(['PUT'])
def update(request:Request):
    user = request.user
    if request.data:
        serializer = serializers.CustomUserUpdateSerializer(request.user , data=request.data, partial=True)
        if serializer.is_valid():
            new_email = request.data.get("email")
            try:
                validate_username(request.data.get("username"))
                validate_name(request.data.get("last_name"))
                validate_name(request.data.get("first_name"))
                validate_email(new_email)
            except ValidationError as e:
                error_message = e.detail
                return Response({"message": error_message}, status=status.HTTP_400_BAD_REQUEST) 
            if new_email and new_email != user.email:
                user.is_email_verified = False
                user.active_2fa = False
                user.save()
            serializer.save()
            token = utils.generate_token(user, True)
            response = Response({
                "message": "update successful",
                "jwt": token
            }, status=status.HTTP_200_OK)
            response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
            return response
        errors = serializer.errors
        formatted_errors = list(errors.values())[0]
        return Response({"message": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "aucun element changer"}, status=status.HTTP_400_BAD_REQUEST)

#*********************************************UPLOAD-IMAGE*****************************************************************#

@api_view(['POST'])
def upload_avatar(request:Request):
    if request.user.is_anonymous:
            return redirect('home')
    file = request.FILES.get('avatar')
    if not file:
        return Response({"error": "Aucune image fournie"}, status=status.HTTP_400_BAD_REQUEST)
    fs = FileSystemStorage(location='media/avatars/')
    filename = fs.save(file.name, file)
    file_url = fs.url(filename)
    user = request.user
    user.avatar = f"avatars/{filename}"
    user.save()
    return Response({"avatar_url": file_url}, status=status.HTTP_201_CREATED)

#*********************************************************************************************************************************#
@api_view(['GET'])
def logout(request:Request):
    token = request.COOKIES.get('jwt')
    user = request.user
    user.is_online = False
    user.save()
    response = Response({"message": "Déconnecté avec succès"}, status=200)
    response.delete_cookie('jwt') 
    return response

#********************************************LOGIN*****************************************************************#

@api_view(['POST'])
def login(request: Request):
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    user = models.CustomUser.objects.filter(Q(username=username) | Q(email=email)).first()
    if user is None:
        return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    if not user.check_password(password):
        return Response({"message": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
    token = utils.generate_token(user, True)
    response = Response({"message": "Login successful","jwt": token}, status=status.HTTP_200_OK)
    user.is_online = True
    if user.active_2fa is True:
        user.code_otp, r_code_otp =  utils.generate_random(8)
        user.is_logged_2fa = True
        utils.send_code(user.email, r_code_otp, user.username)
        user.save()
        response.set_cookie(key='jwt',value=token,httponly=True,secure=True, samesite='Strict')
        response = Response({"message": "Login successful, 2FA required"}, status=status.HTTP_200_OK)
    user.save()
    response.set_cookie(key='jwt',value=token,httponly=True,secure=True, samesite='Strict')
    return response



@api_view(['POST'])
def otp(request: Request):
    try:
        serializer = serializers.verify_otp_Serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        token = utils.generate_token(request.user, True)
        response = Response({"message": "Login successful","jwt": token}, status=status.HTTP_200_OK)
        response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
        user = request.user
        user.is_logged_2fa = False
        user.save()
        return response
    except serializers.ValidationError as e:
        error_details = e.detail.get('code_otp', [])
        if error_details:
            error_message = error_details[0]
        return Response({"message": error_message}, status=400)

@api_view(['GET'])
def profile(request:Request):
    if request.user.is_anonymous:
        return redirect('home')
    serializer = serializers.CustomUserProfileSerializer(request.user, context={'request': request})
    return Response({"data": serializer.data, "message": "Profile retrieved successfully"})

#**************************************************************************************************************#

#****************************************Friendship*************************************************************#

@api_view(['POST'])
def send_friend_request(request: Request):
    try:
        user_end = request.user
        friend_name = models.CustomUser.objects.get(username=request.data.get("username_friend"))
        if user_end == friend_name:
            return Response({"detail": "incorrect request"}, status=status.HTTP_404_NOT_FOUND)
        existing_friendship = models.Friendship.objects.filter(
            (Q(user=user_end.id) & Q(friend=friend_name.id)) | (Q(user=friend_name.id) & Q(friend=user_end.id))).first()
        if existing_friendship:
            if not existing_friendship.accepted:
                return Response({"message": "Une demande d'amitié a déjà été envoyée."},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Vous êtes déjà amis."},status=status.HTTP_400_BAD_REQUEST)
        friendship = models.Friendship.objects.create(user=user_end, friend=friend_name)
        return Response( {"message": "Demande d'amitié envoyée avec succès."}, status=status.HTTP_201_CREATED)
    except models.CustomUser.DoesNotExist:
        return Response({"detail": "username_friend not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def accept_friend_request(request: Request):
    username_friend = request.data.get("username_friend")
    if not username_friend:
        return Response({"detail": "username_friend is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        to_user = models.CustomUser.objects.get(username=username_friend)
        friendship = models.Friendship.objects.get(user=to_user, friend=request.user)
        if friendship.accepted:
            return Response({"detail": "Friend request has already been accepted."}, status=status.HTTP_400_BAD_REQUEST)
        friendship.accepted = True
        friendship.save()
        return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)
    except models.CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except models.Friendship.DoesNotExist:
        return Response({"detail": "No invitation found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def list_friends(request: Request):
    friendships = models.Friendship.objects.filter(
        Q(user=request.user, friend__isnull=False) | 
        Q(friend=request.user, user__isnull=False), 
        accepted=True,
        blocked=False
    )
    if not friendships:
        return Response({"detail": "No friend found."}, status=status.HTTP_200_OK)
    friends_list = [
        {
            "auth_username": request.user.username,
            "id_auth": request.user.id,
        }
    ]
    
    added_friend_ids = set()
    
    for friendship in friendships:
        friend_user = friendship.friend if friendship.user == request.user else friendship.user
        if friend_user.id in added_friend_ids:
            continue
        added_friend_ids.add(friend_user.id)
        if utils.return_image(friend_user.avatar) is True:
            avatar = request.build_absolute_uri(settings.MEDIA_URL + friend_user.avatar).replace('http://', 'https://')
        else:
            avatar = request.build_absolute_uri(settings.MEDIA_URL + 'avatars/default_avatar.png').replace('http://', 'https://')
        
        friends_list.append({
            "id_friend": friend_user.id,
            "username": friend_user.username,
            "avatar": avatar
        })
    return Response(friends_list, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_friend(request: Request):
    if request.user.is_anonymous:
        return redirect('home')
    user_end = request.user
    friend_name = request.data.get("username_friend")
    if friend_name is None:
        return Response({"detail": "Please enter 'username_friend'."}, status=status.HTTP_400_BAD_REQUEST)
    friend_user = models.CustomUser.objects.filter(username=friend_name).first()
    if friend_user is None:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    friendship = models.Friendship.objects.filter((Q(user=user_end) & Q(friend=friend_user)) | (Q(user=friend_user) & Q(friend=user_end)) ).first()
    if friendship is None:
        return Response({"detail": "Friendship relationship not found."}, status=status.HTTP_404_NOT_FOUND)
    friendship.delete()
    return Response({"message": "Friend successfully deleted."}, status=status.HTTP_200_OK)




@api_view(['GET'])
def list_requst_friend(request: Request):
    list_request_friend = models.Friendship.objects.filter(Q(friend=request.user), accepted=False)
    friend_requests = []
    for friendship in list_request_friend:
        if utils.return_image(friendship.user.avatar):
            avatar = request.build_absolute_uri(settings.MEDIA_URL + friendship.user.avatar).replace('http://', 'https://')
        else:
            avatar = request.build_absolute_uri(settings.MEDIA_URL + 'avatars/default_avatar.png').replace('http://', 'https://')
        friend_requests.append({
            "username": friendship.user.username,
            "avatar": avatar
        })
    return Response({"requests": friend_requests}, status=status.HTTP_200_OK)


#**************************************************ACTIVAE 2FA************************************************************#
@api_view(['PUT'])
def active_2fa(request:Request):
    user = request.user
    if 'active_2fa' in request.data:
        if request.data['active_2fa'] == "true":
            user.active_2fa = True
            user.save()
            return Response({"message": "2FA is active"}, status=status.HTTP_200_OK)
        else :
            user.active_2fa = False
            user.save()
    return Response({"message": "2FA is not active"}, status=status.HTTP_200_OK)



@api_view(['GET'])
def search_friend(request):    
    if request.user.is_anonymous:
        return redirect('home')
    user_id = request.GET.get('id')
    if not user_id:
        return Response({"detail": "Enter a valid ID"}, status=status.HTTP_404_NOT_FOUND)
    try:
        user_friend = models.CustomUser.objects.get(id=user_id)
    except models.CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    list_data_user = {}
    if request.user.id == user_friend.id:
        list_data_user["id"] = request.user.id  
        list_data_user["username"] = request.user.username
        list_data_user["avatar"] = request.build_absolute_uri(settings.MEDIA_URL + request.user.avatar).replace('http://', 'https://')
        return Response({"list_data_user": list_data_user}, status=status.HTTP_200_OK)
    if utils.return_image(user_friend.avatar):
        avatar = request.build_absolute_uri(settings.MEDIA_URL + user_friend.avatar).replace('http://', 'https://')
    else:
        avatar = request.build_absolute_uri(settings.MEDIA_URL + 'avatars/default_avatar.png').replace('http://', 'https://')
    list_data_user["id"] = user_friend.id  
    list_data_user["username"] = user_friend.username
    list_data_user["avatar"] = avatar
    status_friendship = "not friend"
    existing_friendship = models.Friendship.objects.filter(
        Q(user=request.user, friend=user_friend) | Q(user=user_friend, friend=request.user)
    ).first()
    if existing_friendship:
        if existing_friendship.accepted:
            status_friendship = "friend"
        else:
            status_friendship = "already invited"
    list_data_user["status_friendship"] = status_friendship
    return Response({"list_data_user": list_data_user}, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def send_verification_email(request):
#     try:
#         token , uid = generate_verification_token(request.user, True)
#         verification_link = f"https://localhost:443/verify_email/{uid}/{token}/"
#         html_message = render_to_string('verify_email_template.html', {
#             'verification_link': verification_link,
#         })
#         utils.send_email(request.user.email, html_message, False)
    
#         return Response({"message": "A verification email has been sent."}, status=status.HTTP_200_OK)
#     except models.CustomUser.DoesNotExist:
#         return Response({"error": "This email does not exist."}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def verify_email(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()
#         user = models.CustomUser.objects.get(pk=uid)
#         if default_token_generator.check_token(user, token):
#             user.is_email_verified = True
#             user.active_2fa = True
#             user.save()
#             return Response({"message": "Your email has been successfully verified."}, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "The verification link is invalid."}, status=status.HTTP_400_BAD_REQUEST)
#     except models.CustomUser.DoesNotExist:
#         return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#**************************************************************************************************************#
