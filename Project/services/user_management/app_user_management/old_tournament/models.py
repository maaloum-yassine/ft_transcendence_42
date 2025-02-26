from django.db import models
from user_managemanet.models import CustomUser 
import shortuuid


class TournamentModels(models.Model):
    
    tournament_name = models.CharField(max_length=128, blank=True, unique=True, default=shortuuid.uuid)
    tournamentgame_name = models.CharField(max_length=128, null=True, blank=True)
    createmodelform  = models.CharField(max_length=128, null=True, blank=True)
    joinmodelform  = models.CharField(max_length=128, null=True, blank=True)
    tournament_members = models.ManyToManyField(CustomUser, related_name="tournament_player", blank=True)
    
    def __str__(self):
        return self.tournament_name
    
