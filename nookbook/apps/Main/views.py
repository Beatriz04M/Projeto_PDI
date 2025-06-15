from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from nookbook.apps.Biblioteca.models import Biblioteca, Estante, ProgressoLeitura, LeituraDiaria
from nookbook.apps.Livros.models import Livro, Leitura
from nookbook.apps.Livros.views import importar_dados_livro_api
from django.db.models import Avg, Q
from django.utils.timezone import localdate
from datetime import timedelta
from collections import defaultdict
import json
from random import sample, choice

@login_required
def inicio(request):
    user = request.user

    # === Estante "A Ler"
    estante_a_ler = Estante.objects.filter(utilizador=user, nome__iexact="a ler").first()
    livros_estante = Biblioteca.objects.filter(utilizador=user, estante_customizada=estante_a_ler).select_related('livro') if estante_a_ler else []

    # === Construir lista de livros em leitura
    em_leitura = []
    for b in livros_estante:
        progresso, _ = ProgressoLeitura.objects.get_or_create(
            utilizador=user, livro=b.livro, defaults={'pag_atual': 0}
        )

        percentagem = int((progresso.pag_atual / b.livro.num_pag) * 100) if b.livro.num_pag else 0

        leitura, _ = Leitura.objects.get_or_create(
            utilizador=user, livro=b.livro, defaults={'estado': 'a_ler'}
        )

        em_leitura.append({
            'id': b.livro.id,
            'titulo': b.livro.titulo,
            'autor': b.livro.autor,
            'capa': b.livro.capa.url if b.livro.capa else '',
            'pag_atual': progresso.pag_atual,
            'pag_total': b.livro.num_pag,
            'percentagem': percentagem,
            'progresso_id': progresso.id,
            'leitura_id': leitura.id
        })

    # === Marcar dias da semana com leitura
    hoje = localdate()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    leituras_semana = LeituraDiaria.objects.filter(utilizador=user, data__gte=inicio_semana).select_related('livro')

    livro_to_progresso = {livro['id']: livro['progresso_id'] for livro in em_leitura}
    dias_por_progresso = defaultdict(set)
    for leitura in leituras_semana:
        pid = livro_to_progresso.get(leitura.livro.id)
        if pid:
            dias_por_progresso[str(pid)].add(leitura.data.weekday())

    dias_lidos_json = json.dumps({k: list(v) for k, v in dias_por_progresso.items()})

    # === Recomendações
    livros_na_biblioteca = Biblioteca.objects.filter(utilizador=user).values_list('livro_id', flat=True)

    livros_bd = (
        Livro.objects
        .exclude(id__in=livros_na_biblioteca)
        .annotate(media_avaliacoes=Avg('avaliacoes__avaliacao'))
        .filter(Q(media_avaliacoes__gte=3.5) | Q(ano_publicacao__gte=2020))
        .order_by('-media_avaliacoes', '-ano_publicacao')
    )
    livros_bd_amostrados = sample(list(livros_bd), min(3, livros_bd.count()))

    # === API: buscar até 3 livros aleatórios com base em termos
    termos = ['aventura', 'romance', 'ficção', 'mistério', 'história']
    livros_api = []
    tentativas = 0
    while len(livros_api) < 3 and tentativas < 10:
        termo = choice(termos)
        dados = importar_dados_livro_api(termo)
        if dados:
            titulos_existentes = [l.titulo if hasattr(l, 'titulo') else l['titulo'] for l in livros_bd_amostrados + livros_api]
            if dados['titulo'] not in titulos_existentes:
                livros_api.append(dados)
        tentativas += 1

    # Combinar e limitar
    livros_recomendados = livros_bd_amostrados + livros_api
    livros_recomendados = sample(livros_recomendados, min(6, len(livros_recomendados)))

    tem_livros_na_estante = livros_estante.exists() if estante_a_ler else False

    return render(request, 'pagina_inicial.html', {
        'em_leitura': em_leitura,
        'livros_recomendados': livros_recomendados,
        'estante_a_ler': estante_a_ler,
        'tem_livros_na_estante': tem_livros_na_estante,
        'dias_lidos_json': dias_lidos_json
    })

def registar_leitura(request):
    if request.method == 'POST':
        progresso_id = request.POST.get('progresso_id')

        if not progresso_id or not progresso_id.isdigit():
            messages.error(request, "Seleciona um livro antes de registar a leitura.")
            return redirect('inicio')

        progresso = get_object_or_404(ProgressoLeitura, id=progresso_id, utilizador=request.user)

        try:
            paginas = int(request.POST.get('paginas', 0))
            if paginas <= 0:
                messages.warning(request, "Insere um número de páginas maior que 0.")
                return redirect('inicio')

            livro = progresso.livro
            progresso.pag_atual = min(progresso.pag_atual + paginas, livro.num_pag)
            progresso.save()

            # Registo diário
            data_hoje = localdate()
            leitura_diaria, created = LeituraDiaria.objects.get_or_create(
                utilizador=request.user,
                livro=livro,
                data=data_hoje,
                defaults={'paginas_lidas': paginas}
            )
            if not created:
                leitura_diaria.paginas_lidas += paginas
                leitura_diaria.save()

            # Atualização na tabela Leitura
            leitura = Leitura.objects.filter(utilizador=request.user, livro=livro).first()
            if leitura:
                if leitura.data_inicio is None:
                    leitura.data_inicio = data_hoje
                if progresso.pag_atual >= livro.num_pag:
                    leitura.data_fim = data_hoje
                    leitura.estado = 'lido'

                    # Mover para estante "Lidos"
                    estante_lidos = Estante.objects.filter(utilizador=request.user, nome__iexact="Lidos").first()
                    if estante_lidos:
                        # Remover de outras estantes (caso existam)
                        Biblioteca.objects.filter(utilizador=request.user, livro=livro).delete()
                        Biblioteca.objects.create(utilizador=request.user, livro=livro, estante_customizada=estante_lidos)

                leitura.save()

            messages.success(request, f"Progresso atualizado para '{livro.titulo}'!")
        except (ValueError, TypeError):
            messages.error(request, "Erro ao registar leitura.")

    return redirect('inicio')



def detalhes_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)

    estantes_utilizador = None
    if request.user.is_authenticated:
        estantes_utilizador = Estante.objects.filter(utilizador=request.user)

    return render(request, 'detalhe_livro.html', {
        'livro': livro,
        'estantes': estantes_utilizador,
    })