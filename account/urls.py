from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='account.signup'),
    path('login/', views.login, name='account.login'),
    path('logout', views.logout, name='account.logout'),
]