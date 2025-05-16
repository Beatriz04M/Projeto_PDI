from django.contrib import admin
from .models import Livro, Generos, Editora, Idioma, PalavraChave, Avaliacao

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'ano_publicacao')
    search_fields = ('titulo', 'autor')
    list_filter = ('ano_publicacao', 'editora', 'idioma')
    filter_horizontal = ('generos','palavra_chave')  

admin.site.register(Generos)
admin.site.register(Editora)
admin.site.register(Idioma)
admin.site.register(PalavraChave)
admin.site.register(Avaliacao)


