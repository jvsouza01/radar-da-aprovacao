# 🎯 Radar do Aprovado - Credenciais de Acesso

## 🔐 Sistema de Login

O sistema agora utiliza **username + senha** para autenticação.

---

## 👤 Usuários do Sistema

### **Administrador**
- **Nome:** João Vithor
- **Username:** `jvithor`
- **Senha padrão:** `senha123`
- **Perfil:** Admin (acesso total)
- **Primeira vez:** Não precisa trocar senha

### **Alunos**

#### Luis Guilherme
- **Username:** `lguilherme`
- **Senha padrão:** `senha123`
- **Perfil:** Aluno
- **Primeira vez:** Sim (precisará trocar senha no primeiro login)

#### Enzo Gabriel
- **Username:** `egabriel`
- **Senha padrão:** `senha123`
- **Perfil:** Aluno
- **Primeira vez:** Sim (precisará trocar senha no primeiro login)

---

## 📋 Como Configurar

### 1. Execute as migrações em ordem:

```
http://localhost:5000/_migrar_autenticacao
```
**Resultado esperado:** Adiciona colunas de senha e define João Vithor como admin

```
http://localhost:5000/_migrar_adicionar_username
```
**Resultado esperado:** Gera usernames automáticos para todos os alunos

### 2. Faça login no sistema

Acesse: `http://localhost:5000/login`

**Admin:**
- Username: `jvithor`
- Senha: `senha123`

**Alunos:**
- Username: `lguilherme`, `egabriel`
- Senha: `senha123` (deverão trocar no primeiro acesso)

---

## 🔑 Regras de Senha

- **Mínimo:** 4 caracteres
- **Primeira vez:** Alunos são obrigados a trocar senha no primeiro login
- **Admin:** Não precisa trocar senha (já configurado)

---

## 🛠️ Funcionalidades por Perfil

### **Admin (João Vithor)**
✅ Gerenciar alunos (criar, editar, deletar)  
✅ Gerenciar times  
✅ Gerenciar simulados  
✅ Visualizar todos os rankings e relatórios  
✅ Registrar questões para qualquer aluno  

### **Alunos**
✅ Registrar suas próprias questões  
✅ Visualizar seu histórico  
✅ Ver rankings gerais  
❌ Não podem editar outros alunos  
❌ Não podem acessar páginas administrativas  

---

## 📝 Criando Novos Alunos

Como **admin**, acesse: `http://localhost:5000/gerenciar-alunos`

**Campos obrigatórios:**
- Nome completo
- Username (apenas letras minúsculas e números)
- Time (opcional)

**Senha automática:** `senha123` (o aluno deverá trocar no primeiro login)
