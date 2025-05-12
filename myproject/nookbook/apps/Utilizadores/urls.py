from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='pagina_login'),
    path('logout/confirmar/', views.confirmar_logout, name='confirmar_logout'),
    path('logout/', views.fazer_logout, name='logout'),  
    path('registo/', views.registo_view, name='pagina_registo')
]

