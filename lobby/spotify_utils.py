import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_random_song_from_playlist(playlist_url):
    try:
        # Move authentication inside the try block so it fails gracefully!
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.environ.get('SPOTIPY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Safely extract the ID (handles weirdly formatted links)
        if 'playlist/' in playlist_url:
            playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
        else:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]

        # Fetch the tracks
        results = sp.playlist_tracks(playlist_id)
        tracks = results.get('items', [])
        
        # Filter out tracks that labels have blocked the previews for
        valid_tracks = []
        for item in tracks:
            track = item.get('track')
            if track and track.get('preview_url'):
                valid_tracks.append(track)

        if not valid_tracks:
            return None # No playable tracks found

        # Pick a random track
        random_track = random.choice(valid_tracks)

        song_data = {
            'name': random_track['name'],
            'artist': random_track['artists'][0]['name'],
            'preview_url': random_track['preview_url'], 
            'cover_art': random_track['album']['images'][0]['url'] if random_track['album']['images'] else None
        }

        return song_data

    except Exception as e:
        print(f"Spotify Fetch Error: {e}")
        return None