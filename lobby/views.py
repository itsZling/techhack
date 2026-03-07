from django.shortcuts import render

# Create your views here.
def index(request, lobby_id):
    return render(request, 'lobby/index.html', {'lobby_id': lobby_id})

def game(request):
    # request.GET grabs the data from the URL (e.g. ?mode=genre&rounds=15)
    # The second argument is a fallback default if the data is missing
    context = {
        'mode': request.GET.get('mode', 'genre'),
        'rounds': request.GET.get('rounds', '5'),
        'detail': request.GET.get('detail', 'none'),
        'lobby_id': request.GET.get('lobby_id', 'unknown'),
    }
    
    return render(request, 'lobby/game.html', context)

def results(request):
    return render(request, 'lobby/results.html')
