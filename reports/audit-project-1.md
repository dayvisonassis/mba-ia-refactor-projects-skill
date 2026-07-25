================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, usuários, pedidos, relatórios)
Architecture:  Monolítica — 4 arquivos flat; pastas "models"/"controllers" só no
               nome, sem separação real (SQL + regra de negócio + notificações misturados)
Source files:  4 files analyzed (~784 linhas)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~784 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 3   →  Total: 13

## Findings

### [CRITICAL] SQL Injection generalizado  (AP-01)
File: models.py:28, 48-49, 60, 68, 92, 110, 127-128, 140, 148-150, 155-166, 174, 280, 291-297
Description: Praticamente toda query é montada por concatenação de string com entrada do
             usuário (ex.: login `WHERE email = '"+email+"' AND senha = '"+senha+"'`).
Impact: Bypass de autenticação (' OR '1'='1), vazamento e destruição de dados. OWASP #1.
Recommendation: Migrar 100% das queries para parâmetros (?, tuplas). Playbook T1.

### [CRITICAL] Endpoints admin executam SQL arbitrário e resetam o banco sem auth  (AP-02/AP-04)
File: app.py:59-78 (/admin/query), app.py:47-57 (/admin/reset-db)
Description: POST /admin/query roda `cursor.execute(query)` com SQL cru do body; /admin/reset-db
             apaga todas as tabelas. Ambos sem autenticação.
Impact: Comprometimento total do banco por design ("SQL injection as a service").
Recommendation: Remover os endpoints; operações admin só via script interno protegido.

### [CRITICAL] Segredos hardcoded e vazados na resposta  (AP-02)
File: app.py:7 (SECRET_KEY), controllers.py:289 (/health retorna a secret_key)
Description: SECRET_KEY fixa no código e devolvida no JSON de /health junto com debug/ambiente.
Impact: Falsificação de sessões; segredo exposto publicamente a qualquer cliente.
Recommendation: Ler de os.environ; /health devolve só status. Playbook T2.

### [CRITICAL] Senhas em texto puro (gravadas, comparadas e retornadas)  (AP-03)
File: models.py:127-128 (grava), models.py:110 (compara), models.py:83 (retorna senha em GET /usuarios), database.py:76-78 (seed em texto puro)
Description: Senha nunca é hasheada; o campo `senha` é serializado na listagem de usuários.
Impact: Vazamento direto de credenciais de todos os usuários se o banco vazar.
Recommendation: werkzeug.security (hash com salt); nunca serializar senha. Playbook T3.

### [HIGH] Conexão de banco global mutável compartilhada entre threads  (AP-06)
File: database.py:4-11
Description: `db_connection = None` global reaproveitado; `check_same_thread=False`.
Impact: Condições de corrida sob carga, dados corrompidos, impossível testar isolado.
Recommendation: Conexão por request (flask.g + teardown). Playbook T6.

### [HIGH] Regra de negócio dentro da camada de dados  (AP-05)
File: models.py:133-169 (criar_pedido: valida estoque, calcula total, insere, baixa estoque)
Description: A "model" concentra regra de negócio de pedido, sem Service/Repository e sem transação.
Impact: Alto acoplamento, regra não testável sem banco, risco de estado inconsistente.
Recommendation: Extrair pedido_service com transação explícita. Playbook T5.

### [HIGH] Efeitos colaterais (e-mail/SMS/push) via print dentro do controller  (AP-05)
File: controllers.py:208-210, 248-250
Description: "Notificações" simuladas com print no fluxo HTTP; lógica de negócio no lugar errado.
Impact: Controller inchado, notificação não reaproveitável/observável.
Recommendation: NotificationService chamado pelo service; logging estruturado. Playbook T5/T10.

### [MEDIUM] Problema N+1 na listagem de pedidos  (AP-08)
File: models.py:171-201 (get_pedidos_usuario), models.py:203-233 (get_todos_pedidos)
Description: 1 query de pedidos + N de itens + M de produtos (cursor2/cursor3 em loop).
Impact: Latência cresce linearmente; gargalo com volume.
Recommendation: JOIN único pedidos+itens+produtos montado em memória. Playbook T8.

### [MEDIUM] Validação duplicada entre criar e atualizar produto  (AP-09)
File: controllers.py:24-62 (criar), controllers.py:64-96 (atualizar)
Description: Blocos de validação quase idênticos, já divergentes (update não valida tamanho de nome/categoria).
Impact: DRY violado; regras divergem silenciosamente.
Recommendation: Validador único reutilizado nas duas rotas. Playbook T9.

### [MEDIUM] DEBUG=True fixo + host 0.0.0.0 (Werkzeug debugger exposto → RCE)  (AP-11 / deprecated)
File: app.py:8, app.py:88
Description: Debug ligado por padrão e servidor publicado em todas as interfaces.
Impact: Execução remota de código via console do debugger; vazamento de stack traces.
Recommendation: debug via variável de ambiente, desligado por padrão. Catálogo Deprecated APIs.

### [LOW] Concatenação `+ str(...)` em vez de f-strings  (AP-10 contexto)
File: controllers.py:8, 57, 106, 161, 179, 208-210, 248-250
Description: Construção de mensagens com concatenação frágil (esquecer str() gera TypeError).
Impact: Legibilidade e propensão a erro.
Recommendation: f-strings.

### [LOW] Magic numbers e listas mágicas espalhados  (AP-10)
File: controllers.py:47-52 (tamanho nome, categorias), controllers.py:242 (status), models.py:257-262 (faixas de desconto)
Description: Números e listas sem constante nomeada, duplicados entre arquivos.
Impact: Intenção obscura; mudança exige caçar valores.
Recommendation: Constantes nomeadas / config. Playbook T12.

### [LOW] print como logging + except genérico vazando detalhes  (AP-11)
File: controllers.py:10-12, 60-62, 218-220 (e demais); todos os `except Exception as e: return str(e)`
Description: print sem nível/timestamp; except genérico devolve str(e) ao cliente.
Impact: Observabilidade ruim; possível vazamento de detalhes internos.
Recommendation: logging + error handler centralizado; mensagens genéricas ao cliente. Playbook T10.

## Deprecated / At-risk APIs
- `app.run(debug=True)` em produção → debugger Werkzeug expõe RCE. Usar debug via env var.
- Senha sem hash (texto puro) → equivalente a texto plano. Usar werkzeug.security / bcrypt.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
