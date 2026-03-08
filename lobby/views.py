from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .youtube_utils import get_random_video_from_playlist

def index(request, lobby_id):
    return render(request, 'lobby/index.html', {'lobby_id': lobby_id})

@login_required
def game(request):
    mode = request.GET.get('mode', 'genre')
    rounds = request.GET.get('rounds', '5')
    detail = request.GET.get('detail', 'none')
    lobby_id = request.GET.get('lobby_id', 'unknown')

    video_id, song_cover, song_name, song_artist = "", "", "", ""
    error_message = ""

    if mode == 'spotify' or mode == 'playlist':
        song_data = get_random_video_from_playlist(detail)
        
        if song_data and 'error' not in song_data:
            video_id = song_data['video_id']
            song_cover = song_data['cover_art']
            song_name = song_data['name']
            song_artist = song_data['artist']
        else:
            error_message = song_data['error'] if song_data else "Video not found."

    context = {
        'mode': mode, 'rounds': rounds, 'detail': detail, 'lobby_id': lobby_id,
        'video_id': video_id, 'song_cover': song_cover,
        'song_name': song_name, 'song_artist': song_artist,
        'error_message': error_message,
    }
    return render(request, 'lobby/game.html', context)

@login_required
def results(request):
    return render(request, 'lobby/results.html')