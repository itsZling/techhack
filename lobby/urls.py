from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='lobby.index'),
    path('game/', views.game, name='game.index')
]
