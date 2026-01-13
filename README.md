# Projeto Mentoria Odisseia - Painel de Desempenho 🚀

## Visão Geral

Esta aplicação web foi desenvolvida como uma ferramenta de **accountability e gamificação** para o grupo de estudos "Mentoria Odisseia", focado na preparação para concursos públicos (principalmente PMBA). O objetivo principal é centralizar o registro de desempenho dos alunos, promovendo a **constância, a análise individual e a competição saudável** dentro do grupo.

O projeto nasceu da necessidade de sair de métodos desorganizados (planilhas, grupos de WhatsApp) para um sistema centralizado que oferecesse métricas claras e rankings atualizados, servindo tanto para o acompanhamento individual quanto para a motivação coletiva.

## Funcionalidades Principais ✨

* **Registro de Desempenho (Questões):**
    * Permite que cada aluno registre diariamente a quantidade de questões resolvidas e o número de acertos.
    * Funcionalidade de apagar registros recentes para correção de erros.
* **Ranking Semanal (Questões):** 🏆
    * Exibe o Top 10 de quantidade de questões e percentual de acerto, considerando apenas os registros feitos desde o último domingo (00:00h).
    * Zera automaticamente toda semana para renovar a competição.
* **Histórico de Rankings:** 📊
    * **Ranking Geral (All-Time):** Mostra o ranking completo (quantidade e percentual) acumulado desde o início do uso da plataforma.
    * **Ranking da Semana Passada:** Exibe o resultado final da semana anterior (Domingo a Sábado) para consulta e registro.
* **Gerenciamento de Simulados:** 📝
    * Cadastro de Empresas aplicadoras (Rumo, Projeto Caveira, Quad, etc.).
    * Cadastro de Simulados específicos (com número/nome, categoria - Soldado/Oficial, data).
    * Lançamento de notas individuais dos alunos por simulado.
    * Funcionalidade de apagar notas lançadas incorretamente.
* **Ranking por Simulado:** 🎯
    * Página dedicada onde é possível selecionar um simulado específico e visualizar o ranking de notas daquele evento.
* **Consulta de Desempenho Individual:** 📈
    * Permite selecionar um aluno e um período de datas para visualizar o total de questões, acertos e percentual de acerto naquele intervalo.
    * Exibe um gráfico de linhas mostrando a evolução diária (questões vs % acerto) no período selecionado.
* **(Admin) Gerenciamento de Alunos:**
    * Adição de novos alunos ao sistema (via rota específica).
    * Renomeação de alunos (via rota específica).

## Stack Tecnológica 🛠️

* **Backend:** Python com Flask e Flask-SQLAlchemy
* **Banco de Dados:** PostgreSQL (hospedado no Render.com)
* **Frontend:** HTML5, CSS3 (puro), JavaScript (Vanilla JS)
* **Gráficos:** Chart.js
* **Hospedagem:** Render.com (PaaS)
* **Versionamento:** Git & GitHub

## Status do Projeto

Atualmente, a aplicação está **ativa e em uso** pelo grupo Mentoria Odisseia. Serve como uma ferramenta diária de acompanhamento e motivação.

---
