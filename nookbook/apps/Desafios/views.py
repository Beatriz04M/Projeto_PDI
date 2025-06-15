from django.shortcuts import render, redirect
from nookbook.apps.Biblioteca.models import Biblioteca, Estante
import random
from django.contrib.auth.decorators import login_required
from nookbook.apps.Desafios.forms import DesafioLeituraForm


@login_required
def roda_da_sorte(request):
    user = request.user
    estante = Estante.objects.filter(utilizador=user, nome__iexact="Quero Ler").first()

    livros = []
    if estante:
        entradas = list(Biblioteca.objects.filter(utilizador=user, estante_customizada=estante))
        random.shuffle(entradas)  
        entradas = entradas[:8]   
        livros = [{
            "id": e.livro.id,
            "titulo": e.livro.titulo,
            "autor": e.livro.autor
        } for e in entradas]

    return render(request, 'roda_sorte.html', {
        'livros': livros,
    })

@login_required
def criar_desafio(request):
    if request.method == 'POST':
        form = DesafioLeituraForm(request.POST)
        if form.is_valid():
            desafio = form.save()
            return redirect('perfil')
    else:
        form = DesafioLeituraForm()

    return render(request, 'criar_desafio.html', {'form': form})
