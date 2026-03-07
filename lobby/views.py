from django.shortcuts import render

# Create your views here.
def index(request, lobby_id):
    return render(request, 'lobby/index.html', {'lobby_id': lobby_id})

def game(request):
    return render(request, 'lobby/game.html')

def results(request):
    return render(request, 'lobby/results.html')
<<<<<<< HEAD

def lobby_view(request, room_code):
    return render(request, 'lobby/lobby.html', {'room_code': room_code})
=======
>>>>>>> c3deeb0c90910faabe1bbe5d4f42d2aa80396535
