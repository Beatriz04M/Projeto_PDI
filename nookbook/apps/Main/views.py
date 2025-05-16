from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from nookbook.apps.Biblioteca.models import Biblioteca, Estante, ProgressoLeitura, LeituraDiaria
from nookbook.apps.Livros.models import Livro
from django.db.models import Avg, Q
from django.utils.timezone import localdate
from datetime import timedelta
from collections import defaultdict
import json

@login_required
def inicio(request):
    user = request.user

    # Obter a estante "A ler"
    estante_a_ler = Estante.objects.filter(utilizador=user, nome__iexact="a ler").first()

    livros_estante = []
    if estante_a_ler:
        livros_estante = Biblioteca.objects.filter(
            utilizador=user,
            estante_customizada=estante_a_ler
        ).select_related('livro')

    # Construir lista de livros em leitura
    em_leitura = []
    for b in livros_estante:
        # Garante que existe um ProgressoLeitura
        progresso, _ = ProgressoLeitura.objects.get_or_create(
            utilizador=user,
            livro=b.livro,
            defaults={'pag_atual': 0}
        )

        percentagem = 0
        if progresso.livro.num_pag:
            percentagem = int(progresso.pag_atual / progresso.livro.num_pag * 100)

        em_leitura.append({
            'id': b.livro.id,
            'titulo': b.livro.titulo,
            'autor': b.livro.autor,
            'capa': b.livro.capa.url if b.livro.capa else '',
            'pag_atual': progresso.pag_atual,
            'pag_total': b.livro.num_pag,
            'percentagem': percentagem,
            'progresso_id': progresso.id
        })

    # === Marcar dias de leitura desta semana ===
    hoje = localdate()
    inicio_semana = hoje - timedelta(days=hoje.weekday())

    leituras_semana = LeituraDiaria.objects.filter(
        utilizador=user,
        data__gte=inicio_semana
    ).select_related('livro')

    # Mapeamento livro_id → progresso_id com base em 'em_leitura'
    livro_to_progresso = {livro['id']: livro['progresso_id'] for livro in em_leitura}

    dias_por_progresso = defaultdict(set)

    for leitura in leituras_semana:
        livro_id = leitura.livro.id
        progresso_id = livro_to_progresso.get(livro_id)
        if progresso_id:
            dias_por_progresso[str(progresso_id)].add(leitura.data.weekday())

    dias_lidos_json = json.dumps({pid: list(dias) for pid, dias in dias_por_progresso.items()})

    # IDs de livros já na biblioteca
    livros_na_biblioteca = Biblioteca.objects.filter(
        utilizador=user
    ).values_list('livro_id', flat=True)

    # Livros recomendados
    livros_qs = (
        Livro.objects
        .exclude(id__in=livros_na_biblioteca)
        .annotate(media_avaliacoes=Avg('avaliacoes__avaliacao'))
        .filter(Q(media_avaliacoes__gte=3) | Q(ano_publicacao__gte=2020))
        .order_by('media_avaliacoes')
    )
    livros_recomendados = list(livros_qs[:10])
    tem_livros_na_estante = livros_estante.exists()

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
            if paginas > 0:
                if progresso.livro.num_pag and progresso.livro.num_pag > 0:
                    progresso.pag_atual = min(progresso.pag_atual + paginas, progresso.livro.num_pag)
                else:
                    progresso.pag_atual += paginas
                progresso.save()

                data_hoje = localdate()
                leitura, created = LeituraDiaria.objects.get_or_create(
                    utilizador=request.user,
                    livro=progresso.livro,
                    data=data_hoje,
                    defaults={'paginas_lidas': paginas}
                )

                if not created:
                    leitura.paginas_lidas += paginas
                    leitura.save()

                messages.success(request, f"Progresso atualizado para '{progresso.livro.titulo}'!")
            else:
                messages.warning(request, "Insere um número de páginas maior que 0.")
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
