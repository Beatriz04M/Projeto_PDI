from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Estante(models.Model):
    nome = models.CharField(max_length=50)
    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE, related_name='estantes')
    cor = models.CharField(max_length=7, blank=True, null=True, default="#f9b4c6")

    class Meta:
        unique_together = ['nome', 'utilizador']

    def __str__(self):
        return f"{self.nome} ({self.utilizador.nome})"

class Biblioteca(models.Model):
    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE)
    livro = models.ForeignKey('Livros.Livro', on_delete=models.CASCADE)
    estante_customizada = models.ForeignKey('Estante', on_delete=models.SET_NULL, null=True, blank=True)
    data_adicao = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('utilizador', 'livro', 'estante_customizada')

    def __str__(self):
        estante = self.estante_customizada.nome if self.estante_customizada else "Sem estante"
        return f"{self.utilizador.nome} adicionou '{self.livro.titulo}' à estante {self.estante.nome}"

class ProgressoLeitura(models.Model):  
    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE)
    livro = models.ForeignKey('Livros.Livro', on_delete=models.CASCADE)
    pag_atual = models.IntegerField(default=0, validators=[MinValueValidator(0)])  
    anotacao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    inicio_leitura = models.DateTimeField(blank=True, null=True)
    fim_leitura = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['utilizador', 'livro'], name='unique_progresso_leitura')
        ]

    def clean(self):
        if self.pag_atual > self.livro.num_pag:
            raise ValidationError(f"A página atual ({self.pag_atual}) não pode ser maior que o total de páginas ({self.livro.num_pag}).")

        if self.inicio_leitura and self.fim_leitura and self.fim_leitura < self.inicio_leitura:
            raise ValidationError("A data de fim da leitura não pode ser anterior à data de início.")

    @property
    def percentagem_lida(self):
        if self.livro and self.livro.num_pag > 0:
            return round((self.pag_atual / self.livro.num_pag) * 100, 2)
        return 0

    @property
    def esta_lido(self):
        return self.percentagem_lida >= 100

    def __str__(self):
        return f"{self.utilizador.nome} - {self.livro.titulo} ({self.pag_atual}/{self.livro.num_pag} - {self.percentagem_lida}%)"

    
class Recomendacao(models.Model):
    class Fonte(models.TextChoices):
        IA = 'ia', 'IA'
        MANUAL = 'manual', 'Manual'
        OUTRO = 'outro', 'Outro'

    utilizador = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.CASCADE, related_name='recomendacoes_recebidas')
    livro = models.ForeignKey('Livros.Livro', on_delete=models.CASCADE)
    fonte = models.CharField(max_length=10, choices=Fonte.choices, default=Fonte.IA)
    recomendado_por = models.ForeignKey('Utilizadores.Utilizador', on_delete=models.SET_NULL, null=True, blank=True, related_name='recomendacoes_feitas')  # Só se for manual
    motivo = models.TextField(blank=True, null=True)
    data_recomendacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['utilizador', 'livro']

    def __str__(self):
        return f"{self.livro.titulo} recomendado a {self.utilizador.nome} ({self.get_fonte_display()})"

