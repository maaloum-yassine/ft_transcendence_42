from django.urls import path, include
from .views import *

urlpatterns = [
    path('', test, name='test'),
    path('create_room/', create_gameroom, name='create_gameroom'),
    path('<str:room_name>/', game_view, name='game'),
    path('tournament/', include('tournament.urls')),
]
