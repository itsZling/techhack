import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .youtube_utils import get_random_video_from_playlist

connected_users = {}
game_state = {}

GENRE_PLAYLISTS = {
    'rap': 'https://www.youtube.com/watch?v=D8fHatctfRo&list=PLm7wnjUQm_FAd_pmjhhWz0MRnGdUDptg4',
    'pop': 'https://www.youtube.com/watch?v=ekr2nIex040&list=PLuJAH0gKWEN686Jh6fQIlO0ue4O-nCK80',
    'emo': 'https://www.youtube.com/watch?v=kXYiU_JCYtU&list=PLoSw9A7teER13dJv-HEAOotSgY_YmqS0h',
    'genre': 'https://www.youtube.com/watch?v=uXZkGWbyvcM&list=RDqj1GooBp0ss&index=1',
}

ARTIST_PLAYLISTS = {
    'bear_ghost': 'https://youtube.com/playlist?list=PLatQ_1ySwOFK5I5L0wbvBKzvv6-gIH8DJ&si=071jYlwbyQjK5hQC',
    'bruno_mars': 'https://youtube.com/playlist?list=PLcXtXCm2EMK_L2b7aF-QcW9WvgDr5thpj&si=6VisRq4V_xM5zQr8',
    'set_it_off': 'https://youtube.com/playlist?list=PLuSVDZ9w-aOgC-U_4cdPLHQ4RbJMDxNrs&si=rw14fPTbuD6NipKY',
    'tyler_the_creator': 'https://youtube.com/playlist?list=PLD2X1LpnqWOO7hHW_zB6xUPhH3vjRmobB&si=aZTJfXUqdUh4zB_I',
    'laufey': 'https://www.youtube.com/watch?v=mwverOouSuo&list=PLpeaYh4ivZkPJn3-eLLy5OnEU0RvvTK_H&index=1',
    'artist': 'https://www.youtube.com/watch?v=uXZkGWbyvcM&list=RDqj1GooBp0ss&index=1',
}

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
        
        state = game_state.get(self.lobby_name)
        if state:
            await self.send(text_data=json.dumps({
                'type': 'initial_song_data',
                'round_number': state['current_round'],
                'song_data': {
                    'name': state['current_answer'],
                    'artist': state.get('current_artist', 'Unknown'),
                    'video_id': state.get('current_video_id'),
                    'cover_art': state.get('current_cover')
                },
                'leaderboard': state['scores']
            }))

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
        state = game_state.get(self.lobby_name)
        data = json.loads(text_data)
        
        if data.get('type') == 'start_game':
            game_mode = data.get('game_mode')
            players = connected_users.get(self.lobby_name, [])
            detail = data.get('detail')
            
            # Updated Logic: Check both dictionaries based on the mode
            if game_mode == 'genre':
                playlist_url = GENRE_PLAYLISTS.get(detail, detail)
            elif game_mode == 'artist':
                playlist_url = ARTIST_PLAYLISTS.get(detail, detail)
            else:
                playlist_url = detail
            
            song_data = await sync_to_async(get_random_video_from_playlist)(playlist_url)
            
            if song_data is None or 'error' in song_data:
                error_msg = song_data['error'] if (song_data and 'error' in song_data) else 'Invalid YouTube link!'
                await self.send(text_data=json.dumps({'type': 'lobby_error', 'message': error_msg}))
                return
            
            # Initialize scoring and round state
            game_state[self.lobby_name] = {
                'current_round': 1,
                'total_rounds': int(data.get('rounds', 5)),
                
                # BUG FIX: Change this from 'detail' to 'playlist_url'
                'playlist_url': playlist_url, 
                
                'current_answer': song_data['name'],
                'current_artist': song_data['artist'], 
                'current_video_id': song_data['video_id'],
                'current_cover': song_data['cover_art'],
                'guessed_correctly': [],
                'has_guessed': [],
                'scores': {user: 0 for user in players}
            }
            
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'game_start_redirect',
                    'game_mode': game_mode,
                    'rounds': data.get('rounds'),
                    'detail': detail
                }
            )
            
        elif data.get('type') == 'chat_message':
            await self.channel_layer.group_send(
                self.lobby_group_name, 
                {
                    'type': 'lobby_message',
                    'user': self.username,
                    'message': data.get('message')
                }
            )

        # --- 2. Handle Guess Submissions ---
        elif data.get('type') == 'submit_guess':
            if not state or self.username in state['has_guessed']:
                return

            state['has_guessed'].append(self.username)

            guess = data.get('guess', '').strip().lower()
            answer = state['current_answer'].strip().lower()
            

            if guess and guess in answer and len(guess) > 2:
                state['guessed_correctly'].append(self.username)
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
            else:
                await self.send(text_data=json.dumps({
                    'type': 'incorrect_guess',
                    'user': self.username
                }))
                
            players_in_lobby = connected_users.get(self.lobby_name, [])
            if len(state['has_guessed']) >= len(players_in_lobby):
                # Trigger next round immediately because everyone has tried!
                await self.receive(json.dumps({'type': 'round_reveal'}))

        # --- 3. Handle Next Round ---
        elif data.get('type') == 'next_round':
            if not state: return

            if state['current_round'] < state['total_rounds']:
                song_data = await sync_to_async(get_random_video_from_playlist)(state['playlist_url'])
                
                if not song_data or 'error' in song_data:
                    await self.channel_layer.group_send(self.lobby_group_name, {
                        'type': 'lobby_message',
                        'user': 'SYSTEM',
                        'message': 'Error fetching next song. Skipping...'
                    })
                    return

                state['current_round'] += 1
                state['guessed_correctly'] = []
                state['has_guessed'] = []
                state['current_answer'] = song_data['name'] # This is now safe!
                state['current_artist'] = song_data.get('artist', 'Unknown')
                state['current_video_id'] = song_data.get('video_id')
                state['current_cover'] = song_data.get('cover_art')
                
                
                await self.channel_layer.group_send(self.lobby_group_name, {
                    'type': 'load_new_round',
                    'round_number': state['current_round'],
                    'song_data': song_data
                })
            else:
                await self.channel_layer.group_send(self.lobby_group_name, {'type': 'game_over'})
        
        elif data.get('type') == 'round_reveal':
            await self.channel_layer.group_send(self.lobby_group_name, {'type': 'round_reveal'})

    async def broadcast_player_list(self):
        players = connected_users.get(self.lobby_name, [])
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {'type': 'player_list_update', 'players': players}
        )
        
    async def round_reveal(self, event):
        await self.send(text_data=json.dumps({'type': 'round_reveal'}))

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