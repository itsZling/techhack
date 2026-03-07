import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Global dictionary to track players in each lobby.
# Format: {'lobby_id': ['player1', 'player2', ...]}
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
        
        # 1. ONLY do this if the user sent a chat message
        if 'message' in data:
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'lobby_message',
                    'message': data['message'],
                    'user': self.username
                }
            )
            
        # 2. ONLY do this if the host clicked START
        elif data.get('type') == 'start_game':
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'game_start_redirect',
                    'game_mode': data['game_mode'],
                    'rounds': data['rounds'],
                    'detail': data['detail']
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
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Handle Chat Messages
        if 'message' in data:
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'lobby_message',
                    'message': data['message'],
                    'user': self.username
                }
            )
        # Handle Game Start Config
        elif data.get('type') == 'start_game':
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'game_start_redirect',
                    'game_mode': data['game_mode'],
                    'rounds': data['rounds'],
                    'detail': data['detail']
                }
            )

    # --- CUSTOM EVENT HANDLERS ---
    
    # ... (Keep your broadcast_player_list, player_list_update, and lobby_message functions here)

    # ADD THIS NEW FUNCTION TO THE BOTTOM
    async def game_start_redirect(self, event):
        # Sends the redirect command and config to the JavaScript
        await self.send(text_data=json.dumps({
            'type': 'redirect',
            'game_mode': event['game_mode'],
            'rounds': event['rounds'],
            'detail': event['detail']
        }))