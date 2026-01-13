document.addEventListener('DOMContentLoaded', () => {
    console.log("--> JS Carregado! Procurando botão...");

    // 1. Pega os elementos da tela
    const selectSimulado = document.getElementById('filtro-simulado');
    const listaRanking = document.getElementById('lista-ranking-simulado');
    const rankingTitulo = document.getElementById('ranking-titulo');
    
    // ESTE É O CARA IMPORTANTE: O BOTÃO
    const btnVerRanking = document.getElementById('btn-ver-ranking');

    // Verifica se o botão foi encontrado
    if (btnVerRanking) {
        console.log("--> Botão ENCONTRADO! Adicionando função de clique.");
        
        // Adiciona a função ao clique do botão
        btnVerRanking.addEventListener('click', async () => {
            console.log("--> CLIQUE DETECTADO!");
            
            const simuladoId = selectSimulado.value;
            if (!simuladoId) {
                alert('Por favor, selecione um simulado.');
                return;
            }

            // Atualiza título e limpa lista
            const selectedOption = selectSimulado.options[selectSimulado.selectedIndex];
            rankingTitulo.textContent = `Ranking: ${selectedOption.dataset.nome}`;
            listaRanking.innerHTML = '<li>Carregando ranking...</li>';

            // Busca os dados no servidor
            try {
                const response = await fetch(`/api/simulados/${simuladoId}/ranking`);
                const ranking = await response.json();
                console.log("--> DADOS RECEBIDOS:", ranking);

                listaRanking.innerHTML = '';
                
                if (ranking.length === 0) {
                    listaRanking.innerHTML = '<li>Nenhuma nota lançada para este simulado ainda.</li>';
                } else {
                    ranking.forEach((item, index) => {
                        const li = document.createElement('li');
                        
                        // Cria o cabeçalho do item
                        const header = document.createElement('div');
                        header.className = 'ranking-item-header';
                        header.innerHTML = `<strong>${index + 1}. ${item.aluno_nome}</strong> - Nota: ${item.nota.toFixed(2)}`;
                        
                        li.appendChild(header);

                        // Se tiver tempos detalhados, adiciona a lógica de expandir
                        if (item.tempo_total_gasto || (item.tempos_por_materia && item.tempos_por_materia !== 'None')) {
                            header.style.cursor = 'pointer';
                            header.innerHTML += ' <span style="font-size:0.8em">▼</span>';

                            const details = document.createElement('div');
                            details.className = 'ranking-item-details';
                            details.style.display = 'none';
                            details.style.marginTop = '10px';
                            details.style.paddingLeft = '20px';
                            details.style.borderLeft = '2px solid var(--primary-green)';

                            let detailsHTML = '';
                            if (item.tempo_total_gasto) {
                                detailsHTML += `<p>Tempo Total: ${item.tempo_total_gasto} min</p>`;
                            }
                            if (item.tempos_por_materia && item.tempos_por_materia !== 'None') {
                                try {
                                    const jsonString = item.tempos_por_materia.replace(/'/g, '"');
                                    const tempos = JSON.parse(jsonString);
                                    detailsHTML += '<ul>';
                                    for (const [materia, tempo] of Object.entries(tempos)) {
                                        if(tempo) detailsHTML += `<li>${materia}: ${tempo} min</li>`;
                                    }
                                    detailsHTML += '</ul>';
                                } catch(e) { console.error("Erro parsing JSON", e); }
                            }
                            details.innerHTML = detailsHTML;
                            li.appendChild(details);

                            // Clique no item para expandir
                            li.addEventListener('click', () => {
                                details.style.display = details.style.display === 'none' ? 'block' : 'none';
                            });
                        }
                        listaRanking.appendChild(li);
                    });
                }
            } catch (error) {
                console.error('Erro ao buscar ranking:', error);
                listaRanking.innerHTML = '<li>Ocorreu um erro ao carregar o ranking.</li>';
            }
        });
    } else {
        console.error("--> ERRO CRÍTICO: O botão 'btn-ver-ranking' NÃO foi encontrado no HTML.");
    }

    // Função para carregar a lista de simulados no dropdown
    async function carregarSimulados() {
        try {
            const response = await fetch('/api/simulados');
            const simulados = await response.json();
            
            selectSimulado.innerHTML = '<option value="">Selecione o simulado</option>';
            if (simulados.length === 0) {
                 const option = document.createElement('option');
                 option.text = "Nenhum simulado cadastrado";
                 selectSimulado.appendChild(option);
            } else {
                simulados.forEach(simulado => {
                    const option = document.createElement('option');
                    option.value = simulado.id;
                    option.dataset.nome = simulado.nome_display; 
                    option.textContent = `${simulado.nome_display} - ${simulado.data}`;
                    selectSimulado.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Erro ao carregar simulados:', error);
        }
    }

    // Inicializa carregando a lista
    carregarSimulados();
});