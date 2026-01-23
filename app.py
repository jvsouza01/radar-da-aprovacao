import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func, Date
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Se não há DATABASE_URL (desenvolvimento local), usa SQLite
if not db_url:
    db_url = 'sqlite:///radar_aprovacao.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
db = SQLAlchemy(app)

# --- CONSTANTES ---
ADMIN_NAME = 'João Vithor'
DEFAULT_PASSWORD = 'senha123'
DATE_FORMAT = '%d/%m/%Y'

# --- MODELOS DO BANCO DE DADOS ---
class Alunos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)  # Nullable para permitir migrações
    time = db.Column(db.String(20), nullable=True, default='Sem Time')
    senha_hash = db.Column(db.String(200), nullable=True)
    tipo_usuario = db.Column(db.String(10), default='aluno')
    primeira_vez = db.Column(db.Integer, default=1)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha) 

class RegistrosQuestoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    quantidade_questoes = db.Column(db.Integer, nullable=False)
    acertos = db.Column(db.Integer, nullable=False)
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    aluno = db.relationship('Alunos', backref=db.backref('registros_questoes', lazy=True))

class Empresas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

class Simulados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=True)
    nome_especifico = db.Column(db.String(100), nullable=True)
    categoria = db.Column(db.String(50), nullable=False)
    data_realizacao = db.Column(db.Date, nullable=False)
    empresa = db.relationship('Empresas', backref=db.backref('simulados', lazy=True))

