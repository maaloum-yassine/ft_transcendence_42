from django.db import models
from django.conf import settings
from user_managemanet.models import CustomUser

class TicTacToeGame(models.Model):
    player_x = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='games_as_x')
    player_o = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='games_as_o', null=True, blank=True)
    board_state = models.CharField(max_length=9, default="---------")  # 9 dashes represent an empty board
    current_turn = models.CharField(max_length=1, choices=[('X', 'Player X'), ('O', 'Player O')], default='X')
    winner = models.CharField(max_length=1, choices=[('X', 'Player X'), ('O', 'Player O'), ('D', 'Draw')], null=True, blank=True)

    def set_winner(self, winner: str):
        """Set the winner of the game."""
        if winner in ['X', 'O', 'D']:
            self.winner = winner
            self.save()

    def __str__(self):
        return f"Game {self.id} between {self.player_x} and {self.player_o}"
