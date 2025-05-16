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
import random
import requests
from django.core.files.base import ContentFile
from .api import buscar_livros, extrair_dados_livros
from nookbook.apps.Livros.models import Livro
from django.shortcuts import render
import random
from .models import AvaliacaoAPI
from decimal import Decimal
from django.db.models import Avg


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
    
    # Adicionar à biblioteca sem estante personalizada
    if Biblioteca.objects.filter(utilizador=utilizador, livro=livro, estante_customizada__isnull=True).exists():
        return False, "📚 Este livro já está guardado na tua biblioteca."
    
    Biblioteca.objects.create(utilizador=utilizador, livro=livro)
    return True, "✅ Livro guardado na tua biblioteca."


def limpar_texto_descricao(texto):
    texto_limpo = re.sub(r"<[^>]*>", "", texto)  
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
    descricao = info.get("description", "Sem descrição disponível")
    capa = info.get("imageLinks", {}).get("thumbnail", "/static/imagens/capa_default.png")
    nota = info.get("averageRating", None)
    categorias_api = info.get("categories", [])

    # Traduz a descrição
    try:
        descricao = tradutor.translate(descricao, dest="pt").text
    except:
        pass

    # Traduz categorias conhecidas
    mapa_generos = {
        "Fiction": "Ficção", "Romance": "Romance", "Mystery": "Suspense",
        "Thriller": "Suspense", "Horror": "Terror", "Fantasy": "Fantasia",
        "Biography": "Biografia", "History": "História", "Science": "Ciência",
        "Classic": "Clássico", "Adventure": "Aventura", "Drama": "Drama"
    }
    categorias_traduzidas = [mapa_generos.get(cat, cat) for cat in categorias_api]

    # Estrutura do livro como dicionário
    livro = {
        "google_id": google_id,
        "titulo": titulo,
        "autor": autores,
        "descricao": descricao,
        "capa": capa,
        "nota": nota if nota is not None else "N/A",
        "categorias": categorias_traduzidas,
    }

    # Estantes do utilizador autenticado
    estantes = []
    if request.user.is_authenticated:
        estantes = Estante.objects.filter(utilizador=request.user)

    # Comentários e média para livros da API
    avaliacoes_api = AvaliacaoAPI.objects.filter(google_id=google_id).order_by("-id")
    media_api = avaliacoes_api.aggregate(media=Avg('avaliacao'))['media'] or 0

    return render(request, "detalhe_livro.html", {
        "livro": livro,
        "avaliacoes_api": avaliacoes_api,
        "media_api": media_api,
        "avaliacoes_bd": None,
        "estantes": estantes
    })

