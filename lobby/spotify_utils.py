import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

def get_random_song_from_playlist(playlist_url):
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.environ.get('SPOTIPY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # 1. Safely extract the ID
        if 'playlist/' in playlist_url:
            playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
        else:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]

        # 2. Try to fetch the playlist
        try:
            results = sp.playlist_tracks(playlist_id)
        except Exception as e:
            print(f"Spotify API Error: {e}")
            return {"error": "Invalid link! Make sure it is a public 'open.spotify.com/playlist/...' link."}

        tracks = results.get('items', [])
        
        # 3. Filter for playable tracks
        valid_tracks = []
        for item in tracks:
            track = item.get('track')
            if track and track.get('preview_url'):
                valid_tracks.append(track)

        if not valid_tracks:
            return {"error": "Spotify blocked the previews for EVERY song in this playlist! Try an indie or older playlist."}

        # 4. Success! Pick a track
        random_track = random.choice(valid_tracks)

        return {
            'name': random_track['name'],
            'artist': random_track['artists'][0]['name'],
            'preview_url': random_track['preview_url'], 
            'cover_art': random_track['album']['images'][0]['url'] if random_track['album']['images'] else None
        }

    except Exception as e:
        print(f"Server Fetch Error: {e}")
        return {"error": f"Server Error: {str(e)}"}
    
def get_random_song_by_artist(artist_name):
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.environ.get('SPOTIPY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Ask Spotify to search for tracks specifically by this artist
        # We replace underscores from your HTML dropdown with spaces
        clean_artist = artist_name.replace("_", " ")
        results = sp.search(q=f'artist:{clean_artist}', type='track', limit=50)
        tracks = results['tracks']['items']
        
        # Filter for playable tracks
        valid_tracks = [track for track in tracks if track.get('preview_url')]
        
        if not valid_tracks:
            return {"error": f"No playable previews found for artist: {clean_artist}."}
            
        # Pick a random track
        random_track = random.choice(valid_tracks)
        
        return {
            'name': random_track['name'],
            'artist': random_track['artists'][0]['name'],
            'preview_url': random_track['preview_url'],
            'cover_art': random_track['album']['images'][0]['url'] if random_track['album']['images'] else None
        }
    except Exception as e:
        print(f"Spotify Artist Error: {e}")
        return {"error": "Failed to connect to Spotify for Artist search."}

def get_random_song_by_genre(genre_name):
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.environ.get('SPOTIPY_CLIENT_ID'),
            client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Ask Spotify to search for tracks specifically in this genre
        results = sp.search(q=f'genre:{genre_name}', type='track', limit=50)
        tracks = results['tracks']['items']
        
        valid_tracks = [track for track in tracks if track.get('preview_url')]
        
        if not valid_tracks:
            return {"error": f"No playable previews found for genre: {genre_name}."}
            
        random_track = random.choice(valid_tracks)
        
        return {
            'name': random_track['name'],
            'artist': random_track['artists'][0]['name'],
            'preview_url': random_track['preview_url'],
            'cover_art': random_track['album']['images'][0]['url'] if random_track['album']['images'] else None
        }
    except Exception as e:
        print(f"Spotify Genre Error: {e}")
        return {"error": "Failed to connect to Spotify for Genre search."}