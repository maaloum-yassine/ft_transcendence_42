from django.urls import path, include
from .views import *

urlpatterns = [
    # path('', test, name='test'),
    # path('creategame_form/', creategame_form, name='creategame_form'),
    path('create_friends_game/', create_friends_game, name='create_friends_game'),
    path('badr_list_games/', list_games, name='list_games'),
    path('history/', history, name='fetch_user_wins_by_id'),
    path('badr_game_stats/', game_stats, name='game_stats'),
    path('user-data/', list_games, name='fetch_user_wins_by_id'),
    path('<str:room_name>/', game_view, name='game'),
]
