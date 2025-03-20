from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameModel
from datetime import datetime
import json
import asyncio
import random

class GameConsumer(AsyncWebsocketConsumer):
    
    games = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['group_name']
        self.room_group_name = f'{self.room_name}'
        self.paddle = None

        
        if self.room_name not in GameConsumer.games:
            GameConsumer.games[self.room_name] = {
                'players': [],
                'game_task': None,
                'start_game': False,
                'player1Y': 250,
                'player2Y': 250,
                'ballX': 0,
                'ballY': 0,
                'player1Score': 0,
                'player2Score': 0,
                'winner': None,
                'Player1name': None,
                'Player2name': None,
                'canvas_width': 1000,
                'canvas_height': 600,
                'table_left': 0,
                'table_right': 1000,
                'table_top': 0,
                'table_bottom': 600,
                'paddle_height': 100,
                'paddle_speed': 400,
                'ballSpeedX': 300,
                'ballSpeedY': 300
            }

        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        game_state = GameConsumer.games[self.room_name]
        game_state['players'].append(self.channel_name)

        
        if len(game_state['players']) == 1:
            self.paddle = 'paddle1'
            game_state['Player1name'] = self.scope['user'].username

        elif len(game_state['players']) == 2:
            self.paddle = 'paddle2'
            game_state['Player2name'] = self.scope['user'].username
            game_state['start_game'] = True
            
            
            self.reset_ball(game_state)

            
            await self.start_game_loop()

            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_start',
                    'start_game': game_state['start_game'],
                    'ballX': game_state['ballX'],
                    'ballY': game_state['ballY'],
                    'player1Y': game_state['player1Y'],
                    'player2Y': game_state['player2Y']
                }
            )

        else:
            
            await self.close()
            return

        
        await self.send(text_data=json.dumps({'paddle': self.paddle}))

    async def disconnect(self, close_code):
        game_state = GameConsumer.games[self.room_name]
        
        
        if self.channel_name in game_state['players']:
            game_state['players'].remove(self.channel_name)

        
        if len(game_state['players']) < 2:
            game_state['start_game'] = False
            
            
            if game_state['game_task']:
                game_state['game_task'].cancel()
                game_state['game_task'] = None

        await self.game_ended_in_db()    
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def game_ended_in_db(self):
        try:
            game = GameModel.objects.get(room_name=self.room_group_name)
            game_state = GameConsumer.games[self.room_name]
            
            game.game_ended = True
            game.player1Score = game_state['player1Score']
            game.player2Score = game_state['player2Score']
            
            
            time_hours = datetime.now().hour - game.created_at.hour
            time_minute = datetime.now().minute - game.created_at.minute
            time_second = datetime.now().second - game.created_at.second
            game.game_spend_time = f"0{time_hours}:0{time_minute}:{time_second}"
            
            
            if game.winner is None:
                if game_state['player2Score'] > game_state['player1Score']:
                    game.winner = game_state['Player2name']
                elif game_state['player2Score'] < game_state['player1Score']:
                    game.winner = game_state['Player1name']
                else:
                    
                    game.winner = game_state['Player2name']
            else:
                game.winner = game_state['winner']

            game.save()
            print(f"Game ended and saved in DB for room: {self.room_group_name}")

        except GameModel.DoesNotExist:
            print(f"Game not found for room: {self.room_group_name}")

    def reset_ball(self, game_state):
        
        game_state['ballX'] = game_state['canvas_width'] / 2
        game_state['ballY'] = game_state['canvas_height'] / 2
        game_state['ballSpeedX'] = 300 * random.choice([-1, 1])
        game_state['ballSpeedY'] = 300 * random.choice([-1, 1])

    async def start_game_loop(self):
        game_state = GameConsumer.games[self.room_name]
        
        
        if not game_state['game_task']:
            game_state['game_task'] = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        game_state = GameConsumer.games[self.room_name]

        try:
            while game_state['start_game']:
                
                self.update_ball_position(game_state, 0.016)
                self.update_paddle_position(game_state, 0.016)

                
                if game_state['player1Score'] == 5:
                    game_state['winner'] = game_state['Player1name']
                    await self.end_game(game_state)

                elif game_state['player2Score'] == 5:
                    game_state['winner'] = game_state['Player2name']
                    await self.end_game(game_state)

                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_state',
                        'player1Y': game_state['player1Y'],
                        'player2Y': game_state['player2Y'],
                        'ballX': game_state['ballX'],
                        'ballY': game_state['ballY'],
                        'player1Score': game_state['player1Score'],
                        'player2Score': game_state['player2Score'],
                        'winner': game_state['winner']
                    }
                )

                await asyncio.sleep(0.016)
            game_state.save()
        except asyncio.CancelledError:
            pass

    def update_ball_position(self, game_state, delta_time):
        
        game_state['ballX'] += game_state['ballSpeedX'] * delta_time
        game_state['ballY'] += game_state['ballSpeedY'] * delta_time

        
        if (game_state['ballY'] <= game_state['table_top'] + 15 or 
            game_state['ballY'] >= game_state['table_bottom'] - 15):
            game_state['ballSpeedY'] = -game_state['ballSpeedY']

        
        if (game_state['ballX'] <= game_state['table_left'] + 30 and 
            game_state['player1Y'] <= game_state['ballY'] <= game_state['player1Y'] + game_state['paddle_height']):
            game_state['ballSpeedX'] = -game_state['ballSpeedX']

        elif (game_state['ballX'] >= game_state['table_right'] - 30 and 
              game_state['player2Y'] <= game_state['ballY'] <= game_state['player2Y'] + game_state['paddle_height']):
            game_state['ballSpeedX'] = -game_state['ballSpeedX']

        
        if game_state['ballX'] <= game_state['table_left'] + 10:
            game_state['player2Score'] += 1
            self.reset_ball(game_state)

        if game_state['ballX'] >= game_state['table_right'] - 10:
            game_state['player1Score'] += 1
            self.reset_ball(game_state)

    def update_paddle_position(self, game_state, delta_time):
        
        game_state['player1Y'] += game_state.get('player1Velocity', 0) * delta_time
        game_state['player1Y'] = max(
            game_state['table_top'], 
            min(game_state['player1Y'], game_state['table_bottom'] - game_state['paddle_height'])
        )

        
        game_state['player2Y'] += game_state.get('player2Velocity', 0) * delta_time
        game_state['player2Y'] = max(
            game_state['table_top'], 
            min(game_state['player2Y'], game_state['table_bottom'] - game_state['paddle_height'])
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        game_state = GameConsumer.games[self.room_name]

        
        if text_data_json.get('type') == 'screen_dimensions':
            game_state['canvas_width'] = text_data_json.get('width', 1000)
            game_state['canvas_height'] = text_data_json.get('height', 600)
            game_state['table_left'] = game_state['canvas_width'] / 10
            game_state['table_right'] = game_state['canvas_width'] - game_state['canvas_width'] / 10
            game_state['table_top'] = game_state['canvas_height'] / 10
            game_state['table_bottom'] = game_state['canvas_height'] - game_state['canvas_height'] / 10

        
        if self.paddle == 'paddle1':
            game_state['player1Velocity'] = text_data_json.get('velocity', 0)
        elif self.paddle == 'paddle2':
            game_state['player2Velocity'] = text_data_json.get('velocity', 0)

    async def end_game(self, game_state):
        await self.game_ended_in_db()    

        game_state['start_game'] = False

        try:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'game_end',
                'winner': game_state['winner'],
                'redirect_url': '/profile/'
            })
        except Exception as e:
            print(f"Error sending game end notification: {e}")

    async def game_state(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'start_game': event['start_game'],
            'ballX': event['ballX'],
            'ballY': event['ballY'],
            'player1Y': event['player1Y'],
            'player2Y': event['player2Y']
        }))

    async def game_end(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_end',
            'winner': event['winner'],
            'url': event.get('redirect_url', '/profile/')
        }))