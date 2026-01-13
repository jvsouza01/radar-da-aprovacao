document.addEventListener('DOMContentLoaded', () => {
    // Displays de tempo
    const displayGeral = document.getElementById('cronometro-geral');
    const displayMateria = document.getElementById('cronometro-materia');

    // Botões
    const gridMaterias = document.getElementById('grid-materias');
    const btnPausa = document.getElementById('btn-pausa');
    const btnFinalizar = document.getElementById('btn-finalizar');
    const btnSalvar = document.getElementById('btn-salvar');
    
    // Seção de finalização
    const finalizarSecao = document.getElementById('finalizar-secao');
    const tempoFinalDisplay = document.getElementById('tempo-final-display');
    const alunoSelect = document.getElementById('aluno-select');
    
    // Variáveis de estado do cronômetro
    let timerGeralIntervalo = null;
    let timerMateriaIntervalo = null;
    let tempoTotalSegundos = 0;
    let tempoMateriaSegundos = 0;
    let materiaAtual = null;
    let isPausado = false;
    
    // Objeto para armazenar os tempos "lap" de cada matéria
    const temposPorMateria = {}; // Ex: { "Português": 1800, "Direito": 3600 }

    // --- FUNÇÕES DO CRONÔMETRO ---

    function formatarTempo(segundos) {
        const h = Math.floor(segundos / 3600).toString().padStart(2, '0');
        const m = Math.floor((segundos % 3600) / 60).toString().padStart(2, '0');
        const s = (segundos % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    function iniciarTimerGeral() {
        if (timerGeralIntervalo) return; // Já está rodando
        timerGeralIntervalo = setInterval(() => {
            if (!isPausado) {
                tempoTotalSegundos++;
                displayGeral.textContent = formatarTempo(tempoTotalSegundos);
            }
        }, 1000);
    }

    function iniciarTimerMateria() {
        pararTimerMateria(); // Para o anterior
        timerMateriaIntervalo = setInterval(() => {
            if (!isPausado) {
                tempoMateriaSegundos++;
                displayMateria.textContent = formatarTempo(tempoMateriaSegundos);
            }
        }, 1000);
    }

    function pararTimerMateria() {
        clearInterval(timerMateriaIntervalo);
        timerMateriaIntervalo = null;
        tempoMateriaSegundos = 0;
    }
    
    function salvarTempoMateriaAtual() {
        if (materiaAtual) {
            // Adiciona o tempo ao total daquela matéria
            const tempoAnterior = temposPorMateria[materiaAtual] || 0;
            temposPorMateria[materiaAtual] = tempoAnterior + tempoMateriaSegundos;
        }
    }

    // --- LÓGICA DOS BOTÕES ---

    // Clicar em um botão de Matéria
    gridMaterias.addEventListener('click', (e) => {
        if (e.target.classList.contains('materia-btn')) {
            if (isPausado) {
                 alert('Retome o simulado antes de trocar de matéria.');
                 return;
            }
            
            const proximaMateria = e.target.dataset.materia;
            
            // Salva o tempo da matéria anterior
            salvarTempoMateriaAtual();
            
            // Reseta o timer da matéria e inicia o novo
            pararTimerMateria();
            displayMateria.textContent = '00:00:00';
            
            if (proximaMateria !== materiaAtual) {
                materiaAtual = proximaMateria;
                iniciarTimerMateria();
                
                // Atualiza destaque visual
                document.querySelectorAll('.materia-btn').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
            } else {
                // Se clicou na mesma matéria, para (como um 'pause' só da matéria)
                materiaAtual = null;
                 document.querySelectorAll('.materia-btn').forEach(btn => btn.classList.remove('active'));
            }
            
            // Garante que o timer geral esteja rodando
            iniciarTimerGeral();
        }
    });

    // Clicar em Pausar/Retomar
    btnPausa.addEventListener('click', () => {
        isPausado = !isPausado;
        if (isPausado) {
            btnPausa.textContent = 'Retomar ▶️';
            btnPausa.style.backgroundColor = 'var(--primary-green)';
        } else {
            btnPausa.textContent = 'Pausar ⏸';
            btnPausa.style.backgroundColor = '#ffc107';
        }
    });

    // Clicar em Finalizar
    btnFinalizar.addEventListener('click', () => {
        if (!confirm('Tem certeza que deseja finalizar o simulado?')) return;
        
        // Para tudo
        isPausado = true;
        clearInterval(timerGeralIntervalo);
        salvarTempoMateriaAtual(); // Salva a última matéria cronometrada
        pararTimerMateria();
        
        // Esconde os botões e mostra a seção de salvar
        gridMaterias.style.display = 'none';
        btnPausa.style.display = 'none';
        btnFinalizar.style.display = 'none';
        displayMateria.parentElement.style.display = 'none'; // Esconde display da matéria
        
        finalizarSecao.style.display = 'block';
        tempoFinalDisplay.textContent = formatarTempo(tempoTotalSegundos);
        
        // Carrega os alunos no dropdown
        carregarAlunos();
    });

    // Carregar Alunos para o dropdown final
    async function carregarAlunos() {
        try {
            const response = await fetch('/api/alunos');
            const alunos = await response.json();
            alunoSelect.innerHTML = '<option value="">Selecione o aluno</option>';
            alunos.forEach(aluno => {
                const option = document.createElement('option');
                option.value = aluno.id;
                option.textContent = aluno.nome;
                alunoSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Erro ao carregar alunos:', error);
        }
    }

    // Clicar em Salvar
    btnSalvar.addEventListener('click', async () => {
        const aluno_id = alunoSelect.value;
        if (!aluno_id) {
            alert('Por favor, selecione seu nome para salvar.');
            return;
        }

        const dadosParaSalvar = {
            aluno_id: parseInt(aluno_id),
            simulado_id: SIMULADO_ID, // Constante global pega do HTML
            tempo_total_gasto: tempoTotalSegundos,
            tempos_por_materia: temposPorMateria
        };

        try {
            const response = await fetch('/api/salvar-tempos-simulado', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dadosParaSalvar)
            });
            const result = await response.json();

            if (response.ok) {
                alert('Tempos salvos com sucesso! Você será redirecionado.');
                // Redireciona para a página de rankings de simulados
                window.location.href = '/ranking-simulados';
            } else {
                alert(`Erro ao salvar: ${result.mensagem}`);
            }
        } catch (error) {
            console.error('Erro ao salvar tempos:', error);
            alert('Erro de comunicação com o servidor.');
        }
    });
});