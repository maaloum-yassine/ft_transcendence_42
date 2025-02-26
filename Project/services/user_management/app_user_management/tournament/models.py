from django.db import models
from user_managemanet.models import CustomUser 
import shortuuid

from a_game.models import GameModel

from django.conf import settings


class TournamentModels(models.Model):
    
    tournament_name = models.CharField(max_length=128, blank=True, unique=True, default=shortuuid.uuid)
    tournamentgame_name = models.CharField(max_length=128, null=True, blank=True)
    tournament_members = models.ManyToManyField(CustomUser, related_name="tournament_player", blank=True)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    game1_name = models.CharField(max_length=128, null=True, blank=True, default="game1")
    game2_name = models.CharField(max_length=128, null=True, blank=True, default="game2")
    
    def __str__(self):
        return self.tournamentgame_name
    
class TournamentMatch(models.Model):
    tournament = models.ForeignKey(TournamentModels, on_delete=models.CASCADE, related_name='matches')
    player1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tournament_matches_as_player1')
    player2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tournament_matches_as_player2')
    game1_room = models.OneToOneField(GameModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='game1_tournamentmatch')
    game2_room = models.OneToOneField(GameModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='game2_tournamentmatch')
    round_number = models.IntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournament_wins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tournament.tournamentgame_name} - Round {self.round_number}: {self.player1.username} vs {self.player2.username}"