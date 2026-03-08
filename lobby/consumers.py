import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .youtube_utils import get_random_video_from_playlist # Import YouTube instead

connected_users = {}
game_state = {}

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
        
        state = game_state.get(self.lobby_name)
        
        if data.get('type') == 'start_game':
            players = connected_users.get(self.lobby_name, [])
            song_data = await sync_to_async(get_random_video_from_playlist)(data.get('detail'))
            
            # Initialize scoring and round state
            game_state[self.lobby_name] = {
                'current_round': 1,
                'total_rounds': int(data.get('rounds', 5)),
                'playlist_url': data.get('detail'),
                'current_answer': song_data['name'],
                'guessed_correctly': [], # Reset every round
                'scores': {user: 0 for user in players} # Persistent scores
            }
            
            await self.channel_layer.group_send(self.lobby_group_name, {
                'type': 'game_start_redirect',
                'game_mode': data.get('game_mode'),
                'rounds': data.get('rounds'),
                'detail': data.get('detail')
            })

        # --- 2. Handle Guess Submissions ---
        elif data.get('type') == 'submit_guess':
            if not state or self.username in state['guessed_correctly']:
                return

            guess = data.get('guess', '').strip().lower()
            answer = state['current_answer'].strip().lower()

            if guess == answer:
                # Add user to the 'correct' list for this round
                state['guessed_correctly'].append(self.username)
                
                # Calculate Points: 5 * (Total Players - Number of people who already guessed)
                players = connected_users.get(self.lobby_name, [])
                total_players = len(players)
                rank = len(state['guessed_correctly'])
                points_earned = 5 * (total_players - (rank - 1))
                
                state['scores'][self.username] += points_earned

                # Broadcast the correct guess and updated leaderboard
                await self.channel_layer.group_send(self.lobby_group_name, {
                    'type': 'points_update',
                    'user': self.username,
                    'points': points_earned,
                    'leaderboard': state['scores']
                })

        # --- 3. Handle Next Round ---
        elif data.get('type') == 'next_round':
            if not state: return
            if state['current_round'] < state['total_rounds']:
                state['current_round'] += 1
                state['guessed_correctly'] = [] # Reset guessers for new round
                
                song_data = await sync_to_async(get_random_video_from_playlist)(state['playlist_url'])
                state['current_answer'] = song_data['name'] # Update the server's answer key
                
                await self.channel_layer.group_send(self.lobby_group_name, {
                    'type': 'load_new_round',
                    'round_number': state['current_round'],
                    'song_data': song_data
                })
            else:
                await self.channel_layer.group_send(self.lobby_group_name, {'type': 'game_over'})

    async def broadcast_player_list(self):
        players = connected_users.get(self.lobby_name, [])
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {'type': 'player_list_update', 'players': players}
        )

    async def points_update(self, event):
            await self.send(text_data=json.dumps(event))

    async def load_new_round(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({'type': 'game_over'}))
        
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