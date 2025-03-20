from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from django.db.models import Q
from django.conf import settings
import requests, jwt  , urllib.parse
from. import utils , models , serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

@api_view(['GET'])
def authorize_42(request:Request):
    return redirect(f"https://api.intra.42.fr/oauth/authorize?client_id={settings.CLIENT_ID_42}&redirect_uri={settings.REDIRECT_URI_42}&response_type=code&scope=public")

@api_view(['GET', 'POST'])
def callback_42(request:Request):
    response = Response()
    if 'error' in request.GET:
        error = request.GET.get('error')
        response = redirect(f'https://{settings.IP_ADRESS}')
        return response
    code = request.GET.get('code')
    token_response = requests.post("https://api.intra.42.fr/oauth/token", data={
        'grant_type': 'authorization_code',
        'client_id': settings.CLIENT_ID_42,
        'client_secret': settings.CLIENT_SECRET_42,
        'code': code,
        'redirect_uri': settings.REDIRECT_URI_42
    })
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    api_url = "https://api.intra.42.fr/v2/me"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
         response = redirect(f'https://{settings.IP_ADRESS}/404')
         return response
    user_data = response.json()
    filtered_data = {
        'username': user_data['login'],
        'email': user_data['email'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'avatar': None
    }
    user = models.CustomUser.objects.filter(Q(email=filtered_data['email'])).first()
    if user :
        token = utils.generate_token(user, True)

        if user.active_2fa is True:
            user.code_otp , r_code_otp =  utils.generate_random(8)
            user.is_logged_2fa = True
            utils.send_code(user.email, r_code_otp, user.username)
            response = redirect(f'https://{settings.IP_ADRESS}/twofa')
        else:
            user.is_online = True
            response = redirect(f'https://{settings.IP_ADRESS}/home')
        user.save()
        response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
        return response
    image_url = user_data['image']['versions']['medium']
    user = models.CustomUser.objects.filter(Q(username=filtered_data['username'])).first()
    if user:
        filtered_data['avatar'] = user_data['image']['versions']['medium']
        return Response({"status": "username already exists", **filtered_data},status=status.HTTP_409_CONFLICT)
    filtered_data['avatar']  = upload_image(image_url)
    serializer = serializers.Login__42Serializer(data=filtered_data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    request.user = user
    user.is_online = True
    user.user_42 = True
    user.save()
    token = utils.generate_token(user, True)
    response = redirect(f'https://{settings.IP_ADRESS}/home')
    response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
    response.data = {'jwt': token}
    return response



@api_view(['POST'])
def update_username(request: Request):
    data_user = request.data
    data_user['avatar'] = upload_image(request.data.get('avatar'))
    serializer = serializers.Login__42Serializer(data=data_user)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    request.user = user
    user.is_online = True
    user.user_42 = True
    user.save()
    token = utils.generate_token(user, True)
    response = redirect('profile')
    response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
    return response


def upload_image(image_url):
    avatar_user = None
    if image_url:
       image_response = requests.get(image_url)
       if image_response.status_code == 200:
            image_name = image_url.split("/")[-1]
            avatar_user = f'avatars/{image_name}'
            default_storage.save(avatar_user, ContentFile(image_response.content))
    return avatar_user

# http://localhost:8000/oauth/login/

#******************************************************************************************************************#
@api_view(['GET'])
def google_login(request:Request):
    params = {
        "client_id": settings.CLIENT_ID_GOOGLE,
        "redirect_uri": settings.REDIRECT_URI_GOOGLE,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}")

@api_view(['GET','POST'])
def google_callback(request:Request):
    response = Response()
    code = request.GET.get("code")
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.CLIENT_ID_GOOGLE,
        "client_secret": settings.CLIENT_SECRET_GOOGLE,
        "redirect_uri": settings.REDIRECT_URI_GOOGLE,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    if response.status_code != 200:
        response = redirect(f'https://{settings.IP_ADRESS}/404')
        return response
    user_data =  response.json()
    filtered_data = {
        'username': user_data['name'],
        'email': user_data['email'],
        'first_name': "None",
        'last_name': "None",
        'avatar': "avatars/default_avatar.png"
    }
    if 'given_name' in user_data:
        filtered_data['first_name'] = user_data['given_name']
    if 'family_name' in user_data:
        filtered_data['last_name'] = user_data['family_name']
    user = models.CustomUser.objects.filter(Q(email=filtered_data['email'])).first()
    if user :
        token = utils.generate_token(user, True)
        if user.active_2fa is True:
            user.code_otp , r_code_otp = utils.generate_random(8)
            response = redirect(f'https://127.0.0.1/twofa')
            user.is_logged_2fa = True
            user.is_email_verified = True
            utils.send_code(user.email, r_code_otp, user.username)
        else:
            user.is_email_verified = True
            user.is_online = True
            response = redirect(f'https://127.0.0.1/home')
        user.save()
        response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
        return response
    user = models.CustomUser.objects.filter(Q(username=filtered_data['username'])).first()
    if user:
        return Response({"status": "username already exists", **filtered_data},status=status.HTTP_409_CONFLICT)
    serializer = serializers.Login__42Serializer(data=filtered_data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    request.user = user
    user.is_online = True
    user.is_email_verified = True
    user.save()
    token = utils.generate_token(user, True)
    response = redirect(f'https://127.0.0.1/home')
    response.set_cookie(key ='jwt', value=token, httponly=True, secure=True, samesite='Strict')
    response.data = {'jwt': token}
    return response







# {'id': '109442195245676049388', 'email': 'maaloum.yassine@gmail.com', 'verified_email': True, 'name': 'Yassine MAALOUM',
#  'given_name': 'Yassine', 'family_name': 'MAALOUM', 'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJhst61E_M2Q3SG8KjTvve-tn6akk7ICGYtOY-FTtv6e3VNpA=s96-c'}
