from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.game, name='game.index'),
    path('results/', views.results, name='results'),
    path('<str:lobby_id>/', views.index, name='lobby.index'), 
]