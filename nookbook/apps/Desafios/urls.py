from django.urls import path
from . import views


urlpatterns = [
    path('roda-da-sorte/', views.roda_da_sorte, name='roda_da_sorte'),
    path('criar-desafio/', views.criar_desafio, name='criar_desafio')
]
    

