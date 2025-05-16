import requests
from googletrans import Translator
tradutor = Translator()

def buscar_livros(filtro=None, valor=None, max_results=10, start_index=0):
    base_url = "https://www.googleapis.com/books/v1/volumes"

    if not valor:
        return None

    if filtro == "titulo":
        query = f"intitle:{valor}"
    elif filtro == "autor":
        query = f"inauthor:{valor}"
    elif filtro == "isbn":
        query = f"isbn:{valor}"
    elif filtro == "palavra":
        query = valor
    else:
        query = valor

    params = {
        "q": query,
        "maxResults": max_results,
        "startIndex": start_index,
        "printType": "books",
        "orderBy": "relevance", 
    }

    try:
        resposta = requests.get(base_url, params=params, timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print(f"Erro ao ligar à API do Google Books: {e}")
        return None



def extrair_dados_livros(json_data, traduzir=False):
    livros = []

    for item in json_data.get('items', []):
        info = item.get('volumeInfo', {})
        google_id = item.get('id')
        titulo = info.get('title')
        autores = info.get('authors')
        descricao = info.get('description')
        imagem_links = info.get('imageLinks', {})
        capa = imagem_links.get('thumbnail')
        nota = info.get('averageRating') if 'averageRating' in info else None

        # Filtro: só livros com todos os dados obrigatórios
        if not (google_id and titulo and autores and descricao and capa):
            continue

        if traduzir:
            try:
                descricao = tradutor.translate(descricao, dest='pt').text
            except Exception as e:
                print(f"Erro ao traduzir: {e}")

        livro = {
            'google_id': google_id,
            'titulo': titulo,
            'autor': ", ".join(autores),
            'descricao': descricao,
            'capa': capa,
            'nota': nota or "N/A"
        }
        livros.append(livro)

    return livros
