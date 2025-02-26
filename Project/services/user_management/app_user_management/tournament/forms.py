from django import forms
from django.forms import ModelForm
from .models import TournamentModels
from a_game.models import GameModel

class CreateTournamentForm(ModelForm):
    class Meta:
        model = TournamentModels
        fields = ['createmodelform']
        widgets = {
            'createmodelform': forms.TextInput(attrs={
                'id':"Hello",
                'placeholder': 'Add name ...',
                'class': 'p-4 text-black w-full rounded-lg border border-gray-300',
                'maxlength': '300',
                'autofocus': True,
            }),
        }

    createmodelform = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            'id':"Hello",
            'placeholder': 'Add name ...',
            'class': 'p-4 text-black w-full rounded-lg border border-gray-300',
            'maxlength': '300',
            'autofocus': True,
        })
    )


class JoinTournamentForm(ModelForm):
    class Meta:
        model = TournamentModels
        fields = ['joinmodelform']
        widgets = {
            'joinmodelform': forms.TextInput(attrs={
                'placeholder': 'Add name ...',
                'class': 'p-4 text-black w-full rounded-lg border border-gray-300',
                'maxlength': '300',
                'autofocus': True,
            }),
        }

    joinmodelform = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add name ...',
            'class': 'p-4 text-black w-full rounded-lg border border-gray-300',
            'maxlength': '300',
            'autofocus': True,
        })
    )

class namegameTournamentForm(ModelForm):
    class Meta:
        model = GameModel
        fields = ['namegamemodelform']
        widgets = {
            'namegamemodelform': forms.TextInput(attrs={
                'placeholder': 'Add name ...',
                'class': 'p-4 text-black w-full rounded-lg border border-gray-300',
                'maxlength': '300',
                'autofocus': True,
            }),
        }

    namegamemodelform = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add name ...',
            'class': 'p-4 text-black w-full rounded-lg border border-gray-300',
            'maxlength': '300',
            'autofocus': True,
        })
    )