from channels.db import database_sync_to_async

import jwt

from .models import CustomUser

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user(user_id):
    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
 

        header_dict = dict(scope['headers'])

        cookie = header_dict.get(b'cookie', b'').decode()

        jwt_prefix = "jwt="
        jwt_start = cookie.find(jwt_prefix)

        if jwt_start != -1:
            print("hellooooooooooooooooooooooooooooooooooo")
            token = cookie[jwt_start + len(jwt_prefix):].split(';')[0]
        else:   
            scope['user'] = AnonymousUser()

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                scope['id'] = payload.get('id')
                user = await get_user(scope['id'])

                if user:
                    scope['user'] = user
                else:
                    scope['user'] = AnonymousUser()   

            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                scope['user'] = AnonymousUser()

        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)