document.addEventListener('DOMContentLoaded', function () {
  setupTagInput('keyword-input', 'keywords-wrapper', 'keywords-hidden');
  initGenreSuggestions();
  initPreviewHandlers();
  setupFormValidation();
  setupMensagemTimeout();
});

function setupMensagemTimeout() {
  const mensagens = document.querySelectorAll('.alerta');
  mensagens.forEach(mensagem => {
    setTimeout(() => {
      mensagem.style.transition = 'opacity 0.5s ease-out';
      mensagem.style.opacity = '0';
      setTimeout(() => mensagem.remove(), 500);
    }, 3000);
  });
}

function setupFormValidation() {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    const titulo = document.querySelector("input[name='titulo']").value;
    const autores = document.querySelector("input[name='autores']").value;
    const numPag = document.querySelector("input[name='num_pag']").value;
    const ano = document.querySelector("input[name='ano_publicacao']").value;

    const currentYear = new Date().getFullYear();
    const onlyNumberRegex = /^\d+$/;
    const autorRegex = /^[A-Za-zÀ-ÿ\s.]+$/;

    if (!autorRegex.test(autores)) {
      alert("O nome do autor só pode conter letras, espaços e pontos.");
      e.preventDefault();
    }

    if (!onlyNumberRegex.test(numPag) || numPag < 1 || numPag > 5000) {
      alert("Número de páginas inválido. Deve ser entre 1 e 5000.");
      e.preventDefault();
    }


    if (ano && (ano <= 1000 || ano > currentYear)) {
      alert(`Ano de publicação inválido. Deve ser entre 1000 e ${currentYear}.`);
      e.preventDefault();
    }
  });
}

function setupTagInput(inputId, wrapperId, hiddenId) {
  const input = document.getElementById(inputId);
  const wrapper = document.getElementById(wrapperId);
  const hiddenInput = document.getElementById(hiddenId);

  if (!input || !wrapper || !hiddenInput) return;

  let tags = [];

  function updateHiddenInputs() {
    wrapper.querySelectorAll(`input[data-tag-generated="true"]`).forEach(el => el.remove());

    tags.forEach(tag => {
      const inputEl = document.createElement('input');
      inputEl.type = 'hidden';
      inputEl.name = hiddenInput.name;
      inputEl.value = tag;
      inputEl.setAttribute("data-tag-generated", "true");
      wrapper.appendChild(inputEl);
    });
  }

  function updatePlaceholder() {
    input.placeholder = tags.length > 0 ? '' :
      (inputId === 'autor-input' ? 'Autores' : 'Palavras-chave (ex: mistério, futebol)');
  }

  function createTag(text) {
    const tag = text.trim();
    if (!tag || tags.includes(tag)) return;

    tags.push(tag);

    const tagEl = document.createElement('span');
    tagEl.className = 'tag';
    tagEl.textContent = tag;

    const removeBtn = document.createElement('span');
    removeBtn.className = 'remove-tag';
    removeBtn.textContent = '×';
    removeBtn.onclick = () => {
      tags = tags.filter(t => t !== tag);
      wrapper.removeChild(tagEl);
      updateHiddenInputs();
      updatePlaceholder();
    };

    tagEl.appendChild(removeBtn);
    wrapper.insertBefore(tagEl, input);
    updateHiddenInputs();
    updatePlaceholder();
  }

  input.addEventListener('keydown', function (e) {
    if (e.key === ',' || e.key === 'Enter') {
      e.preventDefault();
      createTag(input.value.replace(/,$/, ''));
      input.value = '';
    }
  });

  if (hiddenInput.value) {
    tags = hiddenInput.value.split(',').map(t => t.trim()).filter(Boolean);
    tags.forEach(createTag);
  }

  document.querySelector('form').addEventListener('submit', function () {
    const pending = input.value.trim();
    if (pending && !tags.includes(pending)) {
      createTag(pending);
    }
    updateHiddenInputs();
  });
}

function initPreviewHandlers() {
  const input = document.getElementById('capa');
  const preview = document.getElementById('preview-capa');
  const placeholder = document.getElementById('placeholder');
  const previewContainer = document.getElementById('preview-container');
  const removeBtn = document.getElementById('remove-capa-btn');

  if (!input || !preview || !placeholder || !previewContainer || !removeBtn) return;

  input.addEventListener('change', function (event) {
    if (event.target.files && event.target.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
        previewContainer.style.display = 'block';
        removeBtn.style.display = 'inline-block';
        placeholder.style.display = 'none';
      };
      reader.readAsDataURL(event.target.files[0]);
    }
  });

  removeBtn.addEventListener('click', function () {
    input.value = '';
    preview.src = '#';
    previewContainer.style.display = 'none';
    removeBtn.style.display = 'none';
    placeholder.style.display = 'block';
  });
}

