document.addEventListener('DOMContentLoaded', async () => {
    
    // Variável para guardar o título original da página
    let tituloOriginal = document.title;
    let nomeArquivoPDF = "Ranking_Semana_Passada";

    async function carregarRanking() {
        try {
            const response = await fetch('/api/rankings/semana-passada');
            const data = await response.json();

            // --- 1. Atualizar Datas e Título ---
            if (data.periodo) {
                // Atualiza o texto na tela
                const textoPeriodo = `Período: ${data.periodo.inicio} até ${data.periodo.fim}`;
                document.getElementById('periodo-texto').innerText = textoPeriodo;

                // Prepara o nome do arquivo para o PDF (Substitui barras por traços)
                // Ex: Ranking_01-12-2025_a_07-12-2025
                const inicioLimpo = data.periodo.inicio.replace(/\//g, '-');
                const fimLimpo = data.periodo.fim.replace(/\//g, '-');
                nomeArquivoPDF = `Ranking_${inicioLimpo}_a_${fimLimpo}`;
            }

            // --- 2. Preencher Batalha de Times ---
            if (data.batalha) {
                const alphaDiv = document.getElementById('bat-alpha-qtd').parentElement;
                alphaDiv.classList.add('text-alpha');
                const omegaDiv = document.getElementById('bat-omega-qtd').parentElement;
                omegaDiv.classList.add('text-omega');

                document.getElementById('bat-alpha-qtd').innerText = data.batalha.Alpha.questoes;
                document.getElementById('bat-alpha-perc').innerText = data.batalha.Alpha.precisao + '%';
                document.getElementById('bat-omega-qtd').innerText = data.batalha.Omega.questoes;
                document.getElementById('bat-omega-perc').innerText = data.batalha.Omega.precisao + '%';
                document.getElementById('bat-vencedor').innerText = data.batalha.vencedor;
            }

            // --- 3. Preencher Pódios e Listas ---
            preencherPodio('qtd-passada', data.quantidade, 'Questões', 'total');
            preencherPodio('perc-passada', data.percentual, '%', 'percentual');
            preencherLista('ranking-quantidade-passada-lista', data.quantidade, 'Questões', 'total');
            preencherLista('ranking-percentual-passada-lista', data.percentual, '%', 'percentual');

        } catch (error) {
            console.error("Erro ao carregar ranking:", error);
        }
    }

    function preencherPodio(prefixo, lista, unidade, campoValor) {
        [1, 2, 3].forEach(i => {
            const elName = document.getElementById(`podium-${prefixo}-${i}-name`);
            const elScore = document.getElementById(`podium-${prefixo}-${i}-score`);
            if(elName) elName.innerText = '---';
            if(elScore) elScore.innerText = `--- ${unidade}`;
        });
        lista.slice(0, 3).forEach((p, index) => {
            const i = index + 1;
            const elName = document.getElementById(`podium-${prefixo}-${i}-name`);
            const elScore = document.getElementById(`podium-${prefixo}-${i}-score`);
            let val = p[campoValor];
            if(unidade === '%') val = parseFloat(val).toFixed(2);
            if(elName) elName.innerText = p.nome;
            if(elScore) elScore.innerText = `${val} ${unidade}`;
        });
    }

    function preencherLista(elementId, lista, unidade, campoValor) {
        const ol = document.getElementById(elementId);
        ol.innerHTML = '';
        for (let i = 3; i < lista.length; i++) {
            const item = lista[i];
            let valor = item[campoValor];
            if(unidade === '%') valor = parseFloat(valor).toFixed(2);
            const li = document.createElement('li');
            li.innerHTML = `<span>${i + 1}. ${item.nome}</span><strong>${valor} ${unidade}</strong>`;
            ol.appendChild(li);
        }
    }

    // --- LÓGICA DO BOTÃO PDF ---
    const btnPdf = document.getElementById('btn-pdf-semana-passada');
    if (btnPdf) {
        btnPdf.addEventListener('click', () => {
            // 1. Muda o título da página (isso define o nome do arquivo PDF)
            document.title = nomeArquivoPDF;
            
            // 2. Abre a impressão
            window.print();

            // 3. (Opcional) Retorna o título original depois de um tempinho
            setTimeout(() => {
                document.title = tituloOriginal;
            }, 1000);
        });
    }

    carregarRanking();
});