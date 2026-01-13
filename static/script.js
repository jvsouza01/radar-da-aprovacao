document.addEventListener('DOMContentLoaded', () => {
    // Função para buscar os dados dos rankings DA SEMANA e exibi-los
    async function carregarRankings() {
        try {
            const response = await fetch('/api/rankings');
            if (!response.ok) { // Verifica se a API respondeu com sucesso
                 throw new Error(`HTTP error! status: ${response.status}`);
            }
            const rankings = await response.json(); // Ex: { quantidade: [...], percentual: [...] }

            // --- Lógica para Ranking de Quantidade ---
            const rankingQtdList = document.getElementById('ranking-quantidade');
            // Limpa o pódio de Quantidade (Define valores padrão)
            ['1', '2', '3'].forEach(rank => {
                const nameEl = document.getElementById(`podium-qtd-${rank}-name`);
                const scoreEl = document.getElementById(`podium-qtd-${rank}-score`);
                if (nameEl) nameEl.textContent = '---';
                // Adapta o texto padrão do score conforme necessário
                if (scoreEl) scoreEl.textContent = '--- Qtd';
            });
            rankingQtdList.innerHTML = ''; // Limpa a lista de demais colocações

            if (rankings.quantidade && rankings.quantidade.length > 0) {
                const top3Qtd = rankings.quantidade.slice(0, 3);
                const restoQtd = rankings.quantidade.slice(3);

                // Preenche o pódio de Quantidade
                top3Qtd.forEach((item, index) => {
                    const rank = index + 1;
                    const nameEl = document.getElementById(`podium-qtd-${rank}-name`);
                    const scoreEl = document.getElementById(`podium-qtd-${rank}-score`);
                    if (nameEl) nameEl.textContent = item.nome;
                    if (scoreEl) scoreEl.textContent = `${item.total} questões`;
                });

                // Preenche a lista do restante (4º em diante)
                if (restoQtd.length > 0) {
                    restoQtd.forEach((item, index) => {
                        const li = document.createElement('li');
                        // Garante que o número está correto (index do slice(3) + 4)
                        li.textContent = `${index + 4}. ${item.nome} - ${item.total} questões`;
                        rankingQtdList.appendChild(li);
                    });
                } else if (top3Qtd.length >= 1) { // Mudança aqui para verificar se há pelo menos 1 no pódio
                     // Se tem top 1, 2 ou 3 mas não tem mais ninguém
                     // rankingQtdList.innerHTML = '<li>-- Fim da lista --</li>'; // Opcional
                }

            } else {
                rankingQtdList.innerHTML = '<li>Nenhum registro encontrado para esta semana ainda.</li>';
            }

            // --- Lógica para Ranking de Percentual --- (Similar à de Quantidade)
            const rankingPercList = document.getElementById('ranking-percentual');
             // Limpa o pódio de Percentual
            ['1', '2', '3'].forEach(rank => {
                const nameEl = document.getElementById(`podium-perc-${rank}-name`);
                const scoreEl = document.getElementById(`podium-perc-${rank}-score`);
                if (nameEl) nameEl.textContent = '---';
                if (scoreEl) scoreEl.textContent = '--- %';
            });
            rankingPercList.innerHTML = ''; // Limpa a lista

            if (rankings.percentual && rankings.percentual.length > 0) {
                const top3Perc = rankings.percentual.slice(0, 3);
                const restoPerc = rankings.percentual.slice(3);

                // Preenche o pódio de Percentual
                top3Perc.forEach((item, index) => {
                    const rank = index + 1;
                    const nameEl = document.getElementById(`podium-perc-${rank}-name`);
                    const scoreEl = document.getElementById(`podium-perc-${rank}-score`);
                    if (nameEl) nameEl.textContent = item.nome;
                    if (scoreEl) scoreEl.textContent = `${parseFloat(item.percentual).toFixed(2)}%`;
                });

                // Preenche a lista do restante (4º em diante)
                 if (restoPerc.length > 0) {
                    restoPerc.forEach((item, index) => {
                        const li = document.createElement('li');
                        li.textContent = `${index + 4}. ${item.nome} - ${parseFloat(item.percentual).toFixed(2)}%`;
                        rankingPercList.appendChild(li);
                    });
                 } else if (top3Perc.length >= 1) { // Mudança aqui
                     // rankingPercList.innerHTML = '<li>-- Fim da lista --</li>'; // Opcional
                 }

            } else {
                rankingPercList.innerHTML = '<li>Nenhum registro encontrado para esta semana ainda (ou mínimo não atingido).</li>';
            }

        } catch (error) {
            console.error('Erro ao carregar rankings:', error);
            // Limpa tudo em caso de erro para evitar dados inconsistentes
             document.getElementById('ranking-quantidade').innerHTML = '<li>Erro ao carregar ranking.</li>';
             document.getElementById('ranking-percentual').innerHTML = '<li>Erro ao carregar ranking.</li>';
             // Limpar pódios também se desejar (opcional, pode deixar o '---')
        }
    }

    // Carrega os rankings ao abrir a página
    carregarRankings();
});