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

  estantes.forEach(card => {
    card.addEventListener("click", function (e) {
      if (e.target.closest("form") || e.target.tagName === "BUTTON") return;

      const url = card.getAttribute("data-url");
      if (url) {
        window.location.href = url;
      }
    });
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
  
    const menuWidth = menu.offsetWidth;
    const spaceRight = window.innerWidth - rect.right;
  
    if (spaceRight < menuWidth) {
      menu.style.left = `${rect.left - menuWidth + 36}px`;
    } else {
      menu.style.left = `${rect.right - 200}px`;
    }
  
    menu.style.top = `${rect.top + window.scrollY + 35}px`;

    if (window.innerWidth <= 480) {
      const rect = button.getBoundingClientRect();
      menu.style.position = 'absolute';
      menu.style.top = `${window.scrollY + rect.bottom + 8}px`;  
      menu.style.left = `10px`;
      menu.style.right = `auto`;
      menu.style.display = 'flex';
    } 
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