class ResultadosSimulados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    simulado_id = db.Column(db.Integer, db.ForeignKey('simulados.id'), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    # Colunas de tempo removidas
    
    aluno = db.relationship('Alunos', backref=db.backref('resultados_simulados', lazy=True))
    simulado = db.relationship('Simulados', backref=db.backref('resultados_simulados', lazy=True))


# --- AUTENTICAÇÃO ---

def get_usuario_atual():
    """Retorna o aluno logado ou None."""
    if 'user_id' not in session:
        return None
    return Alunos.query.get(session['user_id'])

def login_required(f):
    """Decorador para rotas que exigem autenticação."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para rotas que exigem perfil de admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('tipo_usuario') != 'admin':
            return jsonify({'erro': 'Acesso negado. Apenas administradores.'}), 403
        return f(*args, **kwargs)
    return decorated_function


# --- ROTA DE SETUP ---
@app.route('/_iniciar_banco_de_dados_uma_vez')
def iniciar_banco():
    try:
        # --- MUDANÇA CRUCIAL AQUI ---
        # NÃO usamos db.drop_all() para não apagar as questões!
        
        # Tentamos apagar APENAS as tabelas de simulado para recriá-las corretamente
        # Usamos try/except para não dar erro se elas já não existirem
        try:
            ResultadosSimulados.__table__.drop(db.engine)
        except Exception as e:
            print(f"Aviso ao dropar ResultadosSimulados: {e}")

        try:
            Simulados.__table__.drop(db.engine)
        except Exception as e:
            print(f"Aviso ao dropar Simulados: {e}")

        # Recria as tabelas (O SQLAlchemy só cria o que está faltando)
        # As tabelas 'alunos' e 'registros_questoes' ficarão INTACTAS
        db.create_all()
        
        # --- Populando dados básicos (sem duplicar) ---
        
        # 1. Alunos (Verifica antes de adicionar)
        lista_alunos_final = [
            'Luis Guilherme', 'Enzo Gabriel', 'João Vithor'
        ]
        alunos_adicionados = 0
        for nome_aluno in lista_alunos_final:
            if not Alunos.query.filter_by(nome=nome_aluno).first():
                db.session.add(Alunos(nome=nome_aluno))
                alunos_adicionados += 1
        
        # 2. Empresas (Verifica antes de adicionar)
        lista_de_empresas = ["Quad", "rumo", "projeto missão", "projeto caveira"]
        empresas_adicionadas = 0
        for nome_empresa in lista_de_empresas:
            if not Empresas.query.filter_by(nome=nome_empresa).first():
                db.session.add(Empresas(nome=nome_empresa))
                empresas_adicionadas += 1

        db.session.commit()
        
        return f"Manutenção concluída! Tabelas de Simulado recriadas. Questões preservadas. {alunos_adicionados} alunos e {empresas_adicionadas} empresas adicionados.", 200
            
    except Exception as e:
        db.session.rollback()
        return f"Ocorreu um erro: {e}", 500

# --- FUNÇÃO HELPER DE FUSO HORÁRIO ---
def get_start_of_week():
    from datetime import timezone
    today_utc = datetime.now(timezone.utc)
    today_brt = today_utc - timedelta(hours=3)
    days_since_sunday = (today_brt.weekday() - 6 + 7) % 7
    start_of_week_brt = today_brt - timedelta(days=days_since_sunday)
    start_of_week_brt_midnight = start_of_week_brt.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week_utc = start_of_week_brt_midnight + timedelta(hours=3)
    return start_of_week_utc


# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dados = request.get_json() if request.is_json else request.form
        username = dados.get('username', '').strip().lower()
        senha = dados.get('senha', '')
        
        aluno = Alunos.query.filter_by(username=username).first()
        
        if not aluno or not aluno.senha_hash:
            return jsonify({'erro': 'Usuário não encontrado ou sem senha cadastrada'}), 401
        
        if not aluno.check_senha(senha):
            return jsonify({'erro': 'Senha incorreta'}), 401
        
        # Login bem-sucedido - criar sessão
        session['user_id'] = aluno.id
        session['nome'] = aluno.nome
        session['tipo_usuario'] = aluno.tipo_usuario
        
        # Se for primeira vez, redirecionar para trocar senha
        if aluno.primeira_vez:
            return jsonify({'status': 'trocar_senha', 'redirect': url_for('trocar_senha')})
        
        # Caso contrário, ir para página inicial
        redirect_url = url_for('index')
        return jsonify({'status': 'sucesso', 'redirect': redirect_url})
    
    # GET - mostrar formulário de login
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/trocar-senha', methods=['GET', 'POST'])
@login_required
def trocar_senha():
    if request.method == 'POST':
        dados = request.get_json()
        nova_senha = dados.get('nova_senha', '').strip()
        confirma_senha = dados.get('confirma_senha', '').strip()
        
        if not nova_senha or len(nova_senha) < 4:
            return jsonify({'erro': 'A senha deve ter pelo menos 4 caracteres'}), 400
        
        if nova_senha != confirma_senha:
            return jsonify({'erro': 'As senhas não coincidem'}), 400
        
        aluno = get_usuario_atual()
        aluno.set_senha(nova_senha)
        aluno.primeira_vez = 0
        db.session.commit()
        
        return jsonify({'status': 'sucesso', 'mensagem': 'Senha alterada com sucesso!', 'redirect': url_for('index')})
    
    return render_template('trocar_senha.html')

@app.route('/registrar-questoes')
@login_required
def registrar_questoes():
    """Página para registrar questões. Alunos só veem seu próprio nome, admins veem todos."""
    usuario = get_usuario_atual()
    return render_template('registrar_questoes.html', usuario=usuario)


@app.route('/_migrar_autenticacao')
def migrar_autenticacao():
    """Migração para adicionar autenticação aos alunos existentes."""
    try:
        # 1. Verificar se as colunas já existem
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        colunas = [c['name'] for c in inspector.get_columns('alunos')]
        
        # 2. Adicionar colunas se não existirem
        if 'senha_hash' not in colunas:
            with db.session.connection() as conn:
                conn.execute(text("ALTER TABLE alunos ADD COLUMN senha_hash VARCHAR(200)"))
                conn.execute(text("ALTER TABLE alunos ADD COLUMN tipo_usuario VARCHAR(10) DEFAULT 'aluno'"))
                conn.execute(text("ALTER TABLE alunos ADD COLUMN primeira_vez INTEGER DEFAULT 1"))
                db.session.commit()
        
        # 3. Definir senha padrão para alunos sem senha
        alunos_sem_senha = Alunos.query.filter(Alunos.senha_hash == None).all()
        for aluno in alunos_sem_senha:
            aluno.set_senha(DEFAULT_PASSWORD)  # Senha padrão
            if aluno.tipo_usuario is None:
                # João Vithor é o admin
                if aluno.nome == ADMIN_NAME:
                    aluno.tipo_usuario = 'admin'
                    aluno.primeira_vez = 0  # Admin não precisa trocar senha na primeira vez
                else:
                    aluno.tipo_usuario = 'aluno'
            if aluno.primeira_vez is None:
                aluno.primeira_vez = 1
        
        db.session.commit()
        
        return f"✅ Migração concluída! {len(alunos_sem_senha)} alunos atualizados com senha padrão '{DEFAULT_PASSWORD}'. {ADMIN_NAME} configurado como admin.", 200
    
    except Exception as e:
        db.session.rollback()
        return f"❌ Erro na migração: {e}", 500


@app.route('/_migrar_completo')
def migrar_completo():
    """Migração COMPLETA para adicionar autenticação E usernames em uma única execução."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        colunas = [c['name'] for c in inspector.get_columns('alunos')]
        
        mensagens = []
        
        # 1. Adicionar coluna senha_hash se não existir
        if 'senha_hash' not in colunas:
            with db.session.connection() as conn:
                conn.execute(text("ALTER TABLE alunos ADD COLUMN senha_hash VARCHAR(200)"))
                conn.execute(text("ALTER TABLE alunos ADD COLUMN tipo_usuario VARCHAR(10) DEFAULT 'aluno'"))
                conn.execute(text("ALTER TABLE alunos ADD COLUMN primeira_vez INTEGER DEFAULT 1"))
                db.session.commit()
            mensagens.append("✅ Colunas de autenticação adicionadas")
        
        # 2. Adicionar coluna username se não existir
        if 'username' not in colunas:
            with db.session.connection() as conn:
                conn.execute(text("ALTER TABLE alunos ADD COLUMN username VARCHAR(50)"))
                db.session.commit()
            mensagens.append("✅ Coluna username adicionada")
        
        # 3. AGORA podemos fazer SELECTs, pois as colunas existem
        
        # 3a. Gerar usernames para quem não tem
        def gerar_username(nome_completo):
            partes = nome_completo.strip().split()
            if len(partes) == 1:
                return partes[0].lower()
            return (partes[0][0] + partes[-1]).lower()
        
        alunos = db.session.execute(text("SELECT id, nome, username FROM alunos")).fetchall()
        usernames_gerados = []
        
        for row in alunos:
            aluno_id, nome, username_atual = row
            
            # Se já tem username, pula
            if username_atual:
                continue
            
            username_proposto = gerar_username(nome)
            
            # Verificar unicidade
            username_final = username_proposto
            contador = 1
            while db.session.execute(text("SELECT 1 FROM alunos WHERE username = :u"), {'u': username_final}).first():
                username_final = f"{username_proposto}{contador}"
                contador += 1
            
            # Atualizar username
            db.session.execute(text("UPDATE alunos SET username = :u WHERE id = :i"), {'u': username_final, 'i': aluno_id})
            usernames_gerados.append(f"{nome} → {username_final}")
        
        # 3b. Definir senhas e configurar João Vithor como admin
        alunos_todos = db.session.execute(text("SELECT id, nome, senha_hash FROM alunos")).fetchall()
        senhas_configuradas = 0
        
        for row in alunos_todos:
            aluno_id, nome, senha_hash_atual = row
            
            # Se já tem senha, pula
            if senha_hash_atual:
                continue
            
            senha_hash = generate_password_hash(DEFAULT_PASSWORD)
            
            # João Vithor é admin
            if nome == ADMIN_NAME:
                db.session.execute(text(
                    "UPDATE alunos SET senha_hash = :sh, tipo_usuario = 'admin', primeira_vez = 0 WHERE id = :i"
                ), {'sh': senha_hash, 'i': aluno_id})
                mensagens.append(f"👑 {ADMIN_NAME} configurado como ADMIN")
            else:
                db.session.execute(text(
                    "UPDATE alunos SET senha_hash = :sh, tipo_usuario = 'aluno', primeira_vez = 1 WHERE id = :i"
                ), {'sh': senha_hash, 'i': aluno_id})
            
            senhas_configuradas += 1
        
        db.session.commit()
        
        # Criar índice único em username (PostgreSQL)
        try:
            db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_alunos_username ON alunos(username)"))
            db.session.commit()
            mensagens.append("✅ Índice único criado em username")
        except Exception:  # Ignora erro se índice já existir ou em SQLite
            pass
        
        mensagens.append(f"✅ {senhas_configuradas} senhas configuradas (padrão: senha123)")
        mensagens.append(f"✅ {len(usernames_gerados)} usernames gerados:")
        mensagens.extend([f"  • {ug}" for ug in usernames_gerados])
        
        return "<br>".join(mensagens), 200
    
    except Exception as e:
        db.session.rollback()
        return f"❌ Erro na migração: {e}", 500

@app.route('/_migrar_adicionar_username')
def migrar_adicionar_username():
    """Migração para adicionar campo username aos alunos existentes."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        colunas = [c['name'] for c in inspector.get_columns('alunos')]
        
        # 1. Adicionar coluna username se não existir
        if 'username' not in colunas:
            with db.session.connection() as conn:
                conn.execute(text("ALTER TABLE alunos ADD COLUMN username VARCHAR(50)"))
                db.session.commit()
        
        # 2. Gerar usernames para alunos que não têm
        def gerar_username(nome_completo):
            """Gera username: primeira letra do nome + sobrenome (lowercase, sem espaços)"""
            partes = nome_completo.strip().split()
            if len(partes) == 1:
                return partes[0].lower()
            return (partes[0][0] + partes[-1]).lower()
        
        alunos_sem_username = Alunos.query.filter((Alunos.username == None) | (Alunos.username == '')).all()
        usernames_gerados = []
        
        for aluno in alunos_sem_username:
            username_proposto = gerar_username(aluno.nome)
            
            # Verificar unicidade e adicionar número se necessário
            username_final = username_proposto
            contador = 1
            while Alunos.query.filter_by(username=username_final).first():
                username_final = f"{username_proposto}{contador}"
                contador += 1
            
            aluno.username = username_final
            usernames_gerados.append(f"{aluno.nome} → {username_final}")
            
            # Verifica se é o admin
            if aluno.nome == ADMIN_NAME:
                aluno.tipo_usuario = 'admin'
                aluno.primeira_vez = 0  # Admin não precisa trocar senha
        
        # 3. Tornar username obrigatório e único
        if 'username' in colunas:
            with db.session.connection() as conn:
                # SQLite não suporta ALTER COLUMN diretamente, então pulamos para SQLite
                db_type = str(db.engine.url).split(':')[0]
                if db_type == 'postgresql':
                    conn.execute(text("ALTER TABLE alunos ALTER COLUMN username SET NOT NULL"))
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_alunos_username ON alunos(username)"))
                db.session.commit()
        
        db.session.commit()
        
        msg = f"✅ Migração concluída! {len(alunos_sem_username)} usernames gerados:\n"
        msg += "\n".join(usernames_gerados)
        msg += f"\n\n⚠️ {ADMIN_NAME} configurado como ADMINISTRADOR."
        return msg, 200
    
    except Exception as e:
        db.session.rollback()
        return f"❌ Erro na migração: {e}", 500


# --- ROTAS PRINCIPAIS ---
@app.route('/')
def index(): 
    usuario = get_usuario_atual()
    return render_template('index.html', usuario=usuario)

# NOTA: A rota /registrar-questoes está definida nas linhas 233-238 com mais lógica

@app.route('/historico-questoes')
@login_required
def historico_questoes(): return render_template('historico_questoes.html')

@app.route('/ranking-semana-passada')
def ranking_semana_passada(): return render_template('ranking_semana_passada.html')

@app.route('/ranking-geral')
def ranking_geral(): return render_template('ranking_geral.html')

# --- ROTAS DE API DE QUESTÕES ---

# --- ROTAS DE TIMES ---

@app.route('/gerenciar-times')
@admin_required
def gerenciar_times():
    return render_template('gerenciar_times.html')

@app.route('/batalha-times')
def batalha_times():
    return render_template('batalha_times.html')

@app.route('/api/alunos/atualizar-time', methods=['POST'])
@admin_required
def atualizar_time_aluno():
    dados = request.get_json()
    aluno = Alunos.query.get(dados['aluno_id'])
    if not aluno:
        return jsonify({'erro': 'Aluno não encontrado'}), 404

    aluno.time = dados['time']
    db.session.commit()
    return jsonify({'status': 'sucesso'})

@app.route('/api/batalha/placar', methods=['GET'])
def get_placar_times():
        start_date = get_start_of_week()
        conn = db.session.connection()

        # --- FUNÇÃO AUXILIAR PARA BUSCAR TOTAIS E RANKING ---
        def buscar_dados_time(nome_time):
            # 1. Total Geral do Time
            sql_total = text("""
                SELECT SUM(r.quantidade_questoes) as total_q, SUM(r.acertos) as total_a 
                FROM registros_questoes r 
                JOIN alunos a ON a.id = r.aluno_id 
                WHERE a.time = :time 
                AND r.data_registro >= :start_date
            """)
            res_total = conn.execute(sql_total, {'time': nome_time, 'start_date': start_date}).first()
            
            total_q = res_total.total_q if res_total and res_total.total_q else 0
            total_a = res_total.total_a if res_total and res_total.total_a else 0
            precisao = (total_a / total_q * 100) if total_q > 0 else 0

            # 2. Ranking Individual dos Membros
            sql_ranking = text("""
                SELECT a.nome, SUM(r.quantidade_questoes) as qtd
                FROM registros_questoes r
                JOIN alunos a ON a.id = r.aluno_id
                WHERE a.time = :time
                AND r.data_registro >= :start_date
                GROUP BY a.nome
                ORDER BY qtd DESC
            """)
            res_ranking = conn.execute(sql_ranking, {'time': nome_time, 'start_date': start_date}).mappings().all()
            
            lista_membros = [{'nome': row.nome, 'qtd': row.qtd} for row in res_ranking]

            return {
                'questoes': total_q,
                'acertos': total_a,
                'precisao': round(precisao, 2),
                'ranking': lista_membros # Lista nova incluída aqui
            }

        return jsonify({
            'GUI': buscar_dados_time('GUI'),
            'ENZO': buscar_dados_time('ENZO')
        })

# Atualize a API de alunos para retornar o time atual também
@app.route('/api/alunos-com-time', methods=['GET'])
def get_alunos_com_time():
    alunos = Alunos.query.order_by(Alunos.nome).all()
    return jsonify([{'id': a.id, 'nome': a.nome, 'username': a.username, 'time': a.time} for a in alunos])



@app.route('/_migrar_banco_adicionar_times')
def migrar_times():
    try:
        with db.session.connection() as conn:
            
            conn.execute(text("ALTER TABLE alunos ADD COLUMN time VARCHAR(20) DEFAULT 'Sem Time'"))
            
            
            db.session.commit()
            
        return "Sucesso! Coluna 'time' adicionada e definida como 'Sem Time' para todos.", 200
    except Exception as e:
        
        if "already exists" in str(e):
             return "A coluna 'time' já existe, tudo certo.", 200
        return f"Erro ao adicionar coluna: {e}", 500
    
# --- ROTAS DE GERENCIAMENTO DE ALUNOS ---

@app.route('/gerenciar-alunos')
@admin_required
def gerenciar_alunos_page():
    return render_template('gerenciar_alunos.html')

@app.route('/api/alunos', methods=['POST'])
@admin_required
def criar_aluno():
    dados = request.get_json()
    nome = dados.get('nome', '').strip()
    username = dados.get('username', '').strip().lower()
    time = dados.get('time', 'Sem Time')
    
    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    
    if not username:
        return jsonify({'erro': 'Username é obrigatório'}), 400
    
    if Alunos.query.filter_by(username=username).first():
        return jsonify({'erro': 'Já existe um aluno com esse username'}), 409

    novo_aluno = Alunos(nome=nome, username=username, time=time)
    novo_aluno.set_senha(DEFAULT_PASSWORD)  # Senha padrão
    novo_aluno.primeira_vez = 1  # Força troca de senha no primeiro login
    db.session.add(novo_aluno)
    db.session.commit()
    return jsonify({'status': 'sucesso', 'mensagem': 'Aluno criado!'}), 201

@app.route('/api/alunos/<int:id>', methods=['PUT'])
@admin_required
def editar_aluno(id):
    aluno = Alunos.query.get_or_404(id)
    dados = request.get_json()
    
    novo_nome = dados.get('nome', '').strip()
    novo_username = dados.get('username', '').strip().lower()
    novo_time = dados.get('time')

    if novo_nome:
        aluno.nome = novo_nome
    
    if novo_username:
        # Verifica se o username já existe em OUTRO aluno
        existente = Alunos.query.filter_by(username=novo_username).first()
        if existente and existente.id != id:
            return jsonify({'erro': 'Já existe outro aluno com esse username'}), 409
        aluno.username = novo_username
    
    if novo_time:
        aluno.time = novo_time

    db.session.commit()
    return jsonify({'status': 'sucesso', 'mensagem': 'Dados atualizados!'})

@app.route('/api/alunos/<int:id>', methods=['DELETE'])
@admin_required
def deletar_aluno(id):
    aluno = Alunos.query.get_or_404(id)
    try:
        # Nota: Se houver registros vinculados (questões/simulados), 
        # o banco pode bloquear ou apagar em cascata dependendo da configuração.
        # Aqui vamos deletar os registros filhos manualmente para garantir limpeza
        RegistrosQuestoes.query.filter_by(aluno_id=id).delete()
        ResultadosSimulados.query.filter_by(aluno_id=id).delete()
        
        db.session.delete(aluno)
        db.session.commit()
        return jsonify({'status': 'sucesso', 'mensagem': 'Aluno e histórico apagados.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao apagar: {str(e)}'}), 500    
    

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    alunos = Alunos.query.order_by(Alunos.nome).all()
    return jsonify([{'id': aluno.id, 'nome': aluno.nome} for aluno in alunos])

@app.route('/api/registros', methods=['POST'])
@login_required
def add_registro():
    dados = request.get_json()
    aluno_id = dados.get('aluno_id')
    
    # Converter aluno_id para inteiro (pode vir como string do JSON)
    if aluno_id is not None:
        aluno_id = int(aluno_id)
    
    # Validar que o aluno só pode registrar para si mesmo (exceto admin)
    usuario_atual = get_usuario_atual()
    if usuario_atual.tipo_usuario != 'admin' and aluno_id != usuario_atual.id:
        return jsonify({'erro': 'Você só pode registrar suas próprias questões'}), 403
    
    novo_registro = RegistrosQuestoes(aluno_id=aluno_id, quantidade_questoes=dados['quantidade'], acertos=dados['acertos'])
    db.session.add(novo_registro)
    db.session.commit()
    return jsonify({'status': 'sucesso'}), 201

@app.route('/api/registros/recentes', methods=['GET'])
def get_registros_recentes():
    registros = RegistrosQuestoes.query.order_by(RegistrosQuestoes.id.desc()).limit(10).all()
    lista_registros = [{'id': r.id, 'aluno_id': r.aluno_id, 'aluno_nome': r.aluno.nome, 'questoes': r.quantidade_questoes, 'acertos': r.acertos} for r in registros]
    return jsonify(lista_registros)

@app.route('/api/registros/<int:registro_id>', methods=['DELETE'])
@login_required
def delete_registro(registro_id):
    registro = RegistrosQuestoes.query.get_or_404(registro_id)
    
    # Validar que aluno só pode deletar seus próprios registros
    usuario_atual = get_usuario_atual()
    if usuario_atual.tipo_usuario != 'admin' and registro.aluno_id != usuario_atual.id:
        return jsonify({'erro': 'Você só pode apagar seus próprios registros'}), 403
    
    db.session.delete(registro)
    db.session.commit()
    return jsonify({'status': 'sucesso', 'mensagem': 'Registro apagado.'})

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    start_of_week = get_start_of_week()
    conn = db.session.connection()
    params = {'start_date': start_of_week}
    query_qtd = text('SELECT a.nome, SUM(r.quantidade_questoes) as total FROM registros_questoes r JOIN alunos a ON a.id = r.aluno_id WHERE r.data_registro >= :start_date GROUP BY a.nome ORDER BY total DESC LIMIT 10')
    ranking_quantidade = conn.execute(query_qtd, params).mappings().all()
    query_perc = text('SELECT a.nome, (SUM(r.acertos) * 100.0 / SUM(r.quantidade_questoes)) as percentual FROM registros_questoes r JOIN alunos a ON a.id = r.aluno_id WHERE r.data_registro >= :start_date GROUP BY a.nome HAVING SUM(r.quantidade_questoes) > 20 ORDER BY percentual DESC LIMIT 10')
    ranking_percentual = conn.execute(query_perc, params).mappings().all()
    return jsonify({'quantidade': [dict(row) for row in ranking_quantidade], 'percentual': [dict(row) for row in ranking_percentual]})

@app.route('/api/rankings/geral', methods=['GET'])
def get_rankings_gerais():
    conn = db.session.connection()
    query_qtd = text('SELECT a.nome, SUM(r.quantidade_questoes) as total FROM registros_questoes r JOIN alunos a ON a.id = r.aluno_id GROUP BY a.nome ORDER BY total DESC')
    ranking_quantidade = conn.execute(query_qtd).mappings().all()
    query_perc = text('SELECT a.nome, (SUM(r.acertos) * 100.0 / SUM(r.quantidade_questoes)) as percentual FROM registros_questoes r JOIN alunos a ON a.id = r.aluno_id GROUP BY a.nome HAVING SUM(r.quantidade_questoes) > 0 ORDER BY percentual DESC')
    ranking_percentual = conn.execute(query_perc).mappings().all()
    return jsonify({'quantidade': [dict(row) for row in ranking_quantidade], 'percentual': [dict(row) for row in ranking_percentual]})

@app.route('/api/rankings/semana-passada', methods=['GET'])
def get_rankings_semana_passada():
    # 1. Definição das datas
    start_of_current_week = get_start_of_week()
    end_of_last_week = start_of_current_week - timedelta(seconds=1)
    start_of_last_week = start_of_current_week - timedelta(days=7)
    
    conn = db.session.connection()
    params = {'start': start_of_last_week, 'end': end_of_last_week}
    
    # 2. Consultas (MANTIDAS IGUAIS)
    query_qtd = text('SELECT a.nome, SUM(r.quantidade_questoes) as total FROM registros_questoes r JOIN alunos a ON a.id = r.aluno_id WHERE r.data_registro BETWEEN :start AND :end GROUP BY a.nome ORDER BY total DESC')
    ranking_quantidade = conn.execute(query_qtd, params).mappings().all()
    
    query_perc = text('SELECT a.nome, (SUM(r.acertos) * 100.0 / SUM(r.quantidade_questoes)) as percentual FROM registros_questoes r JOIN alunos a ON a.id = r.aluno_id WHERE r.data_registro BETWEEN :start AND :end GROUP BY a.nome HAVING SUM(r.quantidade_questoes) > 20 ORDER BY percentual DESC')
    ranking_percentual = conn.execute(query_perc, params).mappings().all()

    # 3. Batalha de Times (MANTIDA IGUAL)
    def calcular_time(nome_time):
        sql = text("""
            SELECT SUM(r.quantidade_questoes) as total_q, SUM(r.acertos) as total_a 
            FROM registros_questoes r 
            JOIN alunos a ON a.id = r.aluno_id 
            WHERE a.time = :time AND r.data_registro BETWEEN :start AND :end
        """)
        params_time = params.copy()
        params_time['time'] = nome_time
        res = conn.execute(sql, params_time).first()
        total_q = res.total_q if res and res.total_q else 0
        total_a = res.total_a if res and res.total_a else 0
        precisao = (total_a / total_q * 100) if total_q > 0 else 0
        return {'questoes': total_q, 'precisao': round(precisao, 2)}

    gui = calcular_time('GUI')
    enzo = calcular_time('ENZO')

    vencedor = "EMPATE"
    if gui['questoes'] > enzo['questoes']: vencedor = "GUI 🔵"
    elif enzo['questoes'] > gui['questoes']: vencedor = "ENZO 🔴"

    return jsonify({
        'quantidade': [dict(row) for row in ranking_quantidade], 
        'percentual': [dict(row) for row in ranking_percentual],
        'batalha': {'GUI': gui, 'ENZO': enzo, 'vencedor': vencedor},
        # --- NOVO: Envia as datas formatadas ---
        'periodo': {
            'inicio': start_of_last_week.strftime(DATE_FORMAT),
            'fim': end_of_last_week.strftime(DATE_FORMAT)
        }
    })
# --- ROTAS DE GERENCIAMENTO DE SIMULADOS ---
@app.route('/gerenciar-simulados')
@admin_required
def gerenciar_simulados():
    return render_template('gerenciamento_simulados.html')

@app.route('/api/empresas', methods=['GET'])
def get_empresas():
    empresas = Empresas.query.order_by(Empresas.nome).all()
    return jsonify([{'id': e.id, 'nome': e.nome} for e in empresas])

@app.route('/api/empresas', methods=['POST'])
def add_empresa():
    dados = request.get_json()
    if 'nome' not in dados or dados['nome'].strip() == '': return jsonify({'status': 'erro', 'mensagem': 'O nome da empresa é obrigatório.'}), 400
    existe = Empresas.query.filter_by(nome=dados['nome'].strip()).first()
    if existe: return jsonify({'status': 'erro', 'mensagem': 'Essa empresa já existe.'}), 409
    nova_empresa = Empresas(nome=dados['nome'].strip())
    db.session.add(nova_empresa)
    db.session.commit()
    return jsonify({'status': 'sucesso', 'empresa': {'id': nova_empresa.id, 'nome': nova_empresa.nome}}), 201

@app.route('/api/simulados', methods=['GET'])
def get_simulados():
    simulados = db.session.query(Simulados, Empresas.nome).join(Empresas).order_by(Simulados.data_realizacao.desc()).all()
    lista_simulados = []
    for simulado, empresa_nome in simulados:
        nome_display = f"Nº {simulado.numero}" if simulado.numero else simulado.nome_especifico
        lista_simulados.append({'id': simulado.id, 'nome_display': f"{empresa_nome} - {nome_display} ({simulado.categoria})", 'data': simulado.data_realizacao.strftime(DATE_FORMAT)})
    return jsonify(lista_simulados)

@app.route('/api/simulados', methods=['POST'])
def add_simulado():
    dados = request.get_json()
    if not all(k in dados for k in ['empresa_id', 'categoria', 'data_realizacao']): return jsonify({'status': 'erro', 'mensagem': 'Dados incompletos.'}), 400
    if not dados.get('numero') and not dados.get('nome_especifico'): return jsonify({'status': 'erro', 'mensagem': 'É preciso fornecer o número ou um nome específico.'}), 400
    novo_simulado = Simulados(empresa_id=dados['empresa_id'], numero=dados.get('numero'), nome_especifico=dados.get('nome_especifico'), categoria=dados['categoria'], data_realizacao=datetime.strptime(dados['data_realizacao'], '%Y-%m-%d').date())
    db.session.add(novo_simulado)
    db.session.commit()
    return jsonify({'status': 'sucesso'}), 201

@app.route('/api/resultados', methods=['POST'])
def add_resultado():
    # ROTA SIMPLIFICADA: Só recebe nota
    dados = request.get_json()
    if not all(k in dados for k in ['aluno_id', 'simulado_id', 'nota']):
        return jsonify({'status': 'erro', 'mensagem': 'Dados incompletos (aluno, simulado ou nota).'}), 400
    existe = ResultadosSimulados.query.filter_by(aluno_id=dados['aluno_id'], simulado_id=dados['simulado_id']).first()
    if existe:
        return jsonify({'status': 'erro', 'mensagem': 'Este aluno já possui uma nota para este simulado.'}), 409
    
    novo_resultado = ResultadosSimulados(
        aluno_id=dados['aluno_id'],
        simulado_id=dados['simulado_id'],
        nota=dados['nota']
        # Tempos removidos
    )
    db.session.add(novo_resultado)
    db.session.commit()
    return jsonify({'status': 'sucesso'}), 201

@app.route('/api/resultados/recentes', methods=['GET'])
def get_resultados_recentes():
    resultados = ResultadosSimulados.query.order_by(ResultadosSimulados.id.desc()).limit(15).all()
    lista_resultados = []
    for r in resultados:
        nome_simulado = f"Nº {r.simulado.numero}" if r.simulado.numero else r.simulado.nome_especifico
        nome_display = f"{r.simulado.empresa.nome} - {nome_simulado} ({r.simulado.categoria})"
        lista_resultados.append({'id': r.id, 'aluno_nome': r.aluno.nome, 'simulado_nome': nome_display, 'nota': r.nota})
    return jsonify(lista_resultados)

@app.route('/api/resultados/<int:resultado_id>', methods=['DELETE'])
def delete_resultado(resultado_id):
    resultado = ResultadosSimulados.query.get_or_404(resultado_id)
    db.session.delete(resultado)
    db.session.commit()
    return jsonify({'status': 'sucesso', 'mensagem': 'Nota apagada com sucesso.'})

@app.route('/ranking-simulados')
def ranking_simulados():
    return render_template('ranking_simulados.html')

@app.route('/api/simulados/<int:simulado_id>/ranking', methods=['GET'])
def get_ranking_por_simulado(simulado_id):
    # ROTA SIMPLIFICADA: Removemos os joins de tempo
    resultados = db.session.query(ResultadosSimulados.nota, Alunos.nome).join(Alunos).filter(ResultadosSimulados.simulado_id == simulado_id).order_by(ResultadosSimulados.nota.desc()).all()
    ranking = [{'aluno_nome': nome, 'nota': nota} for nota, nome in resultados]
    return jsonify(ranking)

@app.route('/consulta-desempenho')
def consulta_desempenho(): return render_template('consulta_desempenho.html')

@app.route('/api/consulta/desempenho', methods=['GET'])
def get_consulta_desempenho():
    aluno_id = request.args.get('aluno_id')
    data_inicio_str = request.args.get('inicio')
    data_fim_str = request.args.get('fim')
    if not aluno_id or not data_inicio_str or not data_fim_str: return jsonify({'erro': 'Parâmetros aluno_id, inicio e fim são obrigatórios.'}), 400
    try:
        data_inicio = datetime.strptime(data_inicio_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        data_fim = datetime.strptime(data_fim_str + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        resumo = db.session.query(func.sum(RegistrosQuestoes.quantidade_questoes).label('total_questoes'), func.sum(RegistrosQuestoes.acertos).label('total_acertos')).filter(RegistrosQuestoes.aluno_id == aluno_id, RegistrosQuestoes.data_registro >= data_inicio, RegistrosQuestoes.data_registro <= data_fim).first()
        total_questoes = resumo.total_questoes if resumo and resumo.total_questoes else 0
        total_acertos = resumo.total_acertos if resumo and resumo.total_acertos else 0
        percentual_total = (total_acertos * 100.0 / total_questoes) if total_questoes > 0 else 0
        dados_diarios_query = db.session.query(func.date(RegistrosQuestoes.data_registro).label('dia'), func.sum(RegistrosQuestoes.quantidade_questoes).label('questoes_dia'), func.sum(RegistrosQuestoes.acertos).label('acertos_dia')).filter(RegistrosQuestoes.aluno_id == aluno_id, RegistrosQuestoes.data_registro >= data_inicio, RegistrosQuestoes.data_registro <= data_fim).group_by(func.date(RegistrosQuestoes.data_registro)).order_by(func.date(RegistrosQuestoes.data_registro)).all()
        dados_diarios_formatados = []
        for row in dados_diarios_query:
            dia_data = row.dia; questoes = row.questoes_dia; acertos = row.acertos_dia
            percentual_dia = (acertos * 100.0 / questoes) if questoes > 0 else 0
            dados_diarios_formatados.append({'data': dia_data.strftime('%Y-%m-%d'), 'questoes': questoes, 'acertos': acertos, 'percentual': round(percentual_dia, 2)})
        aluno = Alunos.query.get(aluno_id)
        nome_aluno = aluno.nome if aluno else "Aluno não encontrado"
        return jsonify({'aluno_nome': nome_aluno, 'data_inicio': data_inicio_str, 'data_fim': data_fim_str, 'total_questoes': total_questoes, 'total_acertos': total_acertos, 'percentual_total': round(percentual_total, 2), 'dados_diarios': dados_diarios_formatados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao consultar o banco de dados: {e}'}), 500

# --- EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas se não existirem
    app.run(debug=True, host='0.0.0.0', port=5000)