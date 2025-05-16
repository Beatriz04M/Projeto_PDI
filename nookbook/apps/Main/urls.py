from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registar_leitura/', views.registar_leitura, name='registar_leitura'),
    path('livro/<int:pk>/', views.detalhes_livro, name='detalhes_livro')
]
