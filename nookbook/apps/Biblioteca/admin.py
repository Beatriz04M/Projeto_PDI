from django.contrib import admin
from .models import ProgressoLeitura, Estante, Recomendacao, Biblioteca

admin.site.register(ProgressoLeitura)
admin.site.register(Estante)
admin.site.register(Recomendacao)
admin.site.register(Biblioteca)
