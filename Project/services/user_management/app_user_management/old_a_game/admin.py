from django.contrib import admin
from .models import GameModel

class GameModelAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'get_players']
    readonly_fields = ['room_name', 'get_players', 'created_at', 'game_spend_time', 'game_ended', 'game_started']  # Make players read-only in the admin form
    exclude = ['players']

    def get_players(self, obj):
        return ", ".join([player.username for player in obj.players.all()])
    
    get_players.short_description = 'Players in this Room'

admin.site.register(GameModel, GameModelAdmin)

