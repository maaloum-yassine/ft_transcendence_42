from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *

@login_required
def home_(request):
    return render(request, "tournament/home.html")

@login_required
def TournamentV(request, tournament_name):

    tournament = get_object_or_404(TournamentModels, tournament_name=tournament_name)

    tournament_members = tournament.tournament_members.all()

    if request.user not in tournament.tournament_members.all():

        if tournament.tournament_members.count() < 2:
            tournament.tournament_members.add(request.user)

    context = {
        "tournament_members" : tournament_members,
        "tournament_name" : tournament_name
    }

    return render("game", )

@login_required
def create_or_join(request):


    if request.method == 'POST':
        join_form = JoinTournamentForm(request.POST)
        create_form = CreateTournamentForm(request.POST)

        if create_form.is_valid():
            tournamentgame_name = create_form.cleaned_data['createmodelform']

            if TournamentModels.objects.filter(tournamentgame_name=tournamentgame_name).exists():
                messages.error(request, 'This tournament name is taken, use another name please!')
                return render(request, 'tournament/create_or_join.html', {'create_form': create_form})

            new_tournament = create_form.save(commit=False)
            new_tournament.tournamentgame_name = tournamentgame_name
            new_tournament.save()
            new_tournament.tournament_members.add(request.user)

            messages.success(request, 'Tournament created successfully!')

            return redirect('tournament', tournament_name=new_tournament.tournament_name)

        elif join_form.is_valid():

            tournamentgame_name = join_form.cleaned_data['joinmodelform']

            if TournamentModels.objects.filter(tournamentgame_name=tournamentgame_name).exists():

                tournament = TournamentModels.objects.get(tournamentgame_name=tournamentgame_name)

                if tournament.tournament_members.count() < 2:
                    if request.user not in tournament.tournament_members.all():
                        tournament.tournament_members.add(request.user)
                        messages.success(request, 'You have joined the tournament successfully!')
                        return redirect('tournament', tournament_name=tournament.tournament_name)
                    
                    else:
                        messages.error(request, 'You are already a member of this tournament!')
                        return render(request, 'tournament/create_or_join.html', {'create_form': create_form, 'join_form': join_form})
                    
                else:
                    messages.error(request, "Sorry, this tournament is full!")
                    return render(request, 'tournament/create_or_join.html', {'create_form': create_form, 'join_form': join_form})

            else:
                messages.error(request, 'Sorry, this tournament does not exist!')
                return render(request, 'tournament/create_or_join.html', {'create_form': create_form, 'join_form': join_form})

    else:
        create_form = CreateTournamentForm()
        join_form = JoinTournamentForm()

    return render(request, 'tournament/create_or_join.html', {'create_form': create_form, 'join_form': join_form})
