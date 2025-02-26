from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.request import Request

from .forms import *
from .models import *

from a_game.models import GameModel

import shortuuid


@login_required
def TournamentV(request, tournament_name):
    try:
        tournament = get_object_or_404(TournamentModels, tournament_name=tournament_name)
        tournament_members = tournament.tournament_members.all()

        members_data = [
            {
                'id': member.id,
                'username': member.username,
            } for member in tournament_members
        ]

        is_tournament_full = tournament_members.count() == 4

        context = {
            'tournament_id': tournament.id,
            'tournament_name': tournament.tournament_name,
            'tournament_members': members_data,
            'is_tournament_full': is_tournament_full,
            'is_admin': request.user == tournament.admin,
            'current_user_id': request.user.id,
            'current_user_username': request.user.username,
        }

        if is_tournament_full:
            player1, player2, player3, player4 = tournament_members.all()
            
            existing_match1 = TournamentMatch.objects.filter(
                tournament=tournament, 
                player1=player1, 
                player2=player2,
            ).first()

            existing_match2 = TournamentMatch.objects.filter(
                tournament=tournament, 
                player1=player3, 
                player2=player4,
            ).first()

            if not existing_match1 or not existing_match2:
                game1_room = GameModel.objects.create(
                    gameroom_name=f"Tournament-{tournament.tournament_name}-{shortuuid.uuid()}",
                    room_name=shortuuid.uuid()
                )

                match1 = TournamentMatch.objects.create(
                    tournament=tournament,
                    player1=player1,
                    player2=player2,
                    game1_room=game1_room,
                )

                game2_room = GameModel.objects.create(
                    gameroom_name=f"Tournament-{tournament.tournament_name}-{shortuuid.uuid()}",
                    room_name=shortuuid.uuid()
                )
                match2 = TournamentMatch.objects.create(
                    tournament=tournament,
                    player1=player3,
                    player2=player4,
                    game2_room=game2_room,
                )

                tournament.game1_name = game1_room.room_name
                tournament.game2_name = game2_room.room_name
                tournament.save()

                context.update({
                    'game1_room': game1_room.room_name,
                    'game2_room': game2_room.room_name,
                })

        return JsonResponse(context, safe=True)

    except Exception as e:
        return JsonResponse({
            'error': True,
            'message': str(e)
        }, status=404)


@login_required
@api_view(['POST'])
def create_or_join(request: Request):

    if request.method == 'POST':
        if request.data.get("createtournamentName"):
            tournamentName = request.data.get("createtournamentName")
            print(f"this is the tournament name >>>>>>>>>>>>>   {tournamentName}")
            if TournamentModels.objects.filter(tournamentgame_name=tournamentName).exists():
                return JsonResponse({"state": False, "message": "This tournament name already exists."})
            
            else:

                new_tournament = TournamentModels.objects.create(tournamentgame_name=tournamentName)
                new_tournament.tournament_name = shortuuid.uuid()
                new_tournament.admin = request.user
                new_tournament.save()
                new_tournament.tournament_members.add(request.user)

                return JsonResponse({"state": True, "message": "Tournament created successfully!", "room_name": new_tournament.tournament_name})

        elif request.data.get("jointournamentName"):
            tournamentName = request.data.get("jointournamentName")
            print(f"this is the tournament name >>>>>>>>>>>>>   {tournamentName}")
            if TournamentModels.objects.filter(tournamentgame_name=tournamentName).exists():
                if TournamentModels.objects.get(tournamentgame_name=tournamentName).tournament_members.count() < 4:
                    if request.user not in TournamentModels.objects.get(tournamentgame_name=tournamentName).tournament_members.all():

                        TournamentModels.objects.get(tournamentgame_name=tournamentName).tournament_members.add(request.user)

                        return JsonResponse({"state": True, "message": "You have joined the tournament successfully!", "room_name": TournamentModels.objects.get(tournamentgame_name=tournamentName).tournament_name})
                    return JsonResponse({"state": False, "message": "This tournament is full."})
                return JsonResponse({"state": False, "message": "This tournament name already exists."})
            return JsonResponse({"state": False, "message": "This tournament does not exist."})
        
    return JsonResponse({"state": False, "message": "Invalid request method."})