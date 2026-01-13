document.addEventListener('DOMContentLoaded', () => {
    const alunoSelect = document.getElementById('aluno-select');
    const registroForm = document.getElementById('registro-form');
    const ultimosLancamentosList = document.getElementById('ultimos-lancamentos');

    // Função para buscar a lista de alunos da nossa API
    async function carregarAlunos() {
        try {
            const response = await fetch('/api/alunos');
            const alunos = await response.json();
            alunoSelect.innerHTML = '<option value="">Selecione um aluno</option>';
            alunos.forEach(aluno => {
                const option = document.createElement('option');
                option.value = aluno.id;
                option.textContent = aluno.nome;
                alunoSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Erro ao carregar alunos:', error);
            alunoSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    // Função para carregar os últimos lançamentos de questões
    async function carregarUltimosLancamentos() {
        try {
            const response = await fetch('/api/registros/recentes');
            const registros = await response.json();
            ultimosLancamentosList.innerHTML = ''; // Limpa a lista

            if (registros.length === 0) {
                 ultimosLancamentosList.innerHTML = '<li>Nenhum registro recente.</li>';
            } else {
                registros.forEach(r => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <span>${r.aluno_nome}: ${r.acertos} acertos de ${r.questoes} questões</span>
                        <button class="delete-btn" data-id="${r.id}">Apagar</button>
                    `;
                    ultimosLancamentosList.appendChild(li);
                });
            }
        } catch (error) {
            console.error('Erro ao carregar últimos lançamentos:', error);
             ultimosLancamentosList.innerHTML = '<li>Erro ao carregar lançamentos.</li>';
        }
    }

    // Função para lidar com o envio do formulário de registro
    registroForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(registroForm);
        const dados = {
            aluno_id: formData.get('aluno_id'),
            quantidade: formData.get('quantidade'),
            acertos: formData.get('acertos')
        };
        // Validação simples
        if (!dados.aluno_id) {
             alert('Selecione um aluno.');
             return;
        }
        if (parseInt(dados.acertos) > parseInt(dados.quantidade)) {
            alert('O número de acertos não pode ser maior que a quantidade de questões.');
            return;
        }
        try {
            const response = await fetch('/api/registros', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
            if (response.ok) {
                registroForm.reset(); // Limpa o formulário
                // Define o select de aluno de volta para a opção padrão
                alunoSelect.value = "";
                await carregarUltimosLancamentos(); // Atualiza a lista de lançamentos
                alert('Registro adicionado com sucesso!');
            } else {
                 const result = await response.json().catch(() => ({})); // Tenta pegar erro do backend
                 alert(`Falha ao salvar o registro. ${result.mensagem || ''}`);
            }
        } catch (error) {
            console.error('Erro ao enviar registro:', error);
             alert('Erro de comunicação ao salvar registro.');
        }
    });

    // Lógica para escutar cliques nos botões de apagar na lista de últimos lançamentos
    ultimosLancamentosList.addEventListener('click', async (event) => {
        if (event.target.classList.contains('delete-btn')) {
            const registroId = event.target.dataset.id;
            if (confirm('Tem certeza que deseja apagar este registro?')) {
                try {
                    const response = await fetch(`/api/registros/${registroId}`, {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        await carregarUltimosLancamentos(); // Se apagou, recarrega a lista
                    } else {
                        alert('Falha ao apagar o registro.');
                    }
                } catch (error) {
                    console.error('Erro ao apagar registro:', error);
                     alert('Erro de comunicação ao apagar registro.');
                }
            }
        }
    });

    // Carrega os dados iniciais quando a página é aberta
    carregarAlunos();
    carregarUltimosLancamentos();
});