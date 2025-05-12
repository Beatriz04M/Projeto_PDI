from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from nookbook.apps.Livros.models import Livro, Avaliacao
from nookbook.apps.Biblioteca.models import ProgressoLeitura

@login_required
def dashboard(request):
    user = request.user

    # ✅ 1. IDs dos livros que o utilizador já leu
    livros_lidos_ids = ProgressoLeitura.objects.filter(
        utilizador=user,
        estado='Lido'
    ).values_list('livro_id', flat=True)

    # ✅ 2. Livros lidos (queryset real, se precisares para algo)
    livros_lidos = Livro.objects.filter(id__in=livros_lidos_ids)

    # ✅ 3. Obter os géneros favoritos com base nos livros lidos
    generos_favoritos = livros_lidos.values_list('generos', flat=True).distinct()

    # ✅ 4. Recomendações com base nos géneros
    if generos_favoritos.exists():
        livros_recomendados = Livro.objects.filter(
            generos__in=generos_favoritos
        ).exclude(
            id__in=livros_lidos_ids
        ).distinct()[:10]
    else:
        # ✅ 5. Fallback: livros mais bem avaliados
        livros_recomendados = Livro.objects.annotate(
            media=Avg('avaliacao__pontuacao')  # usa related_name se definido, senão: avaliacao_set
        ).order_by('-media')[:10]

    # ✅ 6. Livro atual (estado = 'A ler')
    livro_atual_id = ProgressoLeitura.objects.filter(
        utilizador=user,
        estado='A ler'
    ).values_list('livro_id', flat=True).first()

    livro_atual = Livro.objects.filter(id=livro_atual_id).first()

    return render(request, 'Main/dashboard.html', {
        'livros_recomendados': livros_recomendados,
        'livro_atual': livro_atual,
    })
