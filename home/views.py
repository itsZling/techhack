from django.shortcuts import render, redirect
import random
import string

def index(request):
    return render(request, 'home/index.html')

def create_lobby(request):
    # Generate a random 6-character code (uppercase letters and digits)
    lobby_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Redirect the user to the lobby URL using the generated code
    return redirect('lobby.index', lobby_id=lobby_code)

def join_lobby(request):
    if request.method == 'POST':
        # Get the code the user typed into the textbox
        lobby_code = request.POST.get('lobby_code')
        if lobby_code:
            # Remove any spaces and redirect them to that room
            clean_code = lobby_code.strip().upper()
            return redirect('lobby.index', lobby_id=clean_code)
            
    # If they somehow got here without submitting the form, send them back to home
    return redirect('home.index')