from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('', views.index, name='lobby.index'),
    path('game/', views.game, name='game.index')
    path('<str:room_code>/', views.lobby_view, name='lobby'),
=======
    path('<str:lobby_id>/', views.index, name='lobby.index'),
    path('game/', views.game, name='game.index'),
    path('results/', views.results, name='results')
>>>>>>> c3deeb0c90910faabe1bbe5d4f42d2aa80396535
]
