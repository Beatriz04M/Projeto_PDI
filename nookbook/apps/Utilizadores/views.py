from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as update_session_auth_hash, get_user_model
User = get_user_model()
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from nookbook.apps.Utilizadores.models import Utilizador
from django.contrib.auth import logout
from nookbook.apps.Desafios.models import DesafioLeitura
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import datetime
from datetime import datetime
from nookbook.apps.Livros.models import Avaliacao, AvaliacaoAPI


def registo_view(request):
    if request.method == "GET":
        return render(request, 'registo.html')

    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verificar se o username já existe
        if Utilizador.objects.filter(username=username).exists():
            return JsonResponse({"sucesso": False, "mensagem": "Este nome de utilizador já está registado."})

        # Verificar se o email já existe
        if Utilizador.objects.filter(email=email).exists():
            return JsonResponse({"sucesso": False, "mensagem": "Este email já está registado."})

        # Criar o utilizador
        try:
            user = Utilizador.objects.create_user(username=username, email=email, password=password)
            user.save()
            return JsonResponse({"sucesso": True, "mensagem": "Utilizador criado com sucesso!"})
        except Exception as e:
            return JsonResponse({"sucesso": False, "mensagem": f"Ocorreu um erro: {str(e)}"})

    return JsonResponse({"sucesso": False, "mensagem": "Método inválido."})

def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')

    elif request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            auth_login(request, user)
            return JsonResponse({"sucesso": True, "redirect_url": "/"})
        else:
            return JsonResponse({"sucesso": False, "mensagem": "Email ou password incorretos."})

    return JsonResponse({"sucesso": False, "mensagem": "Método inválido."})

@login_required
def confirmar_logout(request):
    return render(request, "logout.html")


@login_required
def fazer_logout(request):
    logout(request)
    return redirect('pagina_inicial') 


@login_required
def perfil_view(request):
    user = request.user
    ano_atual = datetime.now().year

    # Desafios
    desafios = DesafioLeitura.objects.all()
    for desafio in desafios:
        desafio.esta_a_participar = user in desafio.participantes.all()

    # Reviews feitas pelo utilizador (base de dados)
    reviews_bd = Avaliacao.objects.filter(utilizador=user).select_related('livro')

    # Reviews da API — apenas se tiverem título e comentário
    reviews_api_raw = AvaliacaoAPI.objects.filter(utilizador=user)
    reviews_api = []
    for r in reviews_api_raw:
        if r.titulo and r.comentario:  
            reviews_api.append({
                'titulo': r.titulo,
                'autor': r.autor or "Autor desconhecido",
                'capa_url': r.capa_url or "/static/imagens/capa_default.png",
                'comentario': r.comentario,
                'avaliacao': r.avaliacao,
            })

    context = {
        'user': user,
        'esconder_barra_pesquisa': True,
        'current_year': ano_atual,
        'desafios': desafios,
        'reviews_bd': reviews_bd,
        'reviews_api': reviews_api,
    }

    return render(request, 'perfil.html', context)



@login_required
def participar_desafio(request, desafio_id):
    desafio = get_object_or_404(DesafioLeitura, pk=desafio_id)
    utilizador = request.user  

    if utilizador not in desafio.participantes.all():
        desafio.participantes.add(utilizador)
    else:
        desafio.participantes.remove(utilizador)

    return redirect('perfil')

@csrf_protect
@login_required
def editar_perfil_view(request):
    user = request.user

    if request.method == 'POST':
        form_action = request.POST.get('form_action')

        if form_action == 'editar_perfil':
            user.username = request.POST.get('nome')
            user.biografia = request.POST.get('biografia')
            if 'foto' in request.FILES:
                user.foto_perfil = request.FILES['foto']
            user.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect ('editar_perfil')

        elif form_action == 'email':
            novo_email = request.POST.get('email')
            if not novo_email:
                messages.error(request, "O campo de e-mail não pode estar vazio.")
            elif User.objects.filter(email=novo_email).exclude(id=user.id).exists():
                messages.error(request, "Este e-mail já está a ser usado.")
            else:
                user.email = novo_email
                user.save()
                messages.success(request, "E-mail atualizado com sucesso!")
            return HttpResponseRedirect(reverse('editar_perfil') + '#gestao')


        elif form_action == 'password':
            nova_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if not nova_password or len(nova_password) < 6:
                messages.error(request, "A password deve ter pelo menos 6 caracteres.")
            elif nova_password != confirm_password:
                messages.error(request, "As passwords não coincidem.")
            else:
                user.set_password(nova_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password alterada com sucesso!")
            return HttpResponseRedirect(reverse('editar_perfil') + '#gestao')

        elif form_action == 'dados_pessoais':
            user.data_nascimento = request.POST.get('data_nascimento')
            user.pais = request.POST.get('pais')
            user.idioma = request.POST.get('idioma')
            user.save()
            messages.success(request, "Dados pessoais atualizados com sucesso!")
        return HttpResponseRedirect(reverse('editar_perfil') + '#gestao')

    return render(request, 'editar_perfil.html', {
        'esconder_barra_pesquisa': True
    })
