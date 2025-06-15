const livrosData = JSON.parse(document.getElementById('livrosData').textContent);
const canvas = document.getElementById('wheelCanvas');
const ctx = canvas.getContext('2d');
const numSectors = livrosData.length;
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const radius = 180;
let anguloInicial = 0;
let girando = false;

function girarRoda() {
  if (girando || livrosData.length === 0) return;
  girando = true;

  const sorteio = Math.floor(Math.random() * numSectors);
  const anglePerSector = 360 / numSectors;

  const degreesToStopAt = 270 - (sorteio * anglePerSector + anglePerSector / 2);

  const destinoFinal = 360 * 5 + ((degreesToStopAt + 360) % 360);

  let atual = 0;
  const velocidade = 10;

  const animacao = setInterval(() => {
    atual += velocidade;
    anguloInicial += (Math.PI / 180) * velocidade;
    desenharRoda();

    if (atual >= destinoFinal) {
      clearInterval(animacao);
      girando = false;
      const escolhido = livrosData[sorteio];
      document.getElementById('resultadoLivro').innerText =
        `Livro sorteado: ${escolhido.titulo}`;
    }
  }, 20);
}

desenharRoda();
function desenharRoda() {
  const anglePerSector = (2 * Math.PI) / numSectors;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < numSectors; i++) {
    const startAngle = anguloInicial + i * anglePerSector;
    const midAngle = startAngle + anglePerSector / 2;

    // Fundo do setor
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, startAngle, startAngle + anglePerSector);
    ctx.fillStyle = i % 2 === 0 ? "#f8d4d4" : "#eed9a4";
    ctx.fill();
    ctx.stroke();

    // Texto
    const titulo = livrosData[i].titulo;
    const textRadius = radius * 0.65;
    const maxTextWidth = (2 * Math.PI * textRadius / numSectors) * 0.65;

    // Fonte base
    let fontSize = 13;
    ctx.font = `bold ${fontSize}px Arial`;

    // --- Dividir em linhas ---
    const palavras = titulo.split(" ");
    const linhas = [];
    let linhaAtual = "";

    palavras.forEach(palavra => {
      const teste = linhaAtual ? linhaAtual + " " + palavra : palavra;
      if (ctx.measureText(teste).width < maxTextWidth) {
        linhaAtual = teste;
      } else {
        linhas.push(linhaAtual);
        linhaAtual = palavra;
      }
    });
    if (linhaAtual) linhas.push(linhaAtual);

    // Reduzir fonte se forem muitas linhas
    while (linhas.length > 3 && fontSize > 9) {
      fontSize -= 1;
      ctx.font = `bold ${fontSize}px Arial`;
      linhas.length = 0;
      linhaAtual = "";
      palavras.forEach(palavra => {
        const teste = linhaAtual ? linhaAtual + " " + palavra : palavra;
        if (ctx.measureText(teste).width < maxTextWidth) {
          linhaAtual = teste;
        } else {
          linhas.push(linhaAtual);
          linhaAtual = palavra;
        }
      });
      if (linhaAtual) linhas.push(linhaAtual);
    }

    // Desenhar texto
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(midAngle);
    ctx.translate(textRadius, 0);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#333";
    ctx.font = `bold ${fontSize}px Arial`;

    const lineHeight = fontSize + 2;
    const offsetY = -((linhas.length - 1) / 2) * lineHeight;

    linhas.forEach((linha, idx) => {
      ctx.fillText(linha, 0, offsetY + idx * lineHeight);
    });

    ctx.restore();
  }
}
