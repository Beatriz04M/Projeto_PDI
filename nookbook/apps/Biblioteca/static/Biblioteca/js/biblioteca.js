// Autoesconde mensagens após 3s
document.addEventListener("DOMContentLoaded", () => {
    const mensagens = document.querySelector(".mensagens");
    if (mensagens) {
      setTimeout(() => {
        mensagens.style.transition = "opacity 0.5s ease-out";
        mensagens.style.opacity = "0";
        setTimeout(() => mensagens.remove(), 500);
      }, 3000);
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    const estantes = document.querySelectorAll(".estante-card");
  
    estantes.forEach(card => {
      const cor = card.getAttribute("data-cor");
      if (cor) {
        card.style.backgroundColor = cor;
      }
    });
  });
  
  
  function abrirModalEstante() {
    document.getElementById("modal-estante").style.display = "flex";
  }
  function fecharModalEstante() {
    document.getElementById("modal-estante").style.display = "none";
  }
  
  // Fechar ao clicar fora
  window.onclick = function(event) {
    const modal = document.getElementById("modal-estante");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    // Garante que todos os dropdowns começam escondidos
    document.querySelectorAll(".dropdown-menu.global").forEach(menu => {
      menu.style.display = "none";
    });
  });
  
  // Fecha dropdowns ao clicar fora
  document.addEventListener("click", function (event) {
    document.querySelectorAll(".dropdown-menu.global").forEach(menu => {
      const isButton = menu.dataset.btnId && document.getElementById(menu.dataset.btnId);
      if (
        !menu.contains(event.target) &&
        !(isButton && isButton.contains(event.target))
      ) {
        menu.style.display = "none";
      }
    });
  });
  
  // Função para abrir o dropdown
  function toggleMenu(estanteId, event) {
    event.stopPropagation();
  
    const menu = document.getElementById(`menu-${estanteId}`);
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const isVisible = menu.style.display === 'flex';
    
    // Fecha todos antes
    document.querySelectorAll('.dropdown-menu.global').forEach(m => m.style.display = 'none');
    if (isVisible) return;
  
    menu.style.display = 'flex';
  
    // Verifica se é mobile
    if (window.innerWidth <= 600) {
      // Com CSS já controlamos o posicionamento
      menu.style.left = '50%';
      menu.style.top = '50%';
      menu.style.transform = 'translate(-50%, -50%)';
      return;
    }
  
    // Posicionamento normal (desktop)
    const menuWidth = menu.offsetWidth;
    const spaceRight = window.innerWidth - rect.right;
  
    if (spaceRight < menuWidth) {
      menu.style.left = `${rect.left - menuWidth}px`;
    } else {
      menu.style.left = `${rect.right}px`;
    }
  
    menu.style.top = `${rect.top + window.scrollY + 10}px`;
  }
  
  
  function fecharMenu(id) {
    const menu = document.getElementById(`menu-${id}`);
    if (menu) menu.style.display = "none";
  }
    

function toggleForm(estanteId) {
  const form = document.getElementById("form-" + estanteId);
  form.style.display = form.style.display === "none" ? "block" : "none";
}

function abrirConfirmacao(estanteId) {
  const modal = document.getElementById(`modal-confirmar-${estanteId}`);
  if (modal) {
    modal.style.display = 'flex';
  }
}

function fecharConfirmacao(estanteId) {
  const modal = document.getElementById(`modal-confirmar-${estanteId}`);
  if (modal) {
    modal.style.display = 'none';
  }
}
z