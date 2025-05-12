from django.contrib.auth.backends import ModelBackend
from apps.Utilizadores.models import Utilizador

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Utilizador.objects.get(email=username)  
            if user.check_password(password):
                return user
        except Utilizador.DoesNotExist:
            return None
