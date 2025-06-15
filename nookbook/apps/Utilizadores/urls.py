from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='pagina_login'),
    path('logout/confirmar/', views.confirmar_logout, name='confirmar_logout'),
    path('logout/', views.fazer_logout, name='logout'),  
    path('registo/', views.registo_view, name='pagina_registo'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('participar-desafio/<int:desafio_id>/', views.participar_desafio, name='participar_desafio'),
    path('editar-perfil/', views.editar_perfil_view, name='editar_perfil'),
]

