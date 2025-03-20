from django.contrib import admin
from .models import GameModel

class GameModelAdmin(admin.ModelAdmin):
    list_display = ['room_name']
    readonly_fields = ['room_name', 'players', 'created_at', 'game_ended', 'game_started', "winner", "player1Score", "player2Score", "game_spend_time"]

admin.site.register(GameModel, GameModelAdmin)

