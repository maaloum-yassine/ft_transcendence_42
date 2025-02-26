from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *
from .models import GameModel
from .forms import *

from datetime import datetime

from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def test(request):
    return Response("Welcome To test  page")

@login_required
def join_game(request, group_name):
    game_room = get_object_or_404(GameModel, gameroom_name=group_name)

    if request.user not in game_room.players.all():
        if game_room.players.count() < 2:
            game_room.players.add(request.user)
            print(f"Added {request.user} to the players of {game_room.gameroom_name}")
        else:
            return render(request, 'a_game/gameisfull.html', {'game_room': game_room})
    else:
        print(f"{request.user} is already a player in the room.")

    return render(request, 'a_game/game.html', {'game_room': game_room})


@login_required
def game_view(request, room_name):

    game_room = get_object_or_404(GameModel, game_room=room_name)

    if game_room.game_ended:
        return render(request, 'a_game/gameended.html', {'game_room': game_room})

    if request.user not in game_room.players.all():
        if game_room.players.count() < 2:
            game_room.players.add(request.user)

            print(f' The Size if the game is {game_room.players.count()} >>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<')

            if game_room.players.count() == 2:
                game_room.game_started = True
                game_room.created_at = datetime.now()
                game_room.save() 

            print(f"Added {request.user} to the players of {game_room.room_name}")
        else:
            return render(request, 'a_game/gameisfull.html', {'game_room': game_room})
    else:
        print(f"{request.user} is already a player in the room.")


    return render(request, 'a_game/game.html', {'game_room': game_room})

@login_required
def create_gameroom(request):

    if request.method == 'POST':
        form = NewGameForm(request.POST)

        if form.is_valid():
            gameroom_name = form.cleaned_data['gameroom_name']

            if GameModel.objects.filter(gameroom_name=gameroom_name).exists():
                messages.error(request, 'This game room name already exists. Please choose another one.')
                return render(request, 'a_game/create_gameroom.html', {'form': form})
            
            new_gameroom = form.save(commit=False)
            new_gameroom.save()
            new_gameroom.players.add(request.user)
            return redirect('game', room_name=new_gameroom.room_name)

    else:
        form = NewGameForm()

    context = {
        'form': form
    }
    return render(request, 'a_game/create_gameroom.html', context)

