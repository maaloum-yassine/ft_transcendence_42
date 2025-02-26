import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import AuthMiddlewareStack

class TicTacToeConsumer(AsyncWebsocketConsumer):
    room_states = {}

    async def connect(self):
        user = self.scope.get("user")
        if not user.is_authenticated:
            await self.close()
            return
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"tictactoe_{self.room_name}"

        if self.room_name not in self.room_states:
            self.room_states[self.room_name] = {
                'board': [None] * 9,
                'players': [],
                'current_turn': None
            }
        room_state = self.room_states[self.room_name]

        if len(room_state['players']) >= 2:
            await self.close()
            return

        self.player_symbol = 'X' if len(room_state['players']) == 0 else 'O'
        room_state['players'].append(self.player_symbol)

        if len(room_state['players']) == 2:
            room_state['current_turn'] = 'X'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "player_assigned",
            "symbol": self.player_symbol,
            "is_first_player": self.player_symbol == 'X',
            "start_game": False
        }))

        if len(room_state['players']) == 2:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_start",
                    "start_game": True
                }
            )

    async def handle_move(self, position, symbol):
        if self.board_state[position] is None:
            self.board_state[position] = symbol
            await self.send_board_update(position, symbol)
        else:
            print("Invalid move attempted!")

    async def check_win(self, board):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        for combo in winning_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] is not None:
                return board[combo[0]]

        if all(cell is not None for cell in board):
            return "draw"

        return None

    async def send_board_update(self, position, symbol):
        print(f"Sending board update: {self.board_state}")
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "board_update",
                "position": position,
                "symbol": symbol,
                "board_state": self.board_state,
                "current_turn": self.get_current_turn(),
            },
        )


    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            "type": "game_start",
            "start_game": True,
            "message": "Game is starting. X goes first!"
        }))
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")
        room_state = self.room_states[self.room_name]

        if message_type == "make_move":
            position = data.get("position")
            symbol = data.get("symbol")

            if (not isinstance(position, int) or 
                not (0 <= position < 9) or 
                room_state['board'][position] is not None or
                room_state['current_turn'] != symbol):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Invalid move"
                }))
                return

            room_state['board'][position] = symbol
            room_state['current_turn'] = 'O' if symbol == 'X' else 'X'
            winner = await self.check_win(room_state['board'])
            if winner:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_end",
                        "winner": winner
                    }
                )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_update",
                        "position": position,
                        "symbol": symbol,
                        "board_state": room_state['board'],
                        "current_turn": room_state['current_turn']
                    }
                )

    async def game_update(self, event):
        print("Handling game_update event:", event)
        await self.send(text_data=json.dumps({
            "type": "board_update",
            "position": event["position"],
            "symbol": event["symbol"],
            "board_state": event["board_state"],
            "current_turn": event["current_turn"]
        }))
    async def final_update(self, event):
        winner = event["winner"]
        loser = event["loser"]
        final_board = event["board_state"]
        message = event["message"]

        if self.player_symbol == loser:
            personal_message = "You lost! Better luck next time!"
        elif self.player_symbol == winner:
            personal_message = "Congratulations! You won!"
        else:
            personal_message = "It's a draw!"

        await self.send(text_data=json.dumps({
            "type": "game_end",
            "board_state": final_board,
            "winner": winner,
            "message": message,
            "personal_message": personal_message
        }))

    async def game_end(self, event):
        winner = event["winner"]
        room_state = self.room_states[self.room_name]
        final_board = room_state['board']

        await self.send(text_data=json.dumps({
            "type": "game_end",
            "winner": winner,
            "board_state": final_board,
            "message": f"Game Over! {winner} wins!" if winner != "draw" else "Game Over! It's a draw."
        }))


    async def disconnect(self, close_code):
        if self.room_name in self.room_states:
            room_state = self.room_states[self.room_name]
            if self.player_symbol in room_state['players']:
                room_state['players'].remove(self.player_symbol)
            if not room_state['players']:
                del self.room_states[self.room_name]

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print("Player disconnected:", self.player_symbol)
