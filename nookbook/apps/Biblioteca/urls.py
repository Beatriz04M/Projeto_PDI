from django.urls import path
from . import views


urlpatterns = [
    path('biblioteca/', views.pagina_biblioteca, name='pagina_biblioteca'),
    path('biblioteca/criar_estante/', views.criar_estante, name='criar_estante'),
    path('biblioteca/adicionar_livro/', views.adicionar_livro_estante, name='adicionar_livro_estante'),
    path('biblioteca/remover_livro/', views.remover_livro_estante, name='remover_livro_estante'),
    path('biblioteca/editar_estante/<int:estante_id>/', views.editar_estante, name='editar_estante'),
    path('biblioteca/eliminar_estante/<int:estante_id>/', views.eliminar_estante, name='eliminar_estante'),
    path('biblioteca/estante/<int:estante_id>/mudar_cor/', views.mudar_cor_estante, name='mudar_cor_estante'),
    path('biblioteca/estante/<int:estante_id>/', views.pagina_estante, name='pagina_estante'),
    path('biblioteca/estante/<int:estante_id>/adicionar/', views.adicionar_livro_aestante, name='adicionar_livro_aestante'),
    path('estante/remover/', views.remover_livro_estante, name='remover_livro_estante'),
]
