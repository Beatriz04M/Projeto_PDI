from django.db.models.signals import post_save
from django.dispatch import receiver
from nookbook.apps.Utilizadores.models import Utilizador
from nookbook.apps.Biblioteca.models import Estante

@receiver(post_save, sender=Utilizador)
def criar_estantes_default(sender, instance, created, **kwargs):
    if created:
        estantes = ['Lido', 'A Ler', 'Quero Ler', 'Abandonei']
        for nome in estantes:
            Estante.objects.get_or_create(utilizador=instance, nome=nome)
