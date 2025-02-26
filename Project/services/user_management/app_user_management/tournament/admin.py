from django.contrib import admin
from .models import TournamentModels, TournamentMatch

class ConcertAdmin(admin.ModelAdmin):
    list_display = ["tournament_name", "tournamentgame_name"]
    readonly_fields = ['tournament_name', 'admin', 'tournament_members', 'game1_name', 'game2_name']

class TournamentMatchAdmin(admin.ModelAdmin):
    readonly_fields = ['tournament', 'player1', 'player2', 'game1_room', 'game2_room', 'round_number', 'is_completed', 'winner', 'created_at']

admin.site.register(TournamentModels, ConcertAdmin)
admin.site.register(TournamentMatch, TournamentMatchAdmin)



# {
#     "username": "nassrolah", 
#     "password": "ZXCzxc123@"
# }