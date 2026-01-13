document.addEventListener('DOMContentLoaded', () => {
    const formConsulta = document.getElementById('form-consulta');
    const selectAluno = document.getElementById('consulta-aluno');
    const inputDataInicio = document.getElementById('consulta-data-inicio');
    const inputDataFim = document.getElementById('consulta-data-fim');
    const divResultado = document.getElementById('resultado-consulta');
    const resultadoTitulo = document.getElementById('resultado-titulo');
    
    // Pegando os dois canvas
    const canvasQuantidade = document.getElementById('graficoQuantidade');
    const canvasPercentual = document.getElementById('graficoPercentual');
    const graficosContainer = document.getElementById('graficos-container'); // Container dos gráficos
    
    // Variáveis para guardar as instâncias dos gráficos
    let graficoQuantidadeInstancia = null;
    let graficoPercentualInstancia = null;

    // Função para carregar alunos (sem alteração)
    async function carregarAlunos() {
        try {
            const response = await fetch('/api/alunos');
            const alunos = await response.json();
            selectAluno.innerHTML = '<option value="">Selecione o aluno</option>';
            alunos.forEach(aluno => {
                const option = document.createElement('option');
                option.value = aluno.id;
                option.textContent = aluno.nome;
                selectAluno.appendChild(option);
            });
        } catch (error) { console.error('Erro:', error); /* ... */ }
    }

    // Função para destruir gráficos existentes
    function destruirGraficos() {
        if (graficoQuantidadeInstancia) graficoQuantidadeInstancia.destroy();
        if (graficoPercentualInstancia) graficoPercentualInstancia.destroy();
        graficoQuantidadeInstancia = null;
        graficoPercentualInstancia = null;
        graficosContainer.style.height = '0px'; // Esconde a área dos gráficos
    }

    // Função para renderizar os DOIS gráficos
    function renderizarGraficos(dadosDiarios) {
        destruirGraficos(); // Garante que gráficos antigos sejam removidos
        graficosContainer.style.height = '400px'; // Mostra a área dos gráficos

        const labels = dadosDiarios.map(d => new Date(d.data + 'T00:00:00').toLocaleDateString('pt-BR'));
        const dadosQuestoes = dadosDiarios.map(d => d.questoes);
        const dadosPercentual = dadosDiarios.map(d => d.percentual);

        // --- Gráfico de Quantidade ---
        const ctxQuantidade = canvasQuantidade.getContext('2d');
        graficoQuantidadeInstancia = new Chart(ctxQuantidade, {
            type: 'bar', // Mudei para barras, fica bom para quantidade
            data: {
                labels: labels,
                datasets: [{
                    label: 'Questões Feitas',
                    data: dadosQuestoes,
                    backgroundColor: 'rgba(32, 201, 151, 0.6)', // Verde com transparência
                    borderColor: '#20c997',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } }, // Esconde legenda, já tem título
                scales: {
                    x: { ticks: { color: '#e0e0e0' }, grid: { color: '#333333' } },
                    y: { 
                        title: { display: true, text: 'Nº de Questões', color: '#e0e0e0' },
                        ticks: { color: '#e0e0e0', stepSize: 20 }, // Ajuste stepSize
                        beginAtZero: true, grid: { color: '#333333' }
                    }
                }
            }
        });

        // --- Gráfico de Percentual ---
        const ctxPercentual = canvasPercentual.getContext('2d');
        graficoPercentualInstancia = new Chart(ctxPercentual, {
            type: 'line', // Linha fica bom para percentual
            data: {
                labels: labels,
                datasets: [{
                    label: '% Acerto',
                    data: dadosPercentual,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.2)',
                    tension: 0.1,
                    pointBackgroundColor: '#dc3545', pointRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } }, // Esconde legenda
                scales: {
                    x: { ticks: { color: '#e0e0e0' }, grid: { color: '#333333' } },
                    y: { 
                        title: { display: true, text: '% Acerto', color: '#e0e0e0' },
                        ticks: { color: '#e0e0e0', stepSize: 10 },
                        min: 0, max: 100, grid: { color: '#333333' }
                    }
                }
            }
        });
    }

    // Lógica do formulário de consulta (modificada)
    formConsulta.addEventListener('submit', async (event) => {
        event.preventDefault();
        const alunoId = selectAluno.value;
        const dataInicio = inputDataInicio.value;
        const dataFim = inputDataFim.value;

        // ... (validações como antes) ...
        if (!alunoId || !dataInicio || !dataFim) { alert('Preencha tudo.'); return; }
        if (new Date(dataFim) < new Date(dataInicio)) { alert('Data fim < início.'); return; }

        resultadoTitulo.textContent = 'Resultado da Consulta';
        divResultado.innerHTML = '<p>Consultando...</p>';
        destruirGraficos(); // Limpa gráficos anteriores

        try {
            const url = `/api/consulta/desempenho?aluno_id=${alunoId}&inicio=${dataInicio}&fim=${dataFim}`;
            const response = await fetch(url);
            const data = await response.json();

            if (response.ok) {
                const dataInicioFormatada = new Date(dataInicio + 'T00:00:00').toLocaleDateString('pt-BR');
                const dataFimFormatada = new Date(dataFim + 'T00:00:00').toLocaleDateString('pt-BR');
                
                resultadoTitulo.textContent = `Resultado para ${data.aluno_nome}`;
                divResultado.innerHTML = `
                    <p><strong>Período:</strong> ${dataInicioFormatada} até ${dataFimFormatada}</p>
                    <p><strong>Total de Questões Feitas:</strong> ${data.total_questoes}</p>
                    <p><strong>Total de Acertos:</strong> ${data.total_acertos}</p>
                    <p><strong>Percentual de Acerto (Total):</strong> ${data.percentual_total}%</p>
                `;

                if (data.dados_diarios && data.dados_diarios.length > 0) {
                    renderizarGraficos(data.dados_diarios);
                } else {
                    divResultado.innerHTML += '<p>Nenhum dado encontrado neste período para gerar os gráficos.</p>';
                }

            } else { divResultado.innerHTML = `<p>Erro: ${data.erro}</p>`; }
        } catch (error) {
            console.error('Erro:', error);
            divResultado.innerHTML = '<p>Erro de comunicação.</p>';
        }
    });

    carregarAlunos(); // Carrega alunos ao iniciar
});