from .api import buscar_livros, extrair_dados_livros  
import re, random, requests, bleach
from googletrans import Translator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Livro, Avaliacao, PalavraChave, AvaliacaoAPI, Leitura
from nookbook.apps.Biblioteca.models import Biblioteca, Estante, LeituraDiaria, ProgressoLeitura
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from datetime import date
from django.core.files.base import ContentFile
from decimal import Decimal

# Página Inicial do site
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

    if len(livros_validos) < 13:
        faltam = 13 - len(livros_validos)
        livros_bd = list(Livro.objects.exclude(google_id__in=vistos))
        random.shuffle(livros_bd)
        for livro_obj in livros_bd[:faltam]:
            livros_validos.append({
                'google_id': '',  
                'titulo': livro_obj.titulo,
                'capa': livro_obj.capa.url if livro_obj.capa else '/static/imagens/capa_default.png'
            })

    livros = livros_validos[:13]
    livro_destaque = livros[0] if livros else None
    livros_flutuantes = livros[1:] if len(livros) > 1 else []

    livros_esquerda = livros_flutuantes[:6]
    livros_direita = livros_flutuantes[6:]

    livros_recomendados_qs = Livro.objects.annotate(
        media_avaliacoes=Avg('avaliacoes__avaliacao')
    )
    livros_recomendados = random.sample(list(livros_recomendados_qs), 6) if livros_recomendados_qs.count() >= 6 else list(livros_recomendados_qs)


    return render(request, "index.html", {
        "livro_destaque": livro_destaque,
        "livros_esquerda": livros_esquerda,
        "livros_direita": livros_direita,
        "livros_recomendados": livros_recomendados
    })

#Secção de pesquisa de livros
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
        livros_bd = Livro.objects.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(sinopse__icontains=query)
        ).annotate(
            media_avaliacoes=Avg('avaliacoes__avaliacao')
        ).distinct()

        filtro = identificar_filtro(query)
        dados_api = buscar_livros(filtro=filtro, valor=query)
        if dados_api:
            livros_api_raw = extrair_dados_livros(dados_api, traduzir=True)

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

        nome = estante.nome.strip().lower()
        estado_leitura = None

        if 'a ler' in nome:
            estado_leitura = 'a_ler'
        elif 'lido' in nome:
            estado_leitura = 'lido'
        elif 'quero' in nome:
            estado_leitura = 'quero_ler'
        elif 'abandonado' in nome:
            estado_leitura = 'abandonado'

        if estado_leitura:
            leitura, criada = Leitura.objects.get_or_create(
                utilizador=utilizador,
                livro=livro,
                defaults={'estado': estado_leitura}
            )
            if not criada and leitura.estado != estado_leitura:
                leitura.estado = estado_leitura
                leitura.save()

        return True, f"✅ Livro guardado na estante '{estante.nome}'!"

    if Biblioteca.objects.filter(utilizador=utilizador, livro=livro, estante_customizada__isnull=True).exists():
        return False, "📚 Este livro já está guardado na tua biblioteca."

    Biblioteca.objects.create(utilizador=utilizador, livro=livro)

    leitura, criada = Leitura.objects.get_or_create(
        utilizador=utilizador,
        livro=livro,
        defaults={'estado': 'quero_ler'}
    )
    if not criada and leitura.estado != 'quero_ler':
        leitura.estado = 'quero_ler'
        leitura.save()
    return True, "Livro guardado na tua biblioteca."


def limpar_texto_descricao(texto):
    tags_permitidas = ['p', 'br', 'i', 'strong', 'em']
    return bleach.clean(texto, tags=tags_permitidas, strip=True)


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

    try:
        descricao = tradutor.translate(descricao, dest="pt").text
    except:
        pass

    categorias_api = info.get("categories", [])
    categorias_traduzidas = set()

    for categoria in categorias_api:
        try:
            traducao = tradutor.translate(categoria, dest="pt").text
            categorias_traduzidas.add(traducao.strip())
        except:
            categorias_traduzidas.add(categoria.strip())

    categorias_traduzidas = list(categorias_traduzidas)

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

    avaliacoes_api = AvaliacaoAPI.objects.filter(google_id=google_id).order_by("-data")
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
    avaliacoes_bd = livro.avaliacoes.select_related('utilizador').order_by('-data')

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
                nota_avaliacao = round(float(nota), 1)
                if not (1.0 <= nota_avaliacao <= 5.0):
                    raise ValueError("Fora do intervalo permitido.")

                avaliacao_existente = Avaliacao.objects.filter(utilizador=request.user, livro=livro).first()

                if avaliacao_existente:
                    messages.error(request, "Já adicionaste uma avaliação para este livro.")
                else:
                    Avaliacao.objects.create(
                        utilizador=request.user,
                        livro=livro,
                        avaliacao=nota_avaliacao,
                        comentario=comentario_texto
                    )
                    messages.success(request, "Comentário adicionado com sucesso! 🎉")
            except ValueError:
                messages.error(request, "A nota deve ser um número entre 1 e 5.")
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
                nota_avaliacao = Decimal(nota)
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
                    avaliacao=nota_avaliacao
                )
                messages.success(request, "Comentário adicionado com sucesso! 🎉")
        else:
            messages.error(request, "Preenche todos os campos corretamente.")

        return redirect("detalhe_livro_api", google_id=google_id)
     
@login_required
def editar_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, utilizador=request.user)
    if request.method == 'POST':
        avaliacao.comentario = request.POST.get('comentario', '').strip()
        avaliacao.avaliacao = Decimal(request.POST.get('avaliacao'))
        avaliacao.save()
        messages.success(request, "Comentário atualizado com sucesso.")
        return redirect('detalhe_livro', livro_id=avaliacao.livro.id)
    return render(request, 'avaliacao_editar.html', {'avaliacao': avaliacao})


@login_required
def remover_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, utilizador=request.user)
    livro_id = avaliacao.livro.id
    avaliacao.delete()
    messages.success(request, "Comentário removido.")
    return redirect('detalhe_livro', livro_id=livro_id)

@login_required
def editar_avaliacao_api(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAPI, id=avaliacao_id, utilizador=request.user)
    if request.method == 'POST':
        avaliacao.comentario = request.POST.get('comentario', '').strip()
        avaliacao.avaliacao = Decimal(request.POST.get('avaliacao'))
        avaliacao.save()
        messages.success(request, "Comentário atualizado com sucesso.")
        return redirect('detalhe_livro_api', google_id=avaliacao.google_id)
    return render(request, 'avaliacao_editar_api.html', {'avaliacao': avaliacao})


@login_required
def remover_avaliacao_api(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoAPI, id=avaliacao_id, utilizador=request.user)
    google_id = avaliacao.google_id
    avaliacao.delete()
    messages.success(request, "Comentário removido.")
    return redirect('detalhe_livro_api', google_id=google_id)
     

@login_required
def guardar_livro_api(request, google_id):

    dados = importar_dados_livro_api(google_id)
    if not dados:
        messages.error(request, "Não foi possível importar o livro.")
        return redirect('detalhe_livro_api', google_id=google_id)

    livro = Livro.objects.filter(google_id=google_id).first()
    estante_id = request.GET.get('estante_id') or request.POST.get('estante_id')

    if livro:
        sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
        messages.success(request, msg if sucesso else f"📚 {msg}")
        return redirect('detalhe_livro_api', google_id=google_id)

    livro = Livro.objects.create(
        titulo=dados['titulo'],
        autor=dados['autor'],
        sinopse=dados.get('descricao', 'Sem sinopse.'),
        num_pag=dados.get('num_paginas') or 100,
        ano_publicacao=dados.get('ano'),
        google_id=google_id
    )

    url_capa = dados.get('capa')
    if url_capa:
        r = requests.get(url_capa)
        if r.status_code == 200:
            nome_arquivo = f"{livro.titulo}.jpg"
            livro.capa.save(nome_arquivo, ContentFile(r.content), save=True)

    sucesso, msg = adicionar_livro_a_estante(request.user, livro, estante_id)
    messages.success(request, msg if sucesso else f"📚 {msg}")

    return redirect('detalhe_livro_api', google_id=google_id)


@login_required
def criar_estante_e_adicionar_api(request, google_id):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cor = request.POST.get("cor") or "#f5f5f5"  

        if not nome:
            messages.error(request, "Nome da estante em falta.")
            return redirect('detalhe_livro_api', google_id=google_id)

        if Estante.objects.filter(utilizador=request.user, nome__iexact=nome).exists():
            messages.error(request, "Já tens uma estante com esse nome.")
            return redirect('detalhe_livro_api', google_id=google_id)

        estante = Estante.objects.create(utilizador=request.user, nome=nome, cor=cor)  
        return redirect(f"/livro/api/{google_id}/guardar/?estante_id={estante.id}")

    messages.error(request, "Não foi possível criar a estante.")
    return redirect('detalhe_livro_api', google_id=google_id)


@login_required
def criar_estante_e_adicionar_bd(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cor = request.POST.get("cor") or "#f5f5f5"  
        livro_id = request.POST.get("livro_id")

        if not nome or not livro_id:
            messages.error(request, "Nome da estante ou ID do livro em falta.")
            return redirect('detalhe_livro', livro_id=livro_id)

        if Estante.objects.filter(utilizador=request.user, nome__iexact=nome).exists():
            messages.error(request, "Já tens uma estante com esse nome.")
            return redirect('detalhe_livro', livro_id=livro_id)

        estante = Estante.objects.create(utilizador=request.user, nome=nome, cor=cor)  
        return redirect(f"/livro/{livro_id}/?estante_id={estante.id}")

    messages.error(request, "Não foi possível criar a estante.")
    return redirect('detalhe_livro')

#Página de adicionar livro
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

        if not dados['titulo'] or not dados['autor'] or not dados['sinopse'] or not dados['num_pag']:
            messages.error(request, "Preenche todos os campos obrigatórios.")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

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

        try:
            dados['ano_publicacao'] = int(dados['ano_publicacao']) if dados['ano_publicacao'] else None
        except ValueError:
            messages.error(request, "Ano de publicação inválido.")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

        existe_por_titulo_autor = Livro.objects.filter(
            titulo__iexact=dados['titulo'],
            autor__iexact=dados['autor']
        ).exists()

        existe_por_isbn = False
        if dados['isbn']:
            existe_por_isbn = Livro.objects.filter(isbn=dados['isbn']).exists()

        if existe_por_titulo_autor or existe_por_isbn:
            messages.error(request, "Este livro já existe no sistema.")
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

            messages.success(request, "Livro adicionado com sucesso.")
            return redirect('inicio')

        except Exception as e:
            messages.error(request, f"Erro inesperado: {e}")
            return render(request, 'adicionar_livro.html', {
                'now': date.today(),
                'form_data': request.POST
            })

    return render(request, 'adicionar_livro.html', {
        'now': date.today(),
        'form_data': {}
    })

@login_required
def adicionar_anotacao(request, leitura_id):
    leitura = get_object_or_404(Leitura, id=leitura_id, utilizador=request.user)

    if request.method == 'POST':
        anotacao = request.POST.get('anotacoes', '').strip()
        leitura.anotacoes = anotacao
        leitura.save()
        messages.success(request, "Anotação guardada.")
        return redirect('inicio')  

    return render(request, 'anotacoes.html', {'leitura': leitura})

@login_required
def leitura_detalhes(request, leitura_id):
    leitura = get_object_or_404(Leitura, id=leitura_id, utilizador=request.user)
    
    progresso = ProgressoLeitura.objects.filter(utilizador=request.user, livro=leitura.livro).first()
    historico = LeituraDiaria.objects.filter(utilizador=request.user, livro=leitura.livro).order_by('-data')

    return render(request, 'leitura_detalhes.html', {
        'leitura': leitura,
        'progresso': progresso,
        'historico': historico
    })

def iniciar_ou_ver_leitura(request, livro_id):
    leitura, _ = Leitura.objects.get_or_create(
        utilizador=request.user,
        livro_id=livro_id,
    )
    return redirect('leitura_detalhes', leitura_id=leitura.id)
