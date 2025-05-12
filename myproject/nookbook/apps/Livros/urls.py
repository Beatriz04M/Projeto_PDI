from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('pesquisar/', views.pesquisar_livros, name='pesquisar_livros'),
    path('livro/<int:livro_id>/', views.detalhe_livro, name='detalhe_livro'),
    path('livro/api/<str:google_id>/', views.detalhe_livro_api, name='detalhe_livro_api'),
    path('livro/<int:livro_id>/comentar/', views.adicionar_comentario, name='adicionar_comentario'),
    path('livro/api/<str:google_id>/comentar/', views.comentar_api, name='comentar_api'),
    path('livro/adicionar/', views.adicionar_livro, name='adicionar_livro'),
    path("livro/api/<str:google_id>/guardar/", views.guardar_livro_api, name="guardar_livro_api"),
    path('livro/adicionar_estante_bd/', views.criar_estante_e_adicionar_bd, name='criar_estante_e_adicionar_bd'),
    path('livro/api/<str:google_id>/adicionar_estante/', views.criar_estante_e_adicionar_api, name='criar_estante_e_adicionar_api'),
]
