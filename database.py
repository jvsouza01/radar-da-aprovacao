import sqlite3

# Função para criar a conexão com o banco de dados
def conectar():
    """Conecta ao banco de dados SQLite e retorna o objeto de conexão e o cursor."""
    conn = sqlite3.connect('mentoria.db')
    return conn

# Função para criar as tabelas iniciais
def criar_tabelas(conn):
    """Cria as tabelas 'alunos' e 'registros_questoes' se elas não existirem."""
    cursor = conn.cursor()
    
    # Criar a tabela de alunos
    # O id será a chave primária que se auto-incrementa
    # O nome será um texto, que não pode ser nulo e deve ser único
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Criar a tabela de registros de questões
    # O 'aluno_id' será uma chave estrangeira, ligando este registro a um aluno
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros_questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            quantidade_questoes INTEGER NOT NULL,
            acertos INTEGER NOT NULL,
            data_registro TEXT NOT NULL,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
        )
    ''')
    
    print("Tabelas 'alunos' e 'registros_questoes' verificadas/criadas.")
    conn.commit()

# Bloco principal que será executado quando rodarmos este arquivo diretamente
if __name__ == '__main__':
    conn = conectar()
    criar_tabelas(conn)
    
    # Podemos adicionar alguns alunos de exemplo para começar
    try:
        cursor = conn.cursor()
        alunos_exemplo = [('Vithor',), ('Fabio',), ('MGLWI',)]
        cursor.executemany('INSERT INTO alunos (nome) VALUES (?)', alunos_exemplo)
        conn.commit()
        print(f"{len(alunos_exemplo)} alunos de exemplo inseridos com sucesso.")
    except sqlite3.IntegrityError:
        # Este erro acontece se tentarmos inserir alunos que já existem (o que é esperado na segunda vez que rodarmos)
        print("Alunos de exemplo já existem no banco de dados.")
    
    conn.close()