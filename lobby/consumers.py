import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'lobby_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.room_group_name, {'type': 'player_joined', 'username': 'New Player',})
    
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({'type': 'new_player', 'username': event['username']}))
        
