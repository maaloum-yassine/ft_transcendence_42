from django.urls import path
from .views import *

urlpatterns = [
    path('create_or_join/', create_or_join, name='create_or_join'),
    path('home_/', home_, name='home_'),
    path('<str:tournament_name>/', TournamentV, name='tournament'),
]