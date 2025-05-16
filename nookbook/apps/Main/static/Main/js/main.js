let index = 0;

function atualizarDiasSemana(progressoId) {
  const spans = document.querySelectorAll('#dias-semana span');
  const diasLidos = diasLidosPorProgresso[progressoId] || [];

  spans.forEach(span => {
    const dia = parseInt(span.dataset.day);
    if (diasLidos.includes(dia)) {
      span.classList.add('ativo');
    } else {
      span.classList.remove('ativo');
    }
  });
}

function moverCarrossel(direcao) {
  const track = document.getElementById("carousel-track");
  const slides = document.querySelectorAll(".livro-slide");
  const total = slides.length;

  if (total === 0) return;

  const cardWidth = slides[0].offsetWidth;

  index += direcao;
  if (index >= total) index = 0;
  if (index < 0) index = total - 1;

  localStorage.setItem('carouselIndex', index);
  track.style.transform = `translateX(-${index * cardWidth}px)`;

  atualizarFormularioEImagem(index);
}

function atualizarFormularioEImagem(indexAtual) {
  const slides = document.querySelectorAll(".livro-slide");
  const slide = slides[indexAtual];

  if (!slide) {
    console.warn("Slide não encontrado para o índice:", indexAtual);
    return;
  }

  const capa = slide.getAttribute("data-capa");
  const progressoId = slide.getAttribute("data-progresso-id");

  const inputProgresso = document.getElementById("progresso-id");
  const img = document.getElementById("capa-formulario");

  if (img && capa) img.src = capa;
  if (inputProgresso && progressoId) inputProgresso.value = progressoId;

  atualizarDiasSemana(progressoId);
}

document.addEventListener("DOMContentLoaded", () => {
  const track = document.getElementById("carousel-track");
  const slides = document.querySelectorAll(".livro-slide");
  const inputProgresso = document.getElementById('progresso-id');
  const capaFormulario = document.getElementById('capa-formulario');

  if (!track || slides.length === 0) return;

  // Restaurar índice com segurança
  let storedIndex = parseInt(localStorage.getItem('carouselIndex'));
  if (isNaN(storedIndex) || storedIndex < 0 || storedIndex >= slides.length) {
    storedIndex = 0;
  }
  index = storedIndex;

  window.requestAnimationFrame(() => {
    const cardWidth = slides[0].offsetWidth;
    if (cardWidth > 0) {
      track.style.transform = `translateX(-${index * cardWidth}px)`;
      atualizarFormularioEImagem(index);
    }
    document.body.classList.add("js-carregado");
  });

  // Configurar cliques nos slides
  slides.forEach(slide => {
    slide.addEventListener('click', () => {
      const progressoId = slide.dataset.progressoId;
      const capa = slide.dataset.capa;

      if (inputProgresso) inputProgresso.value = progressoId;
      if (capaFormulario && capa) capaFormulario.src = capa;

      atualizarDiasSemana(progressoId);
    });
  });

  // Inicializar com primeiro livro se necessário
  if (slides.length > 0 && inputProgresso && inputProgresso.value === '') {
    const first = slides[0];
    inputProgresso.value = first.dataset.progressoId;
    if (capaFormulario) capaFormulario.src = first.dataset.capa;
    atualizarDiasSemana(first.dataset.progressoId);
  }
});

// Inicializar barras de progresso
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.progress-bar').forEach(bar => {
    const valor = bar.dataset.percentagem;
    bar.style.width = valor + '%';
  });
});
