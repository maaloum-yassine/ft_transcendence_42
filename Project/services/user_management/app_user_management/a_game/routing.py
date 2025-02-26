
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/game/<str:group_name>/', consumers.GameConsumer.as_asgi()),
]