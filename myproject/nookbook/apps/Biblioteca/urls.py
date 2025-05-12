from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    # Página principal da biblioteca
    path('biblioteca/', views.pagina_biblioteca, name='pagina_biblioteca'),

    # Criação de estante (usada diretamente na biblioteca)
    path('biblioteca/criar_estante/', views.criar_estante, name='criar_estante'),

    # Adicionar livro a uma estante
    path('biblioteca/adicionar_livro/', views.adicionar_livro_estante, name='adicionar_livro_estante'),

    # Remover livro de estante
    path('biblioteca/remover_livro/', views.remover_livro_estante, name='remover_livro_estante'),

    # Editar nome da estante
    path('biblioteca/editar_estante/<int:estante_id>/', views.editar_estante, name='editar_estante'),

    # Eliminar estante
    path('biblioteca/eliminar_estante/<int:estante_id>/', views.eliminar_estante, name='eliminar_estante'),

    # Mudar a cor da estante
    path('biblioteca/estante/<int:estante_id>/mudar_cor/', views.mudar_cor_estante, name='mudar_cor_estante'),
]
