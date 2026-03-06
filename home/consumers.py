import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_name = self.scope['url_route']['kwargs']['lobby_id']
        self.lobby_group_name = f'lobby_{self.lobby_name}'

        # Join the lobby group
        await self.channel_layer.group_add(self.lobby_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Broadcast the message/action to everyone in the lobby
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'lobby_message',
                'message': data['message'],
                'user': self.scope['user'].username
            }
        )

    async def lobby_message(self, event):
        # This sends the data to the actual WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user']
        }))