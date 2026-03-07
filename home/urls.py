from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),

    path('create-lobby/', views.create_lobby, name='home.create_lobby'),
    path('join-lobby/', views.join_lobby, name='home.join_lobby'),
]