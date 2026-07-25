================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask-cors, marshmallow, requests, python-dotenv
Domain:        Task Manager API (tasks, users, categories, reports)
Architecture:  Em camadas (models/ routes/ services/ utils/) — porém "vazada":
               regra de negócio nas rotas, segurança fraca, duplicação
Source files:  11 módulos analisados (~1158 linhas)
DB tables:     users, tasks, categories
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask (SQLAlchemy)
Files:   11 analyzed | ~1158 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 3   →  Total: 11

## Findings

### [CRITICAL] Hash de senha com MD5 (algoritmo quebrado, sem salt)  (AP-03)
File: models/user.py:29 (set_password), 32 (check_password)
Description: `hashlib.md5(pwd.encode()).hexdigest()` — MD5 é quebrado e rápido de bruteforce.
Impact: Senhas recuperáveis via rainbow tables em caso de vazamento.
Recommendation: werkzeug.security (hash salgado). Playbook T3.

### [CRITICAL] Senha (hash) exposta no to_dict() e propagada em rotas  (AP-03)
File: models/user.py:16-25 (to_dict inclui 'password'); user_routes.py:33, 85, 209
Description: A serialização padrão do usuário devolve o hash em GET /users/<id>, criação e login.
Impact: Hash de senha trafega ao cliente em várias rotas — facilita ataque offline.
Recommendation: Remover 'password' do to_dict(); serializador sem o campo. Playbook T3/T9.

### [CRITICAL] Segredos hardcoded (SECRET_KEY e senha de SMTP)  (AP-02)
File: app.py:13 (SECRET_KEY='super-secret-key-123'); services/notification_service.py:9-10 (email_password='senha123')
Description: Segredos no código-fonte vazam no Git; senha de SMTP em texto puro.
Impact: Comprometimento de sessões e da conta de e-mail.
Recommendation: Variáveis de ambiente / secret manager. Playbook T2.

### [HIGH] Autenticação fake e nenhuma rota protegida  (AP-07)
File: user_routes.py:210 ('token': 'fake-jwt-token-' + id); rotas sensíveis sem auth
Description: "Token" previsível/não assinado; delete de usuário e relatórios sem autenticação. is_admin() nunca é usado.
Impact: Qualquer cliente executa ações privilegiadas sem login.
Recommendation: Token assinado com expiração + decorator de auth/role. Playbook T7.

### [HIGH] Regra `is_overdue` duplicada inline em 5+ lugares  (AP-05/AP-09)
File: task_routes.py:30-39, 71-80, 284-287; user_routes.py:171-180; report_routes.py:34-37, 132-135
Description: Cálculo de "atrasado" reimplementado inline, enquanto Task.is_overdue() existe e é quase ignorado.
Impact: Inconsistência garantida no médio prazo; manutenção cara.
Recommendation: Usar sempre task.is_overdue(); centralizar. Playbook T9.

### [MEDIUM] N+1 na listagem de tasks e nos relatórios  (AP-08)
File: task_routes.py:41-57 (User.query.get/Category.query.get por task); report_routes.py:53-68
Description: Ignora os relacionamentos mapeados (Task.user/Task.category) e refaz queries manuais.
Impact: Performance degrada linearmente com o volume.
Recommendation: joinedload / relacionamentos já mapeados. Playbook T8.

### [MEDIUM] Serialização de task duplicada (model vs. rotas)  (AP-09)
File: task.py:23-36 (to_dict); task_routes.py:16-59; user_routes.py:162-181
Description: Três formas de serializar a mesma entidade, já divergentes (overdue/user_name/campos parciais).
Impact: Respostas inconsistentes entre endpoints; manutenção cara.
Recommendation: Fonte única de serialização estendida com campos derivados. Playbook T9.

### [MEDIUM] Validação de task duplicada em 3 lugares  (AP-09)
File: task_routes.py:96-114 (create), 166-184 (update); utils/helpers.py:57-108 (process_task_data ignorado)
Description: Regras (status, prioridade 1-5, título 3-200) repetidas; utilitário pronto não é usado.
Impact: Inconsistência de validação; esforço triplicado.
Recommendation: Usar process_task_data (ou schema) nas duas rotas. Playbook T9.

### [LOW] `except:` "pelado" engolindo erros  (AP-11)
File: task_routes.py:62, 236; helpers.py:46-50; report_routes/user_routes com except sem tipo
Description: except sem tipo captura tudo (inclui KeyboardInterrupt/SystemExit) e mascara a causa.
Impact: Erros silenciados; diagnóstico quase impossível.
Recommendation: Capturar exceções específicas e logar. Playbook T10.

### [LOW] Imports não usados e print como log  (AP-11 / deprecated)
File: app.py:7 (os/sys/json); task_routes.py:7 (json/os/sys/time); helpers.py:1-7; prints em task_routes.py:149,219,234, user_routes.py:83,147
Description: Imports mortos poluem; print sem nível/timestamp; datetime.utcnow() deprecated (3.12+).
Impact: Legibilidade e observabilidade ruins.
Recommendation: Remover imports; logging; datetime.now(UTC). Playbook T10/T11.

### [LOW] `type(x) == list` e comparações booleanas verbosas  (AP-10)
File: helpers.py:103; task_routes.py:141, 210; user.py:34-38; task.py:38-48
Description: `type(x) == list` deveria ser isinstance; if/else retornando True/False.
Impact: Idiomática/legibilidade.
Recommendation: isinstance(x, list); `return self.role == 'admin'`. Playbook T11.

## Deprecated / At-risk APIs
- `hashlib.md5` para senha → werkzeug.security / bcrypt.
- `datetime.utcnow()` (deprecated Python 3.12+) → datetime.now(UTC).
- `type(x) == list` → isinstance(x, list).

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
