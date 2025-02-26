from django.contrib import admin
from .models import TournamentModels 

class ConcertAdmin(admin.ModelAdmin):
    list_display = ["tournament_name", "tournamentgame_name"]
    readonly_fields = ["tournament_members"]
    exclude = ["createmodelform", "joinmodelform"]  

admin.site.register(TournamentModels, ConcertAdmin)

# {
#     "username": "nassrolah", 
#     "email": "test.sash698@passinbox.com", 
#     "first_name": "nassro",
#     "last_name": "amg",
#     "password": "ZXCzxc123@", 
#     "confirm_password": "ZXCzxc123@"
# }