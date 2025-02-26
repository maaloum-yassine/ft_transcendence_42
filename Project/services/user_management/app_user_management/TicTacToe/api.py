from ninja import NinjaAPI
from .schemas import TicTacToeGameSchema, TicTacToeGameCreateSchema, TicTacToeJoinGame, GameResponseSchema
from .models import TicTacToeGame
from django.shortcuts import get_object_or_404
from user_managemanet.models import CustomUser
from typing import List, Dict
from django.http import JsonResponse
from ninja.errors import HttpError
from django.http import JsonResponse

api = NinjaAPI(csrf=True, urls_namespace="tictactoe-api")

@api.get("/test", response=dict)
def test_endpoint(request):
    return {"message": "API is working"}

@api.post("/stats", response=List[GameResponseSchema])
def list_games(request, id_user: int):
    user = get_object_or_404(CustomUser, id=id_user)
    
    games = (
        TicTacToeGame.objects.filter(player_x=user, winner__isnull=False) |
        TicTacToeGame.objects.filter(player_o=user, winner__isnull=False)
    )
    serialized_games = [
        {
            "id": game.id,
            "player_x": game.player_x.username if game.player_x else None,
            "player_o": game.player_o.username if game.player_o else None,
            "board_state": game.board_state,
            "winner": game.winner,
            "status": determine_game_status(game, user),
        }
        for game in games
    ]
    
    return serialized_games

@api.post("/user_stats", response=Dict[str, int])
def user_stats(request, id_user: int):
    user = get_object_or_404(CustomUser, id=id_user)
    
    games = (
        TicTacToeGame.objects.filter(player_x=user, winner__isnull=False) |
        TicTacToeGame.objects.filter(player_o=user, winner__isnull=False)
    )

    total_games = games.count()
    wins = 0
    losses = 0
    draws = 0
    
    for game in games:
        if game.winner == 'X' and game.player_x == user:
            wins += 1
        elif game.winner == 'O' and game.player_o == user:
            wins += 1
        elif game.winner == 'D':
            draws += 1
        elif game.winner != 'D':
            if game.player_x == user:
                losses += 1
            elif game.player_o == user:
                losses += 1

    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
    }

def determine_game_status(game: TicTacToeGame, user):
    """Determine if the user won, lost, or if the game is ongoing."""
    if game.winner == 'D':
        return "Draw"
    elif game.winner == 'X' and game.player_x == user:
        return "Win"
    elif game.winner == 'O' and game.player_o == user:
        return "Win"
    elif game.winner:
        return "Lose"
    else:
        return "Ongoing"

@api.post("/games", response=TicTacToeGameSchema)
def create_game(request, game_data: TicTacToeGameCreateSchema):
    player_x = get_object_or_404(CustomUser, id=game_data.player_x)
    
    game = TicTacToeGame.objects.create(
        player_x=player_x,
        board_state=game_data.board_state
    )

    response_data = TicTacToeGameSchema.from_orm(game)
    return response_data

@api.get("/games/{game_id}/validate", response=dict)
def validate_game_id(request, game_id: int):
    """
    Validates if the provided game ID exists in the database.
    """
    game = get_object_or_404(TicTacToeGame, id=game_id)
    return {
        "id": game.id,
        "board_state": game.board_state,
        "current_turn": game.current_turn,
        "winner": game.winner,
    }

@api.get("/games/{game_id}", response=TicTacToeGameSchema)
def get_game(request, game_id: int):
    game = get_object_or_404(TicTacToeGame, id=game_id)
    response_data = TicTacToeGameSchema.from_orm(game)
    return response_data


@api.post("/games/{game_id}/join", response=dict)
def join_game(request, game_id: int, game_data: TicTacToeJoinGame):
    """
    Allows a second player to join an existing game.
    """
    user_id = game_data.player_o  
    game = get_object_or_404(TicTacToeGame, id=game_id)
    print(user_id)
    print(f"Current Player X: ID {game.player_x.id}, Username: {game.player_x.username}")
    print(f"Attempting to join with User ID: {user_id}")

    user = get_object_or_404(CustomUser, id=user_id)

    if game.player_x.id == user_id:
        return JsonResponse({
            "error": "You are already Player X in this game.",
            "details": f"User {user_id} is already Player X"
        }, status=400)

    if game.player_o:
        if game.player_o.id == user_id:
           return JsonResponse({
            "error": "You are already Player O in this game.",
            "details": f"User {user_id} is already Player O"
        }, status=400)
        
        return JsonResponse({
            "error": "This game already has two players.",
            "details": f"Game {game_id} is full"
        }, status=400)

    game.player_o = user
    game.save()

    return {
        "message": f"{user.username} joined the game as Player O", 
        "game_id": game.id
    }

@api.put("/games/{game_id}", response=TicTacToeGameSchema)
def update_game(request, game_id: int, game_data: TicTacToeGameCreateSchema):
    try:
        game = get_object_or_404(TicTacToeGame, id=game_id)

        if not game_data.board_state or len(game_data.board_state) != 9:
            raise HttpError(422, "Invalid board state")

        game.board_state = game_data.board_state

        game.current_turn = game_data.current_turn

        x_wins = check_win(game.board_state, 'X')
        o_wins = check_win(game.board_state, 'O')
        is_draw = is_board_full(game.board_state)

        if x_wins:
            game.winner = 'X'
        elif o_wins:
            game.winner = 'O'
        elif is_draw:
            game.winner = 'D'
        else:
            game.winner = game_data.winner

        game.save()  # Save the changes to the game

        return TicTacToeGameSchema.from_orm(game)

    except Exception as e:
        raise HttpError(422, f"Failed to update game state: {str(e)}")

def check_win(board_state: str, player: str) -> bool:
    """
    Check if the given player has won the game.
    
    Winning combinations:
    Horizontal: 0-1-2, 3-4-5, 6-7-8
    Vertical: 0-3-6, 1-4-7, 2-5-8
    Diagonal: 0-4-8, 2-4-6
    """
    win_combinations = [
        # Horizontal
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        # Vertical
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        # Diagonal
        (0, 4, 8),
        (2, 4, 6)
    ]
    
    for combo in win_combinations:
        if all(board_state[i] == player for i in combo):
            return True
    return False

def is_board_full(board_state: str) -> bool:
    """
    Check if the board is full (a draw condition).
    """
    return '-' not in board_state

@api.delete("/games/{game_id}", response=dict)
def delete_game(request, game_id: int):
    game = get_object_or_404(TicTacToeGame, id=game_id)
    game.delete()
    return {"success": True}

