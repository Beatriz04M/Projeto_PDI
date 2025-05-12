document.addEventListener('DOMContentLoaded', function () {
  setupTagInput('autor-input', 'autores-wrapper', 'autores-hidden');
  setupTagInput('keyword-input', 'keywords-wrapper', 'keywords-hidden');
  initGenreSuggestions();
  initPreviewHandlers();
  initISBNValidation();
  setupFormValidation();
  setupMensagemTimeout();
});

function setupMensagemTimeout() {
  setTimeout(() => {
    const mensagens = document.querySelector('.mensagens');
    if (mensagens) {
      mensagens.style.transition = 'opacity 0.5s ease-out';
      mensagens.style.opacity = '0';
      setTimeout(() => mensagens.remove(), 500);
    }
  }, 3000);
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
    const numberRegex = /\d/;
    const onlyNumberRegex = /^\d+$/;

    if (numberRegex.test(titulo)) {
      alert("O título não pode conter números.");
      e.preventDefault();
    }

    if (numberRegex.test(autores)) {
      alert("O nome do autor não pode conter números.");
      e.preventDefault();
    }

    if (numPag <= 0 || !onlyNumberRegex.test(numPag)) {
      alert("Número de páginas inválido.");
      e.preventDefault();
    }

    if (ano && (ano <= 0 || ano > currentYear)) {
      alert(`Ano de publicação inválido. Deve ser entre 1 e ${currentYear}.`);
      e.preventDefault();
    }
  });
}

function setupTagInput(inputId, wrapperId, hiddenId) {
  const input = document.getElementById(inputId);
  const wrapper = document.getElementById(wrapperId);
  const hiddenInput = document.getElementById(hiddenId);
  if (!input || !wrapper || !hiddenInput) return; // ← Proteção contra elementos inexistentes

  let tags = [];

  function updateHiddenInput() {
    hiddenInput.value = tags.join(',');
  }

  function updatePlaceholder() {
    input.placeholder = tags.length > 0 ? '' :
      (inputId === 'autor-input' ? 'Autores (ex: João, Maria)' : 'Palavras-chave (ex: mistério, futebol)');
  }

  function createTag(text) {
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = text;

    const removeBtn = document.createElement('span');
    removeBtn.className = 'remove-tag';
    removeBtn.textContent = '×';
    removeBtn.onclick = () => {
      tags = tags.filter(t => t !== text);
      wrapper.removeChild(tag);
      updateHiddenInput();
      updatePlaceholder();
    };

    tag.appendChild(removeBtn);
    wrapper.insertBefore(tag, input);
  }

  input.addEventListener('keydown', function (e) {
    if (e.key === ',' || e.key === 'Enter') {
      e.preventDefault();
      const value = input.value.trim().replace(/,$/, '');
      if (value && !tags.includes(value)) {
        tags.push(value);
        createTag(value);
        updateHiddenInput();
        updatePlaceholder();
      }
      input.value = '';
    }
  });
}

function initISBNValidation() {
  const isbnInput = document.getElementById("isbn");
  const erroBox = document.getElementById("erro-isbn");

  if (!isbnInput || !erroBox) return;

  isbnInput.addEventListener("input", function () {
    const valor = isbnInput.value.replace(/[-\\s]/g, "");
    if (!/^\\d{10}(\\d{3})?$/.test(valor)) {
      erroBox.textContent = "Formato inválido de ISBN. Use 10 ou 13 dígitos.";
      erroBox.style.color = "red";
    } else {
      erroBox.textContent = "";
    }
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

      genreWrapper.appendChild(tag);
      genreInput.value = "";
      genreSuggestions.innerHTML = "";
      genreSuggestions.style.display = "none";
    }
  }

  function removeGenreTag(genre, tag) {
    selectedGenres = selectedGenres.filter(item => item !== genre);
    genreWrapper.removeChild(tag);
    filterGenreSuggestions();
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
