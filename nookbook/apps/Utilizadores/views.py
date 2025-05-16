from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from nookbook.apps.Utilizadores.models import Utilizador
from django.contrib.auth import logout


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

