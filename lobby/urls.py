from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='lobby.index'),
    path('game/', views.game, name='game.index')
    path('<str:room_code>/', views.lobby_view, name='lobby'),
]
