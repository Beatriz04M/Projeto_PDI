from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from datetime import datetime

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
    data = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['utilizador', 'livro'], name='unique_avaliacao')
        ]

    def __str__(self):
        return f"{self.utilizador.nome} - {self.livro.titulo} ({self.avaliacao}/5)"
    
def ano_atual():
    return datetime.now().year

class Livro(models.Model):
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    sinopse = models.TextField()
    num_pag = models.IntegerField(validators=[MinValueValidator(1)])
    capa = models.ImageField(upload_to='capas/', blank=True, null=True, default='capas/capa_default.png')
    ano_publicacao = models.PositiveIntegerField(null=True, blank=True)
    generos = models.ManyToManyField('Generos', related_name='livros')
    palavra_chave = models.ManyToManyField('PalavraChave', blank=True, related_name='livros')
    editora = models.ForeignKey('Editora', on_delete=models.SET_NULL, null=True, blank=True, related_name='livros')
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    idioma = models.ForeignKey('Idioma', on_delete=models.SET_NULL, null=True, blank=True)
    google_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.titulo} ({self.autor})"
    
    @property
    def media_avaliacoes_individual(self):
        return self.avaliacoes.aggregate(media=Avg('avaliacao'))['media'] or 0


class AvaliacaoAPI(models.Model):
    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE)
    google_id = models.CharField(max_length=50)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    autor = models.CharField(max_length=255, blank=True, null=True)
    capa_url = models.URLField(blank=True, null=True)
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
        return f"{self.utilizador.nome} - {self.titulo or self.google_id} ({self.avaliacao}/5)"

    @property
    def get_avaliacao_display(self):
        return f"{self.avaliacao:.1f}"
    
    
class Leitura(models.Model):
    ESTADOS = (
        ('quero_ler', 'Quero Ler'),
        ('a_ler', 'A Ler'),
        ('lido', 'Lido'),
        ('abandonado', 'Abandonado'),
    )

    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE, related_name='leituras')
    livro = models.ForeignKey('Livros.Livro', on_delete=models.CASCADE, related_name='leituras')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='quero_ler')

    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)

    anotacoes = models.TextField(blank=True, null=True)

    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('utilizador', 'livro')

    def __str__(self):
        return f"{self.utilizador} - {self.livro.titulo} ({self.get_estado_display()})"
