document.addEventListener("DOMContentLoaded", function () {
  // --- Tabs ---
  const tabs = document.querySelectorAll(".tab");
  const contents = document.querySelectorAll(".tab-content");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      contents.forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById(tab.dataset.tab).classList.add("active");
    });
  });

  // --- Confirmação de saída de desafio ---
  document.querySelectorAll('.form-participar').forEach(form => {
    const button = form.querySelector('button');
    form.addEventListener('submit', function (e) {
      if (button.dataset.participando === 'true') {
        const confirmar = confirm("Já estás a participar neste desafio.\nTem a certeza que quer desistir?");
        if (!confirmar) {
          e.preventDefault();
        }
      }
    });
  });
});