def detalhe_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    avaliacoes_bd = livro.avaliacoes.select_related('utilizador').all()

    estantes = []
    if request.user.is_authenticated:
        estantes = Estante.objects.filter(utilizador=request.user)

    return render(request, "detalhe_livro.html", {
        "livro": livro,
        "avaliacoes_api": None,
        "avaliacoes_bd": avaliacoes_bd,
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
            try:
                nota_decimal = Decimal(nota)
            except:
                messages.error(request, "Valor de avaliação inválido.")
                return redirect("detalhe_livro_api", google_id=google_id)

            existe = AvaliacaoAPI.objects.filter(utilizador=request.user, google_id=google_id).exists()
            if existe:
                messages.error(request, "Já comentaste este livro.")
            else:
                AvaliacaoAPI.objects.create(
                    utilizador=request.user,
                    google_id=google_id,
                    comentario=texto,
                    avaliacao=nota_decimal
                )
                messages.success(request, "Comentário adicionado com sucesso! 🎉")
        else:
            messages.error(request, "Preenche todos os campos corretamente.")

        return redirect("detalhe_livro_api", google_id=google_id)
     
@login_required
def adicionar_livro(request):
    if request.method == 'POST':
        autor_formatado = request.POST.get('autor', '').strip()

        dados = {
            'titulo': request.POST.get('titulo', '').strip(),
            'autor': autor_formatado,
            'sinopse': request.POST.get('sinopse', '').strip(),
            'num_pag': request.POST.get('num_pag'),
            'ano_publicacao': request.POST.get('ano_publicacao'),
            'isbn': request.POST.get('isbn') or None,
            'capa': request.FILES.get('capa')
        }

        # Validação dos campos obrigatórios
        if not dados['titulo'] or not dados['autor'] or not dados['sinopse'] or not dados['num_pag']:
            messages.error(request, "Preenche todos os campos obrigatórios.")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

        # Validar número de páginas
        try:
            dados['num_pag'] = int(dados['num_pag'])
            if dados['num_pag'] <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Número de páginas inválido.")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

        # Validar ano de publicação
        try:
            dados['ano_publicacao'] = int(dados['ano_publicacao']) if dados['ano_publicacao'] else None
        except ValueError:
            messages.error(request, "Ano de publicação inválido.")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

        # Verificar ISBN duplicado
        if dados['isbn'] and Livro.objects.filter(isbn=dados['isbn']).exists():
            messages.error(request, "Já existe um livro com esse ISBN.")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

        try:
            livro = Livro.objects.create(
                titulo=dados['titulo'],
                autor=dados['autor'],
                sinopse=dados['sinopse'],
                num_pag=dados['num_pag'],
                ano_publicacao=dados['ano_publicacao'],
                isbn=dados['isbn'],
                capa=dados['capa']
            )

            for palavra in request.POST.getlist('palavras_chave'):
                if palavra.strip():
                    tag, _ = PalavraChave.objects.get_or_create(nome=palavra.strip())
                    livro.palavra_chave.add(tag)

            messages.success(request, "📚 Livro adicionado com sucesso.")
            return redirect('inicio')

        except Exception as e:
            print("❌ Erro inesperado ao guardar livro:", e)
            messages.error(request, f"Erro inesperado: {e}")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

    # GET request
    return render(request, 'adicionar_livro.html', {
        'now': date.today(),
        'form_data': {}
    })


@login_required
def guardar_livro_api(request, google_id):

    dados = importar_dados_livro_api(google_id)
    if not dados:
        messages.error(request, "❌ Não foi possível importar o livro.")
        return redirect('detalhe_livro_api', google_id=google_id)

    livro = Livro.objects.filter(google_id=google_id).first()
    estante_id = request.GET.get('estante_id') or request.POST.get('estante_id')

    # Já existe na base de dados
    if livro:
        sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
        messages.success(request, msg if sucesso else f"📚 {msg}")
        return redirect('detalhe_livro_api', google_id=google_id)

    # Criar novo livro
    livro = Livro.objects.create(
        titulo=dados['titulo'],
        autor=dados['autor'],
        sinopse=dados.get('descricao', 'Sem sinopse.'),
        num_pag=dados.get('num_paginas') or 100,
        ano_publicacao=dados.get('ano'),
        google_id=google_id
    )

    # Guardar imagem da capa (se existir)
    url_capa = dados.get('capa')
    if url_capa:
        try:
            r = requests.get(url_capa)
            if r.status_code == 200:
                nome_arquivo = f"{livro.titulo}.jpg"
                livro.capa.save(nome_arquivo, ContentFile(r.content), save=True)
        except Exception as e:
            print(f"⚠️ Erro ao guardar a capa: {e}")

    # Associar à estante (se aplicável)
    sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
    messages.success(request, msg if sucesso else f"📚 {msg}")

    return redirect('detalhe_livro_api', google_id=google_id)


@login_required
def criar_estante_e_adicionar_api(request, google_id):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cor = request.POST.get("cor") or "#f5f5f5"  

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
        cor = request.POST.get("cor") or "#f5f5f5"  
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
    return redirect('detalhe_livro')

