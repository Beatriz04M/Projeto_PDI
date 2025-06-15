from django import forms
from .models import DesafioLeitura

class DesafioLeituraForm(forms.ModelForm):
    class Meta:
        model = DesafioLeitura
        fields = ['titulo', 'descricao', 'data_fim', 'meta']
        widgets = {
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }
