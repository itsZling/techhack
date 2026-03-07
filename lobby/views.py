from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'lobby/index.html')

def game(request):
    return render(request, 'lobby/game.html')

def results(request):
    return render(request, 'lobby/results.html')

def lobby_view(request, room_code):
    return render(request, 'lobby/lobby.html', {'room_code': room_code})