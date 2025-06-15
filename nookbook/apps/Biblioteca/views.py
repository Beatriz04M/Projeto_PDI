from django.shortcuts import render, redirect, get_object_or_404
from .models import Estante, Biblioteca, ProgressoLeitura
from nookbook.apps.Livros.models import Livro, Leitura
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Q
from nookbook.apps.Livros.views import adicionar_livro_a_estante, importar_dados_livro_api

def garantir_estantes_default(utilizador):
    nomes = ['A Ler', 'Quero Ler', 'Lidos', 'Abandonados']
    for nome in nomes:
        Estante.objects.get_or_create(utilizador=utilizador, nome=nome)

@login_required
def pagina_biblioteca(request):
    garantir_estantes_default(request.user)
    estantes = Estante.objects.filter(utilizador=request.user)

    ordem_default = ['A Ler', 'Quero Ler', 'Lidos', 'Abandonados']
    estantes_ordenadas = []

    for nome in ordem_default:
        estante = estantes.filter(nome=nome).first()
        if estante:
            estantes_ordenadas.append(estante)

    estantes_personalizadas = estantes.exclude(nome__in=ordem_default).order_by('nome')
    estantes_ordenadas.extend(estantes_personalizadas)

    estantes_com_livros = []
    for estante in estantes_ordenadas:
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


@login_required
def criar_estante(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        livro_manual = request.POST.get('nome_livro_manual')
        estante_id = request.POST.get('estante_id')
        cor = request.POST.get('cor') or "#f9b4c6"

        if estante_id:
            estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
        else:
            if Estante.objects.filter(utilizador=request.user, nome=nome).exists():
                messages.error(request, 'Já existe uma estante com esse nome!')
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
                messages.success(request, f"Livro '{livro.titulo}' adicionado à estante '{estante.nome}'.")
            else:
                messages.warning(request, f"O livro '{livro.titulo}' já está na tua biblioteca.")

        return redirect('pagina_biblioteca')

@login_required
def adicionar_livro_estante(request):
    if request.method == 'POST':
        estante_id = request.POST.get('estante_id')
        livro_id = request.POST.get('livro_id')

        estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
        livro = get_object_or_404(Livro, id=livro_id)

        ja_existe = Biblioteca.objects.filter(
            utilizador=request.user,
            livro=livro,
            estante_customizada=estante
        ).exists()

        if ja_existe:
            messages.warning(request, f"'{livro.titulo}' já está na estante {estante.nome}.")
        else:
            Biblioteca.objects.create(
                utilizador=request.user,
                livro=livro,
                estante_customizada=estante
            )

            if estante.nome.strip().lower() == "a ler":
                progresso, created = ProgressoLeitura.objects.get_or_create(
                    utilizador=request.user,
                    livro=livro,
                    defaults={'pag_atual': 0}
                )

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
            messages.error(request, "Livro não encontrado nesta estante.")

        return redirect('pagina_estante', estante_id=estante_id)

    return redirect('pagina_biblioteca')

@login_required
def editar_estante(request, estante_id):
    if request.method == 'POST':
        novo_nome = request.POST.get('novo_nome')
        estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)

        if Estante.objects.filter(utilizador=request.user, nome=novo_nome).exclude(id=estante.id).exists():
            messages.error(request, "Já existe uma estante com esse nome.")
        else:
            estante.nome = novo_nome
            estante.save()
    return redirect('pagina_biblioteca')

@login_required
def eliminar_estante(request, estante_id):
    if request.method == 'POST':
        estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
        estante.delete()  
    return redirect('pagina_biblioteca')

@require_POST
@login_required
def mudar_cor_estante(request, estante_id):
    estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)
    nova_cor = request.POST.get('cor')

    if nova_cor == 'remover':
        estante.cor = None  
    else:
        estante.cor = nova_cor

    estante.save()
    return redirect('pagina_biblioteca')

@login_required
def pagina_estante(request, estante_id):
    estante = get_object_or_404(Estante, id=estante_id, utilizador=request.user)

    livros_na_estante = Biblioteca.objects.filter(estante_customizada=estante).select_related('livro')
    livros = [b.livro for b in livros_na_estante]

    leituras = Leitura.objects.filter(utilizador=request.user)
    leituras_dict = {l.livro_id: l.id for l in leituras}

    query = request.GET.get('q')
    resultados = []

    if query:
        resultados = Livro.objects.filter(
            Q(titulo__icontains=query) | Q(autor__icontains=query)
        ).exclude(id__in=[livro.id for livro in livros])[:10] 

    context = {
        'estante': estante,
        'livros': livros,
        'resultados': resultados,
        'leituras_dict': leituras_dict, 
    }
    return render(request, 'estante.html', context)

@login_required
def adicionar_livro_aestante(request, estante_id=None):
    if request.method != 'POST':
        messages.error(request, "Método inválido.")
        return redirect('pagina_biblioteca')

    livro_id = request.POST.get('livro_id')
    if not livro_id:
        messages.error(request, "Nenhum livro selecionado.")
        return redirect('livros_da_estante', estante_id=estante_id) if estante_id else redirect('pagina_biblioteca')

    livro = get_object_or_404(Livro, id=livro_id)
    sucesso, mensagem = adicionar_livro_a_estante(request.user, livro, estante_id)

    if sucesso:
        messages.success(request, mensagem)
    else:
        messages.warning(request, mensagem)

    return redirect('livros_da_estante', estante_id=estante_id) if estante_id else redirect('pagina_biblioteca')

def pesquisar_livros(request):
    query = request.GET.get('q', '').strip()
    estante_id = request.GET.get('estante_id')

    resultados_bd = Livro.objects.filter(
        Q(titulo__icontains=query) | Q(autor__icontains=query)
    )

    resultados_api = []
    if not resultados_bd.exists():
        dados = importar_dados_livro_api(query)
        if dados:
            resultados_api.append(dados)

    context = {
        'query': query,
        'resultados_bd': resultados_bd,
        'resultados_api': resultados_api,
        'estante_id': estante_id,
    }

    return render(request, 'livros/resultado_pesquisa.html', context)