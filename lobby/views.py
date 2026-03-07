from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'lobby/index.html')

def game(request):
    return render(request, 'lobby/game.html')

def results(request):
    return render(request, 'lobby/results.html')