from .api import buscar_livros, extrair_dados_livros  
import re
from .models import Livro
from googletrans import Translator
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from nookbook.apps.Livros.models import Livro, Avaliacao, Generos, PalavraChave, AvaliacaoAPI
from nookbook.apps.Biblioteca.models import Biblioteca, Estante
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from django.db import IntegrityError
import random
import requests
from django.core.files.base import ContentFile
from .api import buscar_livros, extrair_dados_livros
from nookbook.apps.Livros.models import Livro
from django.shortcuts import render
import random

def pagina_inicial(request):
    livros_validos = []
    vistos = set()
    tentativas = 0
    max_tentativas = 10
    query_generica = "a"

    while len(livros_validos) < 13 and tentativas < max_tentativas:
        start_index = random.choice(range(0, 500, 10))
        resultado = buscar_livros(valor=query_generica, max_results=40, start_index=start_index)

        if resultado:
            novos_livros = extrair_dados_livros(resultado, traduzir=False)

            for livro in novos_livros:
                id_livro = livro.get('google_id')
                capa = livro.get('capa')

                if id_livro and capa and id_livro not in vistos:
                    livros_validos.append(livro)
                    vistos.add(id_livro)
                    if len(livros_validos) == 13:
                        break
        tentativas += 1

    # Se não conseguir 13, preencher com livros da base de dados
    if len(livros_validos) < 13:
        faltam = 13 - len(livros_validos)
        livros_bd = list(Livro.objects.exclude(google_id__in=vistos))
        random.shuffle(livros_bd)
        for livro_obj in livros_bd[:faltam]:
            livros_validos.append({
                'google_id': '',  # pode ser vazio se for local
                'titulo': livro_obj.titulo,
                'capa': livro_obj.capa.url if livro_obj.capa else '/static/imagens/capa_default.png'
            })

    livros = livros_validos[:13]
    livro_destaque = livros[0] if livros else None
    livros_flutuantes = livros[1:] if len(livros) > 1 else []

    livros_esquerda = livros_flutuantes[:6]
    livros_direita = livros_flutuantes[6:]

    todos_livros = list(Livro.objects.all())
    livros_recomendados = random.sample(todos_livros, 6) if len(todos_livros) >= 6 else todos_livros

    return render(request, "index.html", {
        "livro_destaque": livro_destaque,
        "livros_esquerda": livros_esquerda,
        "livros_direita": livros_direita,
        "livros_recomendados": livros_recomendados
    })


def pesquisar_livros(request):
    query = request.GET.get('q', '').strip()
    livros_api = []
    livros_bd = []

    def identificar_filtro(texto):
        isbn_limpo = texto.replace('-', '').replace(' ', '')
        if re.fullmatch(r'\d{10}|\d{13}', isbn_limpo):
            return 'isbn'
        elif ' ' not in texto and texto.isalpha():
            return 'autor'
        elif len(texto.split()) >= 3:
            return 'titulo'
        else:
            return 'palavra'

    if query:
        # --- Pesquisa na Base de Dados ---
        livros_bd = Livro.objects.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(sinopse__icontains=query)
        ).distinct()

        # --- Pesquisa na API ---
        filtro = identificar_filtro(query)
        dados_api = buscar_livros(filtro=filtro, valor=query)
        if dados_api:
            livros_api_raw = extrair_dados_livros(dados_api, traduzir=True)

            # ---- Eliminar livros da API que já existem na BD ----
            titulos_bd = set(livro.titulo.lower() for livro in livros_bd)

            livros_api = []
            for livro in livros_api_raw:
                titulo = livro.get('titulo', '').lower()
                if titulo and titulo not in titulos_bd:
                    livros_api.append(livro)

    return render(request, "resultados.html", {
        "query": query,
        "livros_bd": livros_bd,
        "livros_api": livros_api
    })

def importar_dados_livro_api(google_id):
    resultado = buscar_livros(filtro="id", valor=google_id)
    livros = extrair_dados_livros(resultado, traduzir=True)
    return livros[0] if livros else None

def validar_nota(valor):
    try:
        nota = round(float(valor), 1)
        if 1.0 <= nota <= 5.0:
            return nota
    except:
        pass
    return None

def adicionar_livro_a_estante(utilizador, livro, estante_id):
    if estante_id:
        estante = get_object_or_404(Estante, id=estante_id, utilizador=utilizador)
        if Biblioteca.objects.filter(utilizador=utilizador, livro=livro, estante_customizada=estante).exists():
            return False, f"📚 Este livro já está na estante '{estante.nome}'."
        Biblioteca.objects.create(utilizador=utilizador, livro=livro, estante_customizada=estante)
        return True, f"✅ Livro guardado na estante '{estante.nome}'!"
    return True, "✅ Livro guardado na tua biblioteca."

def limpar_texto_descricao(texto):
    # Remove qualquer conteúdo que possa ser indesejado, como tags HTML
    texto_limpo = re.sub(r"<[^>]*>", "", texto)  # Remove todas as tags HTML
    return texto_limpo.strip()

def detalhe_livro_api(request, google_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{google_id}"
    tradutor = Translator()

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return render(request, 'livros/erro.html', {"mensagem": "Não foi possível obter os dados do livro."})

    info = data.get("volumeInfo", {})

    titulo = info.get("title", "Sem título")
    autores = ", ".join(info.get("authors", ["Autor desconhecido"]))
    descricao = limpar_texto_descricao(info.get("description", "Sem descrição disponível"))
    capa = info.get("imageLinks", {}).get("thumbnail", "/static/imagens/capa_default.png")
    nota = info.get("averageRating", None)
    categorias_api = info.get("categories", [])

    try:
        descricao = tradutor.translate(descricao, dest="pt").text
    except:
        pass

    mapa_generos = {
        "Fiction": "Ficção", "Romance": "Romance", "Mystery": "Suspense",
        "Thriller": "Suspense", "Horror": "Terror", "Fantasy": "Fantasia",
        "Biography": "Biografia", "History": "História", "Science": "Ciência",
        "Classic": "Clássico", "Adventure": "Aventura", "Drama": "Drama"
    }
    categorias_traduzidas = [mapa_generos.get(cat, cat) for cat in categorias_api]

    livro = {
       "google_id": google_id,
       "titulo": titulo,
       "autor": autores,
       "descricao": descricao,
       "capa": capa,
       "nota": nota if nota is not None else "N/A",
       "categorias": categorias_traduzidas,
    }

    estantes = []
    if request.user.is_authenticated:
        estantes = Estante.objects.filter(utilizador=request.user)

    return render(request, "detalhe_livro.html", {
        "livro": livro,
        "avaliacoes": [],
        "estantes": estantes  
    })

def detalhe_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    avaliacoes = livro.avaliacoes.select_related('utilizador').all()

    estantes = []
    if request.user.is_authenticated:
        estantes = Estante.objects.filter(utilizador=request.user)

    return render(request, "detalhe_livro.html", {
        "livro": livro,
        "avaliacoes": avaliacoes, 
        "estantes": estantes  
    })

@login_required
def adicionar_comentario(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if request.method == 'POST':
        comentario_texto = request.POST.get('comentario', '').strip()
        nota = request.POST.get('avaliacao')

        if comentario_texto and nota:
            try:
                nota_decimal = round(float(nota), 1)
                if not (1.0 <= nota_decimal <= 5.0):
                    raise ValueError("Fora do intervalo permitido.")

                avaliacao_existente = Avaliacao.objects.filter(utilizador=request.user, livro=livro).first()

                if avaliacao_existente:
                    messages.error(request, "Já adicionaste uma avaliação para este livro.")
                else:
                    Avaliacao.objects.create(
                        utilizador=request.user,
                        livro=livro,
                        avaliacao=nota_decimal,
                        comentario=comentario_texto
                    )
                    messages.success(request, "Comentário adicionado com sucesso! 🎉")
            except ValueError:
                messages.error(request, "A nota deve ser um número entre 1.0 e 5.0.")
        else:
            messages.error(request, "Preenche todos os campos corretamente.")

    return redirect('detalhe_livro', livro_id=livro.id)

@login_required
def comentar_api(request, google_id):
    if request.method == "POST":
        texto = request.POST.get("comentario", "").strip()
        nota = request.POST.get("avaliacao")

        if texto and nota:
            nota = round(float(nota), 1)
            existe = AvaliacaoAPI.objects.filter(utilizador=request.user, google_id=google_id).exists()

            if existe:
                messages.error(request, "Já comentaste este livro.")
            else:
                AvaliacaoAPI.objects.create(
                    utilizador=request.user,
                    google_id=google_id,
                    comentario=texto,
                    avaliacao=nota
                )
                messages.success(request, "Comentário adicionado com sucesso! 🎉")
        else:
            messages.error(request, "Preenche todos os campos corretamente.")

        return redirect("detalhe_livro_api", google_id=google_id)

@login_required
def adicionar_livro(request):
    if request.method == 'POST':
        dados = {
            'titulo': request.POST.get('titulo'),
            'autor': request.POST.get('autores'),
            'sinopse': request.POST.get('sinopse'),
            'num_pag': request.POST.get('num_pag'),
            'ano_publicacao': request.POST.get('ano_publicacao'),
            'isbn': request.POST.get('isbn') or None,
            'capa': request.FILES.get('capa')
        }
        estante_id = request.POST.get('estante_id')

        if not all([dados['titulo'], dados['autor'], dados['sinopse'], dados['num_pag']]):
            messages.error(request, "Preenche todos os campos obrigatórios.")
            return redirect('adicionar_livro')

        if dados['isbn'] and Livro.objects.filter(isbn=dados['isbn']).exists():
            messages.error(request, "Já existe um livro com esse ISBN.")
            return redirect('adicionar_livro')

        try:
            livro = Livro.objects.create(
                titulo=dados['titulo'],
                autor=dados['autor'],
                sinopse=dados['sinopse'],
                num_pag=int(dados['num_pag']),
                ano_publicacao=int(dados['ano_publicacao']) if dados['ano_publicacao'] else None,
                isbn=dados['isbn'],
                capa=dados['capa']
            )

            for genero_nome in request.POST.getlist('generos[]'):
                genero, _ = Generos.objects.get_or_create(nome=genero_nome)
                livro.generos.add(genero)

            for palavra in request.POST.getlist('palavras_chave'):
                tag, _ = PalavraChave.objects.get_or_create(nome=palavra)
                livro.palavra_chave.add(tag)

            sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
            messages.success(request, msg if sucesso else "Livro adicionado mas já existia na estante.")

            return redirect('pagina_biblioteca')

        except IntegrityError:
            messages.error(request, '❌ Erro ao guardar o livro. Verifica os dados e tenta novamente.')
            return redirect('adicionar_livro')

    estantes = Estante.objects.filter(utilizador=request.user)
    return render(request, 'adicionar_livro.html', {
        'now': date.today(),
        'estantes': estantes
    })

@login_required
def guardar_livro_api(request, google_id):
    dados = importar_dados_livro_api(google_id)
    if not dados:
        messages.error(request, "❌ Não foi possível importar o livro.")
        return redirect('detalhe_livro_api', google_id=google_id)

    livro = Livro.objects.filter(google_id=google_id).first()
    estante_id = request.GET.get('estante_id') or request.POST.get('estante_id')

    if livro:
        sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
        messages.success(request, msg if sucesso else "Livro já estava na estante.")
        return redirect('detalhe_livro_api', google_id=google_id)

    livro = Livro.objects.create(
        titulo=dados['titulo'],
        autor=dados['autor'],
        sinopse=dados.get('descricao', 'Sem sinopse.'),
        num_pag=dados.get('num_paginas') or 100,
        ano_publicacao=dados.get('ano'),
        google_id=google_id
    )

    if dados.get('capa'):
        try:
            r = requests.get(dados['capa'])
            if r.status_code == 200:
                livro.capa.save(f"{livro.titulo}.jpg", ContentFile(r.content), save=True)
        except:
            pass

    sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
    messages.success(request, msg)
    return redirect('detalhe_livro_api', google_id=google_id)

@login_required
def criar_estante_e_adicionar_api(request, google_id):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cor = request.POST.get("cor") or "#f5f5f5"  # ← NOVO

        if not nome:
            messages.error(request, "❌ Nome da estante em falta.")
            return redirect('detalhe_livro_api', google_id=google_id)

        if Estante.objects.filter(utilizador=request.user, nome__iexact=nome).exists():
            messages.error(request, "⚠️ Já tens uma estante com esse nome.")
            return redirect('detalhe_livro_api', google_id=google_id)

        estante = Estante.objects.create(utilizador=request.user, nome=nome, cor=cor)  # ← ALTERADO
        return redirect(f"/livro/api/{google_id}/guardar/?estante_id={estante.id}")

    messages.error(request, "❌ Não foi possível criar a estante.")
    return redirect('detalhe_livro_api', google_id=google_id)

@login_required
def criar_estante_e_adicionar_bd(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cor = request.POST.get("cor") or "#f5f5f5"  # ← NOVO
        livro_id = request.POST.get("livro_id")

        if not nome or not livro_id:
            messages.error(request, "❌ Nome da estante ou ID do livro em falta.")
            return redirect('detalhe_livro', livro_id=livro_id)

        if Estante.objects.filter(utilizador=request.user, nome__iexact=nome).exists():
            messages.error(request, "⚠️ Já tens uma estante com esse nome.")
            return redirect('detalhe_livro', livro_id=livro_id)

        estante = Estante.objects.create(utilizador=request.user, nome=nome, cor=cor)  # ← ALTERADO
        return redirect(f"/livro/{livro_id}/?estante_id={estante.id}")

    messages.error(request, "❌ Não foi possível criar a estante.")
    return redirect('pagina_biblioteca')

