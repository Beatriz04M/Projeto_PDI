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
    path('leitura/<int:leitura_id>/', views.leitura_detalhes, name='leitura_detalhes'),
    path('leitura/<int:leitura_id>/anotacoes/', views.adicionar_anotacao, name='adicionar_anotacao'),
    path('leitura/iniciar/<int:livro_id>/', views.iniciar_ou_ver_leitura, name='iniciar_ou_ver_leitura'),
    path('avaliacao/<int:avaliacao_id>/editar/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliacao/<int:avaliacao_id>/remover/', views.remover_avaliacao, name='remover_avaliacao'),
    path('avaliacao_api/<int:avaliacao_id>/editar/', views.editar_avaliacao_api, name='editar_avaliacao_api'),
    path('avaliacao_api/<int:avaliacao_id>/remover/', views.remover_avaliacao_api, name='remover_avaliacao_api'),

]
