from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilizador
from django.utils.html import format_html

class UtilizadorAdmin(UserAdmin):
    model = Utilizador
    list_display = ('email', 'username', 'nome', 'idioma', 'foto_perfil_miniatura', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'idioma')
    search_fields = ('email', 'username', 'nome')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'nome', 'password')}),
        ('Informações Pessoais', {'fields': ('biografia', 'foto_perfil', 'data_nascimento', 'pais', 'idioma', 'generos_fav')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nome', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    def foto_perfil_miniatura(self, obj):
        if obj.foto_perfil:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />', obj.foto_perfil.url)
        return "(Sem foto)"
    
    foto_perfil_miniatura.short_description = 'Foto'

admin.site.register(Utilizador, UtilizadorAdmin)
