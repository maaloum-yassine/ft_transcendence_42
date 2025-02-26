from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import TournamentModels, TournamentMatch
import json
import logging

logger = logging.getLogger(__name__)


class TournamentConsumer(AsyncWebsocketConsumer):

    ready_players = []

    async def connect(self):
        self.user = self.scope['user']
        self.tournament_name = self.scope['url_route']['kwargs']['tournament_name']
        self.group_name = f'tournament_{self.tournament_name}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        try:
            tournament = await self.get_tournament()
            if tournament:
                await self.update_members_list()
            else:
                logger.warning(f"Tournament not found: {self.tournament_name}")
        except Exception as e:
            logger.error(f"Error connecting to tournament: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'join':
                await self.update_members_list()
            elif action == 'player_ready':
                await self.handle_player_ready()
        except Exception as e:
            logger.error(f"Error receiving WebSocket message: {e}")


    async def handle_player_ready(self):
        tournament = await self.get_tournament()
        self.ready_players.append(self.user.username)

        tournament_members = await self.get_players_in_tournament()

        if len(self.ready_players) <= 2:
            game_room = tournament.game1_name
        else:
            game_room = tournament.game2_name

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'player_ready_update',
                'ready_players': list(self.ready_players),
                'tournament_members': tournament_members,
            }
        )

        await self.send(text_data=json.dumps({
            'type': 'redirect_to_game',
            'tournament_members': tournament_members,
            'ready_user': self.user.username,
            'game_room': game_room
        }))

    async def redirect_to_game(self, event):
        pass

    async def player_ready_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_ready_update',
            'ready_players': event['ready_players'],
            'tournament_members': event['tournament_members']
        }))

    async def update_members_list(self):
        try:
            tournament_members = await self.get_players_in_tournament()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'tournament_members_handler',
                    'tournament_members': tournament_members
                }
            )
        except Exception as e:
            logger.error(f"Error updating members list: {e}")


    @database_sync_to_async
    def get_tournament(self):
        try:
            return TournamentModels.objects.get(tournament_name=self.tournament_name)
        except TournamentModels.DoesNotExist:
            return None

    @database_sync_to_async
    def get_tournament_match(self):
        try:
            return TournamentMatch.objects.get(tournament__tournament_name=self.tournament_name)
        except TournamentMatch.DoesNotExist:
            return None


    @database_sync_to_async
    def get_players_in_tournament(self):
        try:
            tournament = TournamentModels.objects.get(tournament_name=self.tournament_name)
            players = tournament.tournament_members.all()
            return [player.username for player in players]
        except TournamentModels.DoesNotExist:
            logger.warning(f"Tournament not found when getting players: {self.tournament_name}")
            return []

    @database_sync_to_async
    def remove_user_from_tournament(self):
        try:
            tournament = TournamentModels.objects.get(tournament_name=self.tournament_name)
            tournament.tournament_members.remove(self.user)
        except TournamentModels.DoesNotExist:
            logger.warning(f"Tournament not found when removing user: {self.tournament_name}")

    async def tournament_members_handler(self, event):
        await self.send(text_data=json.dumps({
            'type': 'tournament_members_handler',
            'tournament_members': event['tournament_members']
        }))
