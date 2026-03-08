import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .youtube_utils import get_random_video_from_playlist # Import YouTube instead

connected_users = {}

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_name = self.scope['url_route']['kwargs']['lobby_id']
        self.lobby_group_name = f'lobby_{self.lobby_name}'
        self.username = self.scope['user'].username
        if self.lobby_name not in connected_users:
            connected_users[self.lobby_name] = []
        if self.username not in connected_users[self.lobby_name]:
            connected_users[self.lobby_name].append(self.username)
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.accept()
        await self.broadcast_player_list()

    async def disconnect(self, close_code):
        if self.lobby_name in connected_users:
            if self.username in connected_users[self.lobby_name]:
                connected_users[self.lobby_name].remove(self.username)
            if len(connected_users[self.lobby_name]) == 0:
                del connected_users[self.lobby_name]
            else:
                await self.broadcast_player_list()
        await self.channel_layer.group_discard(self.lobby_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'message' in data:
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {'type': 'lobby_message', 'message': data['message'], 'user': self.username}
            )
        elif data.get('type') == 'start_game':
            game_mode = data.get('game_mode')
            detail = data.get('detail')

            # VALIDATE YOUTUBE LINK
            if game_mode == 'spotify' or game_mode == 'playlist':
                # FETCH DATA FIRST
                song_data = await sync_to_async(get_random_video_from_playlist)(detail)
                
                # THEN CHECK FOR ERRORS
                if song_data is None or 'error' in song_data:
                    error_msg = song_data['error'] if (song_data and 'error' in song_data) else 'Invalid YouTube link!'
                    await self.send(text_data=json.dumps({'type': 'lobby_error', 'message': error_msg}))
                    return 

            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'game_start_redirect',
                    'game_mode': game_mode,
                    'rounds': data.get('rounds'),
                    'detail': detail
                }
            )

    async def broadcast_player_list(self):
        players = connected_users.get(self.lobby_name, [])
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {'type': 'player_list_update', 'players': players}
        )

    async def player_list_update(self, event):
        await self.send(text_data=json.dumps({'type': 'player_list', 'players': event['players']}))

    async def lobby_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message'], 'user': event['user']}))

    async def game_start_redirect(self, event):
        await self.send(text_data=json.dumps({
            'type': 'redirect',
            'game_mode': event['game_mode'],
            'rounds': event['rounds'],
            'detail': event['detail']
        }))