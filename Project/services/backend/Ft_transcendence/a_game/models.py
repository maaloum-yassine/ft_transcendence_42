from django.db import models

import shortuuid

from user_managemanet.models import CustomUser


class GameModel(models.Model):
    room_name = models.CharField(max_length=180, blank=True, unique=True, default=shortuuid.uuid)
    gameroom_name = models.CharField(max_length=128, unique=True, null=True, blank=True)
    players = models.ManyToManyField(CustomUser, related_name="room_player", blank=True)
    player1Score = models.IntegerField(default=0, blank=True)
    player2Score = models.IntegerField(default=0, blank=True)
    game_spend_time = models.CharField(max_length=10, blank=True)
    game_started = models.BooleanField(default=False)
    game_ended = models.BooleanField(default=False)
    winner = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(max_length=400, null=True, blank=True)

    def __str__(self):
        return self.room_name
