from django.shortcuts import render, redirect, get_object_or_404
from .models import Estante, Biblioteca
from nookbook.apps.Livros.models import Livro
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


@login_required
def pagina_biblioteca(request):
    garantir_estantes_default(request.user)
    estantes = Estante.objects.filter(utilizador=request.user).order_by('nome')  

    estantes_com_livros = []
    for estante in estantes:
        livros = Biblioteca.objects.filter(estante_customizada=estante).select_related('livro')
        estantes_com_livros.append((estante, livros))
        estante.cor = estante.cor or '#f9b4c6'

    livros_disponiveis = Livro.objects.exclude(
        id__in=Biblioteca.objects.filter(utilizador=request.user).values_list('livro_id', flat=True)
    )

    return render(request, 'biblioteca.html', {
        'estantes_com_livros': estantes_com_livros,
        'livros_disponiveis': livros_disponiveis
    })


def biblioteca_view(request):
    estantes_default = ['A ler', 'Quero Ler', 'Lidos', 'Abandonados']
    for nome in estantes_default:
        Estante.objects.get_or_create(utilizador=request.user, nome=nome)

    estantes = Estante.objects.filter(utilizador=request.user)
    return render(request, 'biblioteca.html', {'estantes': estantes})

def biblioteca_view(request):
    if request.method == 'POST':
        nova = request.POST.get('nova_estante')
        if nova:
            Estante.objects.get_or_create(utilizador=request.user, nome=nova)

    estantes_default = ['A ler', 'Quero Ler', 'Lidos', 'Abandonados']
    for nome in estantes_default:
        Estante.objects.get_or_create(utilizador=request.user, nome=nome)

    estantes = Estante.objects.filter(utilizador=request.user)
    return render(request, 'biblioteca.html', {'estantes': estantes})

def garantir_estantes_default(utilizador):
    nomes = ['A ler', 'Quero Ler', 'Lidos', 'Abandonados']
    for nome in nomes:
        Estante.objects.get_or_create(utilizador=utilizador, nome=nome)

@login_required
def criar_estante(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        livro_manual = request.POST.get('nome_livro_manual')
        estante_id = request.POST.get('estante_id')
        cor = request.POST.get('cor') or "#f5f5f5"

        if estante_id:
            estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
        else:
            if Estante.objects.filter(utilizador=request.user, nome=nome).exists():
                messages.error(request, '❌ Já existe uma estante com esse nome.')
                return redirect('pagina_biblioteca')
            estante = Estante.objects.create(utilizador=request.user, nome=nome, cor=cor)

        if livro_manual:
            from nookbook.apps.Livros.models import Livro
            try:
                livro = Livro.objects.get(titulo__iexact=livro_manual.strip())
            except Livro.DoesNotExist:
                return redirect(f"{reverse('pesquisar_api_por_titulo')}?titulo={livro_manual}&estante_id={estante.id}")

            if not Biblioteca.objects.filter(utilizador=request.user, livro=livro).exists():
                Biblioteca.objects.create(utilizador=request.user, livro=livro, estante_customizada=estante)
                messages.success(request, f"📚 Livro '{livro.titulo}' adicionado à estante '{estante.nome}'.")
            else:
                messages.warning(request, f"⚠️ O livro '{livro.titulo}' já está na tua biblioteca.")

        return redirect('pagina_biblioteca')

@login_required
def adicionar_livro_estante(request):
    if request.method == 'POST':
        estante_id = request.POST.get('estante_id')
        livro_id = request.POST.get('livro_id')

        estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
        livro = get_object_or_404(Livro, id=livro_id)

        if Biblioteca.objects.filter(utilizador=request.user, livro=livro).exists():
            messages.warning(request, 'Esse livro já está na biblioteca.')
        else:
            Biblioteca.objects.create(utilizador=request.user, livro=livro, estante_customizada=estante)
            messages.success(request, f"'{livro.titulo}' adicionado à estante {estante.nome}.")

    return redirect('pagina_biblioteca')

@login_required
def remover_livro_estante(request):
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        estante_id = request.POST.get('estante_id')

        try:
            entrada = Biblioteca.objects.get(
                utilizador=request.user,
                livro_id=livro_id,
                estante_customizada_id=estante_id
            )
            entrada.delete()
        except Biblioteca.DoesNotExist:
            messages.error(request, "❌ Livro não encontrado nesta estante.")

    return redirect('pagina_biblioteca')

@login_required
def editar_estante(request, estante_id):
    if request.method == 'POST':
        novo_nome = request.POST.get('novo_nome')
        estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)

        if Estante.objects.filter(utilizador=request.user, nome=novo_nome).exclude(id=estante.id).exists():
            messages.error(request, "❌ Já existe uma estante com esse nome.")
        else:
            estante.nome = novo_nome
            estante.save()
    return redirect('pagina_biblioteca')

@login_required
def eliminar_estante(request, estante_id):
    if request.method == 'POST':
        estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
        estante.delete()  # ← Remove da base de dados
    return redirect('pagina_biblioteca')

@require_POST
@login_required
def mudar_cor_estante(request, estante_id):
    estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
    nova_cor = request.POST.get('cor')

    if nova_cor == 'remover':
        estante.cor = None  # Remove a cor → usará cor padrão no template
    else:
        estante.cor = nova_cor

    estante.save()
    return redirect('pagina_biblioteca')

