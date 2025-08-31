document.getElementById('formatarTabelaBtn').addEventListener('click', async () => {
  const dados = {
    professores,
    restricoes,
  };

    const resposta = await fetch("http://127.0.0.1:5000/formatar", {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  });

  const resultado = await response.json();
  console.log("Horários gerados:", resultado);
});