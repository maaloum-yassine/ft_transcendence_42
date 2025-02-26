from channels.generic.websocket import AsyncWebsocketConsumer

from django.shortcuts import get_object_or_404

from .models import GameModel

import json
import asyncio
import random
from datetime import datetime

class GameConsumer(AsyncWebsocketConsumer):
    players = 0
    start_game = False
    game_task = None

    ballX = 0
    ballY = 0
    ballSpeedX = 300
    ballSpeedY = 300
    player1Score = 0
    player2Score = 0
    player1Y = 250
    player2Y = 250
    player1Velocity = 0
    player2Velocity = 0
    canvas_width = 1000
    canvas_height = 600
    table_left = 0
    table_right = 0
    paddle_speed = 400
    paddle_height = 100
    player1 = None
    player2 = None

    async def connect(self):
        # if not self.scope['user'].is_authenticated:
        #     return await self.close()
            
        self.room_name = self.scope['url_route']['kwargs']['group_name']
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope ['user']
        # self.gameroom = get_object_or_404(GameModel, gameroom_name=self.room_name)3

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Print the user that connects to the socket
        # print(f"User connected: {self.scope['user']}")
        GameConsumer.players += 1
        if GameConsumer.players == 1:
            self.paddle = 'paddle1'
            GameConsumer.player1 = self.scope['user']
        elif GameConsumer.players == 2:
            self.paddle = 'paddle2'
            GameConsumer.player2 = self.scope['user']
            GameConsumer.start_game = True
            # GameModel.game_started = True
            # GameModel.created_at = datetime.now()
            GameConsumer.reset_ball()
            await self.start_game_loop()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_start',
                    'start_game': GameConsumer.start_game,
                    'ballX': GameConsumer.ballX,
                    'ballY': GameConsumer.ballY,
                    'player1Y': GameConsumer.player1Y,
                    'player2Y': GameConsumer.player2Y
                }
            )
        else:
            await self.close()
            return

        await self.send(text_data=json.dumps({'paddle': self.paddle}))

    async def disconnect(self, close_code):

        #check winner
        # if GameConsumer.player1Score > GameConsumer.player2Score:
        #     GameModel.winner = GameConsumer.player1
        # else:
        #     GameModel.winner = GameConsumer.player2
        # print(f"Winner is {GameModel.winner}")

        GameConsumer.players -= 1

        if GameConsumer.players < 2:
            game_room = get_object_or_404(GameModel, room_name=self.room_name)
            game_room.game_ended = True
            game_room.save()

            GameConsumer.start_game = False
            
            if GameConsumer.game_task:
                GameConsumer.game_task.cancel()
                GameConsumer.game_task = None
        
        # GameModel.game_spend_time = datetime.now() - GameModel.created_at
        # GameModel.game_started = False
        # GameModel.game_ended = True
        # GameModel.save()

        # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_end',
                'game_ended': True
            }
        )
        
        await self.close()

    @staticmethod
    def reset_ball():
        GameConsumer.ballX = GameConsumer.canvas_width / 2
        GameConsumer.ballY = GameConsumer.canvas_height / 2
        GameConsumer.ballSpeedX = 300 * random.choice([-1, 1])
        GameConsumer.ballSpeedY = 300 * random.choice([-1, 1])

    async def start_game_loop(self):
        if not GameConsumer.game_task:
            GameConsumer.game_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        try:
            while GameConsumer.start_game:
                self.update_ball_position(0.016)
                self.update_paddle_position(0.016)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_state',
                        'player1Y': GameConsumer.player1Y,
                        'player2Y': GameConsumer.player2Y,
                        'ballX': GameConsumer.ballX,
                        'ballY': GameConsumer.ballY,
                        'player1Score': GameConsumer.player1Score,
                        'player2Score': GameConsumer.player2Score
                    }
                )

                await asyncio.sleep(0.016)
        except asyncio.CancelledError:
            pass

    def update_ball_position(self, delta_time):
        GameConsumer.ballX += GameConsumer.ballSpeedX * delta_time
        GameConsumer.ballY += GameConsumer.ballSpeedY * delta_time

        if GameConsumer.ballY <= GameConsumer.table_top + 15 or GameConsumer.ballY >= GameConsumer.table_bottom - 15:
            GameConsumer.ballSpeedY = -GameConsumer.ballSpeedY
        

        if GameConsumer.ballX <= GameConsumer.table_left + 30 and GameConsumer.player1Y <= GameConsumer.ballY <= GameConsumer.player1Y + GameConsumer.paddle_height:
            GameConsumer.ballSpeedX = -GameConsumer.ballSpeedX
        elif GameConsumer.ballX >= GameConsumer.table_right - 30 and GameConsumer.player2Y <= GameConsumer.ballY <= GameConsumer.player2Y + GameConsumer.paddle_height:
            GameConsumer.ballSpeedX = -GameConsumer.ballSpeedX

        if GameConsumer.ballX <= GameConsumer.table_left:
            GameConsumer.player2Score += 1
            GameConsumer.reset_ball()
        elif GameConsumer.ballX >= GameConsumer.table_right:
            GameConsumer.player1Score += 1
            GameConsumer.reset_ball()

    def update_paddle_position(self, delta_time):
        GameConsumer.player1Y += GameConsumer.player1Velocity * delta_time
        GameConsumer.player1Y = max(GameConsumer.table_top , min(GameConsumer.player1Y, GameConsumer.table_bottom - GameConsumer.paddle_height))


        GameConsumer.player2Y += GameConsumer.player2Velocity * delta_time
        GameConsumer.player2Y = max(GameConsumer.table_top , min(GameConsumer.player2Y, GameConsumer.table_bottom - GameConsumer.paddle_height))


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if text_data_json.get('type') == 'screen_dimensions':
            GameConsumer.canvas_width = text_data_json.get('width', 1000)
            GameConsumer.canvas_height = text_data_json.get('height', 600)
            GameConsumer.table_left = GameConsumer.canvas_width / 10
            GameConsumer.table_right = GameConsumer.canvas_width - GameConsumer.canvas_width / 10
            GameConsumer.table_top = GameConsumer.canvas_height / 10
            GameConsumer.table_bottom = GameConsumer.canvas_height - GameConsumer.canvas_height / 10

        if self.paddle == 'paddle1':
            GameConsumer.player1Velocity = text_data_json.get('velocity', 0)
        elif self.paddle == 'paddle2':
            GameConsumer.player2Velocity = text_data_json.get('velocity', 0)
        
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