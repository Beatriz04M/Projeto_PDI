from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class DesafioLeitura(models.Model):  
    participantes = models.ManyToManyField('Utilizadores.Utilizador', blank=True, related_name='desafios')
    titulo = models.CharField(max_length=255, unique=True)
    descricao = models.TextField()    
    data_inicio = models.DateField(auto_now_add=True)
    data_fim = models.DateField()
    meta = models.PositiveIntegerField(default=1)  

    class Meta:
        ordering = ['-data_inicio']  

    def clean(self):
        if self.data_fim and self.data_inicio:
            if self.data_inicio > self.data_fim:
                raise ValidationError("A data de início não pode ser posterior à data de fim.")

        if self.data_fim and self.data_fim < now().date():
            raise ValidationError("A data de fim não pode estar no passado.")

    def __str__(self):
        return f"{self.titulo} ({self.data_inicio} - {self.data_fim}) - Meta: {self.meta} livros"

