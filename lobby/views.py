from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .spotify_utils import get_random_song_from_playlist, get_random_song_by_artist, get_random_song_by_genre

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
    error_message = ""

    song_data = None
    if mode == 'spotify':
        song_data = get_random_song_from_playlist(detail)
    elif mode == 'genre':
        song_data = get_random_song_by_genre(detail)
    elif mode == 'artist':
        song_data = get_random_song_by_artist(detail)
        
    if song_data:
        song_url = song_data['preview_url']
        song_cover = song_data['cover_art']
        song_name = song_data['name']
        song_artist = song_data['artist']
    else:
        error_message = f"Spotify could not find any playable 30-second previews for this {mode}."

    context = {
        'mode': mode, 'rounds': rounds, 'detail': detail, 'lobby_id': lobby_id,
        'song_url': song_url, 'song_cover': song_cover, 'song_name': song_name,
        'song_artist': song_artist, 
        'error_message': error_message,
    }
    return render(request, 'lobby/game.html', context)

def results(request):
    return render(request, 'lobby/results.html')
