================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Node.js (JavaScript)
Framework:     Express ^4.18.2
Dependencies:  sqlite3 ^5.1.6
Domain:        LMS / cursos online com checkout (users, courses, enrollments, payments, audit_logs)
Architecture:  Monolítica — God Class (AppManager) com conexão, schema, seed,
               rotas e regra de negócio; segredos e "cripto" caseira em utils.js
Source files:  3 files analyzed (~180 linhas)
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 2   →  Total: 11

## Findings

### [CRITICAL] God Class concentrando DB, schema, seed, rotas e regra de negócio  (AP-04)
File: AppManager.js:4-141
Description: Uma única classe cria a conexão (constructor), define schema+seed (initDb) e
             todas as rotas de checkout/relatório/exclusão (setupRoutes). Zero separação MVC.
Impact: Impossível testar isolado; qualquer mudança toca o arquivo inteiro.
Recommendation: Quebrar em config/database/models/services/controllers/routes. Playbook T4.

### [CRITICAL] Segredos de produção hardcoded  (AP-02)
File: utils.js:1-7 (dbPass, paymentGatewayKey "pk_live_...", smtpUser)
Description: Senha de banco de produção e chave LIVE do gateway de pagamento no código-fonte.
Impact: Comprometimento financeiro direto e do banco de produção; vaza no Git.
Recommendation: Mover para process.env / secret manager; rotacionar chaves. Playbook T2.

### [CRITICAL] Dados de cartão e chave do gateway logados em texto puro  (AP-02)
File: AppManager.js:45 (console.log com `cc` e `config.paymentGatewayKey`)
Description: Número do cartão e chave do gateway gravados nos logs. Viola PCI-DSS.
Impact: Vazamento de dados de cartão; violação regulatória.
Recommendation: Nunca logar PAN/chave; tokenizar e logar só id de transação. Playbook T3/T10.

### [CRITICAL] "Criptografia" de senha caseira e quebrada (badCrypto)  (AP-03)
File: utils.js:17-23 (badCrypto), uso em AppManager.js:68
Description: base64 repetido truncado em 10 chars, sem salt; senha default "123456" quando vazia.
Impact: Senhas trivialmente recuperáveis; contas comprometidas em vazamento.
Recommendation: bcrypt/argon2/scrypt com salt. Playbook T3.

### [HIGH] Callback hell no checkout, sem transação (matrícula órfã)  (AP-05/AP-12)
File: AppManager.js:37-77
Description: db.get/db.run aninhados em 5+ níveis; se o INSERT payments falha após o INSERT
             enrollments, a matrícula fica órfã (sem rollback).
Impact: Dados inconsistentes (matrícula sem pagamento); manutenção penosa.
Recommendation: async/await + transação BEGIN/COMMIT/ROLLBACK. Playbook T5.

### [HIGH] Aprovação de pagamento fake baseada no prefixo do cartão  (AP-05)
File: AppManager.js:47 (`cc.startsWith("4") ? "PAID" : "DENIED"`)
Description: Decide "pago" só porque o cartão começa com 4; sem integração/verificação real.
Impact: Matrículas "pagas" sem cobrança real; perda financeira.
Recommendation: Isolar em paymentService; status derivado da resposta da transação. Playbook T5.

### [HIGH] Exclusão de usuário deixa matrículas/pagamentos órfãos  (AP-12)
File: AppManager.js:131-137
Description: DELETE FROM users sem remover enrollments/payments; a própria resposta admite o lixo.
Impact: Dados órfãos, relatórios financeiros incorretos, corrupção lógica.
Recommendation: Exclusão transacional das dependências (ou FK cascade). Playbook T5.

### [MEDIUM] Relatório financeiro com N+1 assíncrono e contadores manuais frágeis  (AP-08)
File: AppManager.js:80-129
Description: Para cada curso, query de enrollments; para cada enrollment, query de user e payment,
             com contadores "pending" para saber quando responder.
Impact: Performance ruim; resposta pode nunca chegar se um callback falhar.
Recommendation: JOIN/agregação (SUM, GROUP BY) ou Promise.all + async/await. Playbook T8.

### [MEDIUM] Nomes crípticos e ausência de validação de entrada  (AP-09)
File: AppManager.js:29-35 (usr, eml, pwd, c_id, card)
Description: Nomes abreviados; validação só checa presença, sem formato de e-mail nem cartão.
Impact: Dados sujos, erros tardios difíceis de rastrear.
Recommendation: Nomes descritivos + validação por schema antes de tocar no banco. Playbook T9.

### [LOW] Estado global mutável exportado e código morto  (AP-06/AP-10)
File: utils.js:9-10,25 (globalCache, totalRevenue); AppManager.js:2 (import não usado)
Description: globalCache cresce sem TTL (memory leak); totalRevenue importado e nunca usado.
Impact: Vazamento de memória, acoplamento oculto, ruído no código.
Recommendation: Remover cache global/imports mortos; cache com escopo/TTL se necessário.

### [LOW] Banco :memory: perde todos os dados a cada restart  (AP-06 / deprecated)
File: AppManager.js:7 (`new sqlite3.Database(':memory:')`)
Description: Todos os dados (inclusive pagamentos) somem quando o processo reinicia.
Impact: Perda total de dados a cada deploy/restart.
Recommendation: Arquivo persistente; :memory: só para testes.

## Deprecated / At-risk APIs
- sqlite3 estilo callback aninhado → acesso baseado em Promise + async/await.
- badCrypto (base64 caseiro) → bcrypt/argon2/scrypt.
- SQLite :memory: como banco da aplicação → arquivo persistente.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
