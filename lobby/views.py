from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Make sure all three of your Spotify tools are imported!
from .spotify_utils import get_random_song_from_playlist, get_random_song_by_artist, get_random_song_by_genre

def index(request, lobby_id):
    return render(request, 'lobby/index.html', {'lobby_id': lobby_id})

@login_required
def game(request):
    mode = request.GET.get('mode', 'genre')
    rounds = request.GET.get('rounds', '5')
    detail = request.GET.get('detail', 'none')
    lobby_id = request.GET.get('lobby_id', 'unknown')

    song_url, song_cover, song_name, song_artist = "", "", "", ""
    error_message = ""

    # Fetch the song based on the game mode
    song_data = None
    if mode == 'spotify':
        song_data = get_random_song_from_playlist(detail)
    elif mode == 'genre':
        song_data = get_random_song_by_genre(detail)
    elif mode == 'artist':
        song_data = get_random_song_by_artist(detail)
        
    # Check if song_data exists AND it does NOT contain our custom error message
    if song_data and 'error' not in song_data:
        song_url = song_data['preview_url']
        song_cover = song_data['cover_art']
        song_name = song_data['name']
        song_artist = song_data['artist']
    else:
        # If it returned a specific error from spotify_utils, use that.
        # Otherwise, fall back to a generic error message.
        if song_data and 'error' in song_data:
            error_message = song_data['error']
        else:
            error_message = f"Spotify could not find any playable 30-second previews for this {mode}."

    context = {
        'mode': mode,
        'rounds': rounds,
        'detail': detail,
        'lobby_id': lobby_id,
        'song_url': song_url,
        'song_cover': song_cover,
        'song_name': song_name,
        'song_artist': song_artist,
        'error_message': error_message,
    }

    return render(request, 'lobby/game.html', context)

@login_required
def results(request):
    # A basic placeholder view so your urls.py doesn't throw an error!
    return render(request, 'lobby/results.html')