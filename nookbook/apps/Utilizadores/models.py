from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UtilizadorManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        if not username:
            raise ValueError("O username é obrigatório")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)

def user_directory_path(instance, filename):
    return f'perfil/{instance.email}/{filename}'

class Utilizador(AbstractUser):
    nome = models.CharField(max_length=100, default="Utilizador")
    username = models.CharField(max_length=100, unique=True)  
    email = models.EmailField(unique=True)
    biografia = models.CharField(max_length=1000, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)

    IDIOMAS_CHOICES = [
        ('pt', 'Português'),
        ('en', 'Inglês'),
        ('es', 'Espanhol'),
        ('fr', 'Francês'),
        ('de', 'Alemão'),
    ]
    idioma = models.CharField(max_length=10, choices=IDIOMAS_CHOICES, default='pt')

    generos_fav = models.ManyToManyField('Livros.Generos', blank=True, related_name='utilizadores')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    EMAIL_FIELD = "email"  # <- esta linha que deves adicionar!

    objects = UtilizadorManager()

    def __str__(self):
        return f"{self.username} ({self.email})"
