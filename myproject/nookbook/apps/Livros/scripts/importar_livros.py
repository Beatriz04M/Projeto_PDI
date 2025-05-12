from apps.Livros.models import Livro, Generos
from django.core.files.base import ContentFile

# Dicionário com os livros organizados por género
livros_por_genero = {
    "ficcao": [
        {"titulo": "A Sombra do Vento", "autor": "Carlos Ruiz Zafón"},
        {"titulo": "1984", "autor": "George Orwell"},
        {"titulo": "A Menina que Roubava Livros", "autor": "Markus Zusak"},
        {"titulo": "O Conto da Aia", "autor": "Margaret Atwood"},
        {"titulo": "Cem Anos de Solidão", "autor": "Gabriel García Márquez"},
        {"titulo": "As Intermitências da Morte", "autor": "José Saramago"},
    ],
    "romance": [
        {"titulo": "Orgulho e Preconceito", "autor": "Jane Austen"},
        {"titulo": "O Diário de uma Paixão", "autor": "Nicholas Sparks"},
        {"titulo": "Como Eu Era Antes de Você", "autor": "Jojo Moyes"},
        {"titulo": "P.S. Eu Te Amo", "autor": "Cecelia Ahern"},
        {"titulo": "Anna e o Beijo Francês", "autor": "Stephanie Perkins"},
        {"titulo": "Um Dia", "autor": "David Nicholls"},
    ],
    "terror": [
        {"titulo": "O Iluminado", "autor": "Stephen King"},
        {"titulo": "Drácula", "autor": "Bram Stoker"},
        {"titulo": "Frankenstein", "autor": "Mary Shelley"},
        {"titulo": "A Assombração da Casa da Colina", "autor": "Shirley Jackson"},
        {"titulo": "O Cemitério", "autor": "Stephen King"},
        {"titulo": "Coraline", "autor": "Neil Gaiman"},
    ],
    "fantasia": [
        {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling"},
        {"titulo": "O Hobbit", "autor": "J.R.R. Tolkien"},
        {"titulo": "O Nome do Vento", "autor": "Patrick Rothfuss"},
        {"titulo": "Eragon", "autor": "Christopher Paolini"},
        {"titulo": "A Bússola Dourada", "autor": "Philip Pullman"},
        {"titulo": "A Rainha Vermelha", "autor": "Victoria Aveyard"},
    ],
    "suspense": [
        {"titulo": "Garota Exemplar", "autor": "Gillian Flynn"},
        {"titulo": "A Paciente Silenciosa", "autor": "Alex Michaelides"},
        {"titulo": "O Código Da Vinci", "autor": "Dan Brown"},
        {"titulo": "Antes de Dormir", "autor": "S.J. Watson"},
        {"titulo": "Os Homens que Não Amavam as Mulheres", "autor": "Stieg Larsson"},
        {"titulo": "A Garota no Trem", "autor": "Paula Hawkins"},
    ]
}

# Inserção dos livros na base de dados
for chave_genero, lista_livros in livros_por_genero.items():
    genero_obj, _ = Generos.objects.get_or_create(nome=chave_genero)

    for livro in lista_livros:
        novo_livro, created = Livro.objects.get_or_create(
            titulo=livro['titulo'],
            autor=livro['autor'],
            defaults={
                'sinopse': "Sinopse indisponível.",
                'num_pag': 100,
                'ano_publicacao': None,
                'isbn': None,
            }
        )
        novo_livro.generos.add(genero_obj)
        novo_livro.save()
