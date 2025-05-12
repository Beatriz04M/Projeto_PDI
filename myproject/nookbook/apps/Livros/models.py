from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Generos(models.Model):
    class TipoGenero(models.TextChoices):
        FICCAO = 'ficcao', 'Ficção'
        ROMANCE = 'romance', 'Romance'
        TERROR = 'terror', 'Terror'
        FANTASIA = 'fantasia', 'Fantasia'
        SUSPENSE = 'suspense', 'Suspense'
        CIENCIA = 'ciencia', 'Ciência'
        HISTORIA = 'historia', 'História'
        BIOGRAFIA = 'biografia', 'Biografia'
        AUTOAJUDA = 'autoajuda', 'Autoajuda'
        INFANTIL = 'infantil', 'Infantil'
        CLASSICO = 'classico', 'Clássico'
        OUTRO = 'outro', 'Outro'
        NENHUM = 'nenhum', 'Nenhum'

    nome = models.CharField(
        max_length=20,
        choices=TipoGenero.choices,
        unique=True
    )

    def __str__(self):
        return self.get_nome_display()

class Editora(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome

class Idioma(models.Model):
    codigo = models.CharField(max_length=10)  
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class FonteLivro(models.Model):
    nome = models.CharField(max_length=50)  
    referencia_api = models.CharField(max_length=255, blank=True, null=True)  
    data_importacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class PalavraChave(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Avaliacao(models.Model):
    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE)
    livro = models.ForeignKey('Livros.Livro', on_delete=models.CASCADE, related_name='avaliacoes')
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    comentario = models.TextField(blank=True, null=True)  

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['utilizador', 'livro'], name='unique_avaliacao')
        ]

    def __str__(self):
        return f"{self.utilizador.nome} - {self.livro.titulo} ({self.avaliacao}/5)"
    

class Livro(models.Model):
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    sinopse = models.TextField()
    num_pag = models.IntegerField(validators=[MinValueValidator(1)])
    capa = models.ImageField(upload_to='livros/', blank=True, null=True)
    ano_publicacao = models.PositiveIntegerField(blank=True, null=True)
    generos = models.ManyToManyField('Generos', related_name='livros')
    palavra_chave = models.ManyToManyField('PalavraChave', blank=True, related_name='livros')
    editora = models.ForeignKey('Editora', on_delete=models.SET_NULL, null=True, blank=True, related_name='livros')
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    idioma = models.ForeignKey('Idioma', on_delete=models.SET_NULL, null=True, blank=True)
    google_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.titulo} ({self.autor})"
    
    @property
    def media_avaliacoes(self):
        return self.avaliacoes.aggregate(media=Avg('avaliacao'))['media'] or 0


class AvaliacaoAPI(models.Model):
    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE)
    google_id = models.CharField(max_length=50)
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    comentario = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilizador', 'google_id')

    def __str__(self):
        return f"{self.utilizador.nome} - {self.google_id} ({self.avaliacao}/5)"

    def get_avaliacao_display(self):
        return f"{self.avaliacao:.1f}"