function initGenreSuggestions() {
  const allGenres = ["Romance", "Aventura", "Ficção", "Mistério", "Fantasia", "Thriller", "Sci-Fi", "História", "Drama", "Comédia"];
  let selectedGenres = [];
  const genreInput = document.querySelector("#genre-input");
  const genreWrapper = document.querySelector("#genre-tag-wrapper");
  const genreSuggestions = document.querySelector("#genre-suggestions");

  if (!genreInput || !genreWrapper || !genreSuggestions) return;

  genreInput.addEventListener("input", () => {
    filterGenreSuggestions();
    genreSuggestions.style.display = "block";
  });

  genreInput.addEventListener("focus", () => {
    filterGenreSuggestions();
    genreSuggestions.style.display = "block";
  });

  genreInput.addEventListener("click", (e) => {
    e.stopPropagation();
    genreSuggestions.style.display = "block";
  });

  document.addEventListener("click", (e) => {
    if (!genreWrapper.contains(e.target) && !genreSuggestions.contains(e.target)) {
      genreSuggestions.style.display = "none";
    }
  });

function addGenreTag(genre) {
  if (!selectedGenres.includes(genre)) {
    selectedGenres.push(genre);

    const tag = document.createElement("div");
    tag.className = "tag";
    tag.textContent = genre;

    const removeTag = document.createElement("span");
    removeTag.className = "remove-tag";
    removeTag.textContent = "x";
    removeTag.onclick = () => removeGenreTag(genre, tag);
    tag.appendChild(removeTag);

    genreWrapper.insertBefore(tag, genreInput);
    genreInput.value = "";
    genreSuggestions.innerHTML = "";
    genreSuggestions.style.display = "none";

    genreInput.placeholder = "";
  }
}

  function removeGenreTag(genre, tag) {
    selectedGenres = selectedGenres.filter(item => item !== genre);
    genreWrapper.removeChild(tag);
    filterGenreSuggestions();

    if (selectedGenres.length === 0) {
      genreInput.placeholder = "Géneros (ex: Romance, Aventura)";
    }
  }

  function filterGenreSuggestions() {
    const inputValue = genreInput.value.toLowerCase();
    genreSuggestions.innerHTML = "";

    const filtered = allGenres.filter(genre =>
      !selectedGenres.includes(genre) &&
      (inputValue === "" || genre.toLowerCase().includes(inputValue))
    );

    if (filtered.length > 0) {
      genreSuggestions.style.display = "block";
      filtered.forEach(genre => {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.textContent = genre;
        div.onclick = () => addGenreTag(genre);
        genreSuggestions.appendChild(div);
      });
    } else {
      genreSuggestions.style.display = "none";
    }
  }
}

function toggleComentarioForm() {
  const form = document.getElementById("comentario-form");
  if (!form) return;
  const isHidden = form.style.display === "none" || form.style.display === "";
  form.style.display = isHidden ? "block" : "none";
}

function toggleAdicionarDropdown() {
  const dropdown = document.getElementById("dropdown-adicionar-conteudo");
  dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

document.addEventListener("click", function (e) {
  const dropdown = document.getElementById("dropdown-adicionar-conteudo");
  const botaoDropdown = document.querySelector(".btn-adicionar-livro");

  if (dropdown && !dropdown.contains(e.target) && !botaoDropdown.contains(e.target)) {
    dropdown.style.display = "none";
  }

  const formComentario = document.getElementById("comentario-form");
  const botaoComentario = document.querySelector(".btn-toggle-comentario");

  if (formComentario && !formComentario.contains(e.target) && !botaoComentario.contains(e.target)) {
    formComentario.style.display = "none";
  }
});

function fecharDropdown() {
  const dropdown = document.getElementById("dropdown-adicionar-conteudo");
  if (dropdown) {
    dropdown.style.display = "none";
  }
}

function fecharComentarioForm() {
  const form = document.getElementById("comentario-form");
  if (form) {
    form.style.display = "none";
  }
}

function validarISBNInput() {
  const isbnField = document.getElementById("isbn");
  const erroDiv = document.getElementById("erro-isbn");
  const raw = isbnField.value;
  const digitsOnly = raw.replace(/[-\s]/g, "");

  if (!/^[\d\s-]+$/.test(raw)) {
    erroDiv.textContent = "O ISBN só pode conter números, espaços e hífens.";
    return false;
  }

  if (!(digitsOnly.length === 10 || digitsOnly.length === 13)) {
    erroDiv.textContent = "O ISBN deve ter exatamente 10 ou 13 dígitos.";
    return false;
  }

  erroDiv.textContent = "";
  return true;
}

  function validarFormularioLivro() {
    const tagsGenero = document.querySelectorAll('#genre-tag-wrapper .tag');
    const erroGenero = document.getElementById('erro-genero');

    if (tagsGenero.length === 0) {
      erroGenero.textContent = 'Por favor, adicione pelo menos um género.';
      
      setTimeout(() => {
        erroGenero.textContent = '';
      }, 3000);

      return false; 
    }

    erroGenero.textContent = ''; 
    return true;
  }