# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<receiver>\w+)/(?P<sender>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/second/$', consumers.SecondConsumer.as_asgi()),
    re_path(r'ws/(?P<receiver>\w+)/$', consumers.ChatNotification.as_asgi()),
  
]