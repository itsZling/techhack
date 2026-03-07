from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .spotify_utils import get_random_song_from_playlist

# Create your views here.
def index(request, lobby_id):
    return render(request, 'lobby/index.html', {'lobby_id': lobby_id})

@login_required
def game(request):
    mode = request.GET.get('mode', 'genre')
    rounds = request.GET.get('rounds', '5')
    detail = request.GET.get('detail', 'none')
    lobby_id = request.GET.get('lobby_id', 'unknown')

    song_url, song_cover, song_name, song_artist = "", "", "", ""
    error_message = "" # Add a new error variable

    if mode == 'spotify':
        song_data = get_random_song_from_playlist(detail)
        if song_data:
            song_url = song_data['preview_url']
            song_cover = song_data['cover_art']
            song_name = song_data['name']
            song_artist = song_data['artist']
        else:
            # If song_data is None, pass this message to the HTML!
            error_message = "Spotify could not find any playable 30-second previews for this playlist."

    context = {
        'mode': mode, 'rounds': rounds, 'detail': detail, 'lobby_id': lobby_id,
        'song_url': song_url, 'song_cover': song_cover, 'song_name': song_name,
        'song_artist': song_artist, 
        'error_message': error_message, # Pass it to the template
    }
    return render(request, 'lobby/game.html', context)

def results(request):
    return render(request, 'lobby/results.html')
