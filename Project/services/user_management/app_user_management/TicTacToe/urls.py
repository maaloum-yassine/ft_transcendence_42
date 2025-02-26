from django.urls import path
from . import views

from django.urls import path, re_path
from . import views
from .api import api  # Your NinjaAPI instance
from .consumers import TicTacToeConsumer

urlpatterns = [
    path('getId/', views.getId, name='getID'),
    path('getUsername/', views.getUsername, name='getUsername'),
    path('tictactoe-api/', api.urls),  # Django Ninja API for TicTacToe
    # WebSocket URL pattern
    re_path(r'ws/tictactoe/(?P<room_name>\w+)/$', TicTacToeConsumer.as_asgi()),
]
