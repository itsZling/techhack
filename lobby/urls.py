from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.game, name='game.index'),
    path('results/', views.results, name='results'),
    
    # 2. Put the wildcard path LAST! 
    # This way, it only catches actual random lobby codes.
    path('<str:lobby_id>/', views.index, name='lobby.index'), 
]