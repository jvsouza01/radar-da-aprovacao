document.addEventListener('DOMContentLoaded', () => {
    // Seletores para os elementos do ranking
    const rankingQtdGeralLista = document.getElementById('ranking-quantidade-geral-lista');
    const rankingPercGeralLista = document.getElementById('ranking-percentual-geral-lista');

    // Função para buscar o ranking GERAL (All-Time) e preencher o HTML
    async function carregarRankingGeral() {
        try {
            const response = await fetch('/api/rankings/geral');
            const rankings = await response.json();

            // --- Lógica para Ranking de Quantidade ---
            // Limpa o pódio de Quantidade (Define valores padrão)
            ['1', '2', '3'].forEach(rank => {
                const nameEl = document.getElementById(`podium-qtd-geral-${rank}-name`);
                const scoreEl = document.getElementById(`podium-qtd-geral-${rank}-score`);
                if (nameEl) nameEl.textContent = '---';
                if (scoreEl) scoreEl.textContent = '--- Questões';
            });
            rankingQtdGeralLista.innerHTML = ''; // Limpa a lista de demais colocações

            if (rankings.quantidade && rankings.quantidade.length > 0) {
                const top3Qtd = rankings.quantidade.slice(0, 3);
                const restoQtd = rankings.quantidade.slice(3);

                // Preenche o pódio de Quantidade
                top3Qtd.forEach((item, index) => {
                    const rank = index + 1;
                    const nameEl = document.getElementById(`podium-qtd-geral-${rank}-name`);
                    const scoreEl = document.getElementById(`podium-qtd-geral-${rank}-score`);
                    if (nameEl) nameEl.textContent = item.nome;
                    if (scoreEl) scoreEl.textContent = `${item.total} Questões`;
                });

                // Preenche a lista do restante (4º em diante)
                if (restoQtd.length > 0) {
                    restoQtd.forEach((item, index) => {
                        const li = document.createElement('li');
                        li.textContent = `${index + 4}. ${item.nome} - ${item.total} questões`;
                        rankingQtdGeralLista.appendChild(li);
                    });
                } else if (top3Qtd.length >= 1) {
                    // Opcional: rankingQtdGeralLista.innerHTML = '<li>-- Fim da lista --</li>';
                }
            } else {
                rankingQtdGeralLista.innerHTML = '<li>Nenhum registro encontrado ainda.</li>';
            }

            // --- Lógica para Ranking de Percentual ---
            // Limpa o pódio de Percentual
            ['1', '2', '3'].forEach(rank => {
                const nameEl = document.getElementById(`podium-perc-geral-${rank}-name`);
                const scoreEl = document.getElementById(`podium-perc-geral-${rank}-score`);
                if (nameEl) nameEl.textContent = '---';
                if (scoreEl) scoreEl.textContent = '--- %';
            });
            rankingPercGeralLista.innerHTML = ''; // Limpa a lista

            if (rankings.percentual && rankings.percentual.length > 0) {
                const top3Perc = rankings.percentual.slice(0, 3);
                const restoPerc = rankings.percentual.slice(3);

                // Preenche o pódio de Percentual
                top3Perc.forEach((item, index) => {
                    const rank = index + 1;
                    const nameEl = document.getElementById(`podium-perc-geral-${rank}-name`);
                    const scoreEl = document.getElementById(`podium-perc-geral-${rank}-score`);
                    if (nameEl) nameEl.textContent = item.nome;
                    if (scoreEl) scoreEl.textContent = `${parseFloat(item.percentual).toFixed(2)}%`;
                });

                // Preenche a lista do restante (4º em diante)
                if (restoPerc.length > 0) {
                    restoPerc.forEach((item, index) => {
                        const li = document.createElement('li');
                        li.textContent = `${index + 4}. ${item.nome} - ${parseFloat(item.percentual).toFixed(2)}%`;
                        rankingPercGeralLista.appendChild(li);
                    });
                } else if (top3Perc.length >= 1) {
                    // Opcional: rankingPercGeralLista.innerHTML = '<li>-- Fim da lista --</li>';
                }
            } else {
                rankingPercGeralLista.innerHTML = '<li>Nenhum registro encontrado ainda (ou mínimo não atingido).</li>';
            }

        } catch (error) {
            console.error('Erro ao carregar ranking geral:', error);
            rankingQtdGeralLista.innerHTML = '<li>Erro ao carregar ranking.</li>';
            rankingPercGeralLista.innerHTML = '<li>Erro ao carregar ranking.</li>';
        }
    }
    
    carregarRankingGeral(); // Carrega o ranking ao abrir a página
});