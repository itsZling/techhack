import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
# Import BOTH utilities
from .spotify_utils import get_random_song_from_playlist
from .youtube_utils import get_random_video_from_playlist

connected_users = {}

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_name = self.scope['url_route']['kwargs']['lobby_id']
        self.lobby_group_name = f'lobby_{self.lobby_name}'
        self.username = self.scope['user'].username

        # 1. Create the lobby list if it doesn't exist yet
        if self.lobby_name not in connected_users:
            connected_users[self.lobby_name] = []
        
        # 2. Add the user to the list (if they aren't already in it)
        if self.username not in connected_users[self.lobby_name]:
            connected_users[self.lobby_name].append(self.username)

        # 3. Join the lobby group
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.accept()

        # 4. Broadcast the completely updated list to everyone
        await self.broadcast_player_list()

    async def disconnect(self, close_code):
        # 1. Remove the user from the list when they leave
        if self.lobby_name in connected_users:
            if self.username in connected_users[self.lobby_name]:
                connected_users[self.lobby_name].remove(self.username)
            
            # 2. If the room is empty, delete it from memory
            if len(connected_users[self.lobby_name]) == 0:
                del connected_users[self.lobby_name]
            else:
                # 3. Otherwise, broadcast the new list so the next person gets host status!
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

            # NEW: Switch logic based on mode
            song_data = None
            if game_mode == 'spotify':
                # Use the Spotify fetcher if mode is playlist
                song_data = await sync_to_async(get_random_song_from_playlist)(detail)
            elif game_mode == 'playlist': # Assuming you renamed it to 'playlist' in HTML
                # Use the YouTube fetcher
                song_data = await sync_to_async(get_random_video_from_playlist)(detail)

            # Check for errors from either service
            if game_mode in ['spotify', 'playlist']:
                if song_data is None or 'error' in song_data:
                    error_msg = song_data['error'] if (song_data and 'error' in song_data) else 'Invalid playlist link!'
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


    # --- CUSTOM EVENT HANDLERS ---

    async def broadcast_player_list(self):
        # Grabs the current list of players and sends it to the group
        players = connected_users.get(self.lobby_name, [])
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'player_list_update',
                'players': players
            }
        )

    async def player_list_update(self, event):
        # Sends the list specifically as a 'player_list' type to the JavaScript
        await self.send(text_data=json.dumps({
            'type': 'player_list',
            'players': event['players']
        }))

    async def lobby_message(self, event):
        # Sends the chat message to the JavaScript
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user']
        }))

    # ADD THIS NEW FUNCTION TO THE BOTTOM
    async def game_start_redirect(self, event):
        # Sends the redirect command and config to the JavaScript
        await self.send(text_data=json.dumps({
            'type': 'redirect',
            'game_mode': event['game_mode'],
            'rounds': event['rounds'],
            'detail': event['detail']
        }))