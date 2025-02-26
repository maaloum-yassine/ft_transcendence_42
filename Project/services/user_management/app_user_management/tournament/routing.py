from django.urls import re_path
from tournament.consumers import TournamentConsumer

websocket_urlpatterns = [
    re_path(r'ws/game/tournament/(?P<tournament_name>\w+)/$', TournamentConsumer.as_asgi()),
]