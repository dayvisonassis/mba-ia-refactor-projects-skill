# Explicação Didática dos Problemas Encontrados

> Documento de estudo. Para **cada** problema identificado nos 3 projetos, explico:
> **(1)** o trecho de código exato (`arquivo:linha`), **(2)** por que é um problema,
> **(3)** o impacto real e **(4)** como se corrige.
> Use isso para conferir quais problemas você identificou manualmente e quais passaram batido.

## Escala de severidade (referência)

| Severidade | Significado |
|---|---|
| **CRITICAL** | Falha de segurança/arquitetura que quebra o sistema, expõe dados sensíveis ou destrói a separação de responsabilidades. |
| **HIGH** | Forte violação de MVC/SOLID que dificulta muito manutenção e testes. |
| **MEDIUM** | Padronização, duplicação de código ou performance moderada (ex: N+1). |
| **LOW** | Legibilidade, nomenclatura, magic numbers. |

---

# Projeto 1 — `code-smells-project` (Python/Flask — API de E-commerce)

Arquivos: `app.py`, `controllers.py`, `models.py`, `database.py`. É um monolito com nomes de camada (controllers/models) mas **sem** a disciplina de camadas real.

## 1.1 — [CRITICAL] SQL Injection em massa (concatenação de strings em queries)
**Onde:** `models.py` — praticamente todas as funções. Exemplos:
- `models.py:28` → `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
- `models.py:48-49` → `INSERT INTO produtos (...) VALUES ('" + nome + "', ...`
- `models.py:110` → `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
- `models.py:291` → `query += " AND (nome LIKE '%" + termo + "%' ...)"`

**Por que é um problema:** as queries são construídas concatenando entrada do usuário diretamente na string SQL. Um atacante que envie `email = ' OR '1'='1` no login recebe autenticação sem senha; em `buscar_produtos`, `q='; DROP TABLE produtos;--` pode destruir dados. É a vulnerabilidade nº 1 do OWASP há mais de uma década.

**Impacto:** vazamento total do banco, bypass de autenticação, destruição/adulteração de dados.

**Correção:** usar **queries parametrizadas** — `cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))`. O driver escapa o valor; texto do usuário nunca vira código SQL. (Repare que `database.py:70-72` já usa o jeito certo com `?` no seed — o resto do código ignorou o padrão.)

## 1.2 — [CRITICAL] Endpoint que executa SQL arbitrário do cliente
**Onde:** `app.py:59-78` — rota `POST /admin/query` que faz `cursor.execute(query)` com o SQL vindo do corpo da requisição.

**Por que é um problema:** é literalmente um "SQL injection como serviço". Qualquer pessoa que alcance a rota executa qualquer comando no banco — sem autenticação, sem autorização, sem allowlist. Some-se a `POST /admin/reset-db` (`app.py:47-57`) que apaga todas as tabelas, também sem auth.

**Impacto:** comprometimento total do banco por design.

**Correção:** remover o endpoint. Operações administrativas devem ser scripts internos protegidos, nunca um endpoint HTTP que aceita SQL cru. Se precisar de admin, exigir autenticação + autorização + operações específicas (não SQL livre).

## 1.3 — [CRITICAL] Credenciais e segredos hardcoded + expostos
**Onde:**
- `app.py:7` → `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
- `controllers.py:289` → o `health_check` **retorna a `secret_key` no JSON de resposta**.

**Por que é um problema:** a SECRET_KEY do Flask assina sessões/tokens; hardcoded no código-fonte ela vaza para o Git e para qualquer um com acesso ao repositório. Pior: o `/health` a devolve na resposta HTTP, expondo-a publicamente para qualquer cliente.

**Impacto:** falsificação de sessões, comprometimento de segurança da aplicação.

**Correção:** ler segredos de variáveis de ambiente (`os.environ`) e **nunca** retorná-los em respostas. O `/health` deve devolver só status.

## 1.4 — [CRITICAL] Senhas armazenadas e comparadas em texto puro
**Onde:**
- `models.py:127-128` → `INSERT INTO usuarios (... senha ...) VALUES ('... senha ...')` grava a senha crua.
- `models.py:110` → o login compara `senha = '" + senha + "'` diretamente no banco.
- `database.py:76-78` → usuários seed com senhas `"admin123"`, `"123456"` em texto puro.
- `models.py:83` → `get_todos_usuarios` **retorna o campo `senha`** para o cliente (rota `GET /usuarios`).

**Por que é um problema:** senha nunca deve ser guardada em texto puro. Se o banco vazar, todas as contas estão comprometidas — e ainda são reutilizadas pelos usuários em outros serviços. Retornar a senha na listagem agrava tudo.

**Impacto:** vazamento direto de credenciais de todos os usuários.

**Correção:** hashear com algoritmo forte (`bcrypt`/`argon2`), comparar via `check_password`, e **nunca** serializar o campo senha nas respostas.

## 1.5 — [HIGH] Estado global mutável de conexão (singleton compartilhado entre threads)
**Onde:** `database.py:4-11` — `db_connection = None` global, reaproveitado; conexão SQLite criada com `check_same_thread=False`.

**Por que é um problema:** uma única conexão global compartilhada por todas as requisições/threads gera condições de corrida e travamentos. O `check_same_thread=False` só silencia o aviso do SQLite; não torna o acesso seguro. Estado global mutável é um dos maiores inimigos de testabilidade e concorrência.

**Impacto:** bugs intermitentes sob carga, dados corrompidos, impossível testar isoladamente.

**Correção:** conexão por requisição (ex: `flask.g` + teardown) ou um pool. Injetar a dependência de dados em vez de importar um global.

## 1.6 — [HIGH] Lógica de negócio dentro da camada de dados (Fat Model / God Function)
**Onde:** `models.py:133-169` — `criar_pedido` faz validação de estoque, cálculo de total, inserção do pedido, dos itens **e** baixa de estoque, tudo numa função na "model".

**Por que é um problema:** a camada de dados deveria só persistir/consultar. Aqui ela concentra regra de negócio (cálculo de total, política de estoque) — não há separação Controller/Service/Repository. Isso viola SRP e MVC: qualquer mudança de regra mexe no acesso a dados.

**Impacto:** impossível testar a regra sem banco, alto acoplamento, difícil evoluir.

**Correção:** separar em camadas — Controller recebe request, Service aplica regra (estoque/total), Repository só faz SQL. Envolver a operação numa transação explícita.

## 1.7 — [HIGH] "Notificações" e efeitos colaterais via `print` no controller
**Onde:** `controllers.py:208-210` e `248-250` — envio de e-mail/SMS/push simulado com `print(...)` dentro do controller de pedido.

**Por que é um problema:** o controller mistura orquestração HTTP com notificação. Além de `print` não ser notificação de verdade, o efeito colateral está preso ao fluxo da requisição, sem retry, sem fila, sem serviço dedicado. É lógica de negócio no lugar errado.

**Impacto:** impossível reaproveitar/observar notificações; controller inchado.

**Correção:** extrair um `NotificationService` chamado pelo Service de pedidos; usar logging estruturado, não `print`.

## 1.8 — [MEDIUM] Problema N+1 na listagem de pedidos
**Onde:** `models.py:171-201` (`get_pedidos_usuario`) e `models.py:203-233` (`get_todos_pedidos`) — para cada pedido roda uma query de itens, e para cada item roda outra query de produto (`cursor2`, `cursor3`).

**Por que é um problema:** é o clássico N+1: 1 query para pedidos + N para itens + M para produtos. Com muitos pedidos vira centenas de idas ao banco por request.

**Impacto:** latência que cresce linearmente com os dados; gargalo de performance.

**Correção:** um `JOIN` único entre pedidos, itens_pedido e produtos, montando o resultado em memória.

## 1.9 — [MEDIUM] Validação duplicada entre criar e atualizar produto
**Onde:** `controllers.py:24-62` (`criar_produto`) e `controllers.py:64-96` (`atualizar_produto`) — blocos quase idênticos de validação (nome, preço, estoque, categoria).

**Por que é um problema:** duplicação (violação de DRY). Uma regra que mude precisa ser alterada em dois lugares; fácil divergirem (de fato: `criar` valida tamanho de nome e categoria, `atualizar` não).

**Impacto:** manutenção cara e inconsistências silenciosas.

**Correção:** extrair um validador/schema único (ex: função `validar_produto(dados)` ou marshmallow/pydantic) reutilizado pelas duas rotas.

## 1.10 — [MEDIUM] `DEBUG=True` fixo e servidor exposto em produção
**Onde:** `app.py:8` (`DEBUG=True`), `app.py:88` (`debug=True`) e `app.py:88` (`host="0.0.0.0"`).

**Por que é um problema:** com debug ligado, o Flask expõe o **Werkzeug debugger**, que permite execução de código remoto via console interativo em caso de erro. `0.0.0.0` publica em todas as interfaces. Combinado, é porta aberta para RCE.

**Impacto:** execução remota de código, vazamento de stack traces.

**Correção:** debug controlado por variável de ambiente, desligado por padrão; nunca `debug=True` em produção.

## 1.11 — [LOW] Construção de strings com `+ str(...)` em vez de f-strings
**Onde:** onipresente — `controllers.py:8` (`"Listando " + str(len(produtos)) + " produtos"`), `controllers.py:57`, `208-210`, etc.

**Por que é um problema:** legibilidade e propensão a erro (esquecer um `str()` gera `TypeError`). f-strings são o idiomático moderno em Python.

**Correção:** `f"Listando {len(produtos)} produtos"`.

## 1.12 — [LOW] Magic numbers e listas mágicas espalhados
**Onde:** `controllers.py:47-50` (`2`, `200` para tamanho de nome), `controllers.py:52` (lista de categorias hardcoded), `models.py:257-262` (faixas de desconto `10000`, `5000`, `0.1`...), `controllers.py:242` (lista de status).

**Por que é um problema:** números/listas sem nome não comunicam intenção e ficam duplicados (a lista de status aparece em `controllers.py:242` e a de categorias em `:52`). Mudar a regra exige caça ao valor.

**Correção:** extrair para constantes nomeadas (`NOME_MIN_LEN = 2`, `CATEGORIAS_VALIDAS = [...]`, `FAIXAS_DESCONTO = ...`).

## 1.13 — [LOW] `print` como logging e `except Exception` genérico
**Onde:** `controllers.py` inteiro — `print("ERRO: " + str(e))` e blocos `except Exception as e: return ...500`.

**Por que é um problema:** `print` não tem nível, timestamp nem destino configurável; `except Exception` genérico engole qualquer erro e devolve `str(e)` ao cliente (pode vazar detalhes internos). Não há tratamento centralizado.

**Correção:** módulo `logging` + um error handler centralizado do Flask; mensagens genéricas ao cliente, detalhes só no log.

---

# Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API com checkout)

Arquivos: `src/app.js`, `src/AppManager.js`, `src/utils.js`. O nome "Frankenstein LMS" (app.js:13) já entrega: uma God Class com todas as rotas, callbacks aninhados e segredos no código.

## 2.1 — [CRITICAL] God Class concentrando tudo (`AppManager`)
**Onde:** `AppManager.js:4-141` — uma classe que cria a conexão com o banco (`constructor`), define schema + seed (`initDb`) **e** todas as rotas de checkout, relatório financeiro e exclusão de usuário (`setupRoutes`).

**Por que é um problema:** é o anti-pattern God Class / God Method. Uma única classe é responsável por conexão, DDL, seed, roteamento, regra de negócio de pagamento e persistência. Zero separação Model/View/Controller. Qualquer alteração toca esse arquivo gigante.

**Impacto:** impossível testar em isolamento, alto risco a cada mudança, reuso zero.

**Correção:** quebrar em camadas — `db/` (conexão), `models/` ou repositories, `controllers/` (checkout, report, users), `routes/` (definição das rotas). Injetar dependências.

## 2.2 — [CRITICAL] Segredos de produção hardcoded no código
**Onde:** `utils.js:1-7` — `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: ...`.

**Por que é um problema:** senha de banco de **produção** e **chave live** do gateway de pagamento no código-fonte. Vaza no Git; qualquer um com o repo pode cobrar/estornar no gateway real. O `pk_live_` indica ambiente de produção, não sandbox.

**Impacto:** comprometimento financeiro direto e do banco de produção.

**Correção:** mover para variáveis de ambiente / secret manager; rotacionar as chaves que já vazaram.

## 2.3 — [CRITICAL] Dados sensíveis de cartão logados em texto puro
**Onde:** `AppManager.js:45` — `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`.

**Por que é um problema:** o número do cartão de crédito (`cc`) e a chave do gateway são gravados nos logs. Isso viola PCI-DSS diretamente — dados de cartão nunca podem ser logados. Logs costumam ser agregados/retidos, multiplicando a exposição.

**Impacto:** vazamento de dados de cartão, violação regulatória (PCI-DSS).

**Correção:** nunca logar PAN de cartão nem chaves; tokenizar o cartão via gateway e logar apenas um id de transação.

## 2.4 — [CRITICAL] "Criptografia" de senha caseira e quebrada (`badCrypto`)
**Onde:** `utils.js:17-23` (`badCrypto`) e uso em `AppManager.js:68`.

**Por que é um problema:** a função faz base64 repetido e trunca em 10 chars — não é hash criptográfico. Base64 é reversível, o truncamento gera colisões absurdas, e não há salt. Além disso a senha default `"123456"` é aplicada quando `p` é vazio. É segurança teatral.

**Impacto:** senhas trivialmente recuperáveis; contas comprometidas em vazamento.

**Correção:** `bcrypt`/`argon2` com salt. Nunca inventar hash próprio.

## 2.5 — [HIGH] Callback hell / Pyramid of Doom no checkout
**Onde:** `AppManager.js:37-77` — `db.get` dentro de `db.get` dentro de `db.run` dentro de `db.run`... aninhamento de 5+ níveis com tratamento de erro repetido em cada callback.

**Por que é um problema:** o fluxo assíncrono em callbacks aninhados é ilegível e frágil. O tratamento de erro é copiado em cada nível, e não há transação: se o `INSERT payments` falhar após o `INSERT enrollments` ter sucesso (`:50-56`), a matrícula fica órfã, sem rollback.

**Impacto:** dados inconsistentes (matrícula sem pagamento), manutenção penosa.

**Correção:** usar `async/await` com driver baseado em Promise, envolver o checkout numa transação (`BEGIN/COMMIT/ROLLBACK`).

## 2.6 — [HIGH] Regra de aprovação de pagamento fake baseada no número do cartão
**Onde:** `AppManager.js:47` — `let status = cc.startsWith("4") ? "PAID" : "DENIED"`.

**Por que é um problema:** decide "pago" só porque o cartão começa com 4 (bandeira Visa). Não há integração real com gateway, nem verificação de fundos. É lógica de negócio crítica embutida de forma incorreta no controller.

**Impacto:** matrículas "pagas" sem cobrança real; perda financeira.

**Correção:** integração real com o gateway (assíncrona), status derivado da resposta da transação, não do prefixo do cartão.

## 2.7 — [HIGH] Exclusão de usuário deixa órfãos (sem integridade referencial)
**Onde:** `AppManager.js:131-137` — `DELETE FROM users` sem remover `enrollments`/`payments`; a própria resposta admite: *"as matrículas e pagamentos ficaram sujos no banco"*.

**Por que é um problema:** viola integridade referencial. As tabelas não têm FK com `ON DELETE`, e o código não limpa dependências. Fica lixo apontando para um usuário inexistente.

**Impacto:** dados órfãos, relatórios financeiros incorretos, corrupção lógica.

**Correção:** foreign keys com cascade apropriado **ou** exclusão transacional das dependências; considerar soft-delete.

## 2.8 — [MEDIUM] Relatório financeiro com N+1 assíncrono e contadores manuais
**Onde:** `AppManager.js:80-129` — para cada curso, uma query de enrollments; para cada enrollment, uma de user e outra de payment, com "contadores pendentes" (`coursesPending`, `enrPending`) para saber quando responder.

**Por que é um problema:** é N+1 elevado ao cubo, orquestrado com contadores manuais frágeis — qualquer erro em um callback trava a contagem e a resposta nunca é enviada (ou é enviada incompleta). Não há tratamento se `err` vier preenchido no meio.

**Impacto:** performance ruim, respostas que podem nunca chegar, difícil manter.

**Correção:** uma query com `JOIN`/agregação (`SUM`, `GROUP BY`) resolvendo tudo no banco; ou `Promise.all` com async/await.

## 2.9 — [MEDIUM] Nomes de campos/variáveis crípticos e sem validação de entrada
**Onde:** `AppManager.js:29-35` — `usr`, `eml`, `pwd`, `c_id`, `card` extraídos do body; validação só checa presença (`if (!u || !e ...)`), sem formato de e-mail, sem validar cartão.

**Por que é um problema:** nomes abreviados prejudicam a leitura; a ausência de validação real deixa passar dados malformados que só vão falhar lá no banco. Falta uma camada de validação (schema).

**Impacto:** dados sujos, erros tardios difíceis de rastrear.

**Correção:** nomes descritivos, validação por schema (ex: `joi`/`zod`) antes de tocar no banco.

## 2.10 — [LOW] Estado global mutável exportado e nunca usado
**Onde:** `utils.js:9-10,25` — `globalCache = {}` e `totalRevenue = 0` globais, exportados; `logAndCache` escreve em `globalCache` sem qualquer expiração; `totalRevenue` é importado em `AppManager.js:2` mas nunca usado.

**Por que é um problema:** estado global mutável cria acoplamento oculto e cresce sem limite (memory leak em `globalCache`). `totalRevenue` importado sem uso é código morto que confunde.

**Impacto:** vazamento de memória, acoplamento, ruído no código.

**Correção:** remover o cache global (ou usar um cache com TTL/escopo); remover imports/exports não utilizados.

## 2.11 — [LOW] Banco em memória perde tudo a cada restart
**Onde:** `AppManager.js:7` — `new sqlite3.Database(':memory:')`.

**Por que é um problema:** todos os dados (usuários, matrículas, pagamentos) somem quando o processo reinicia. Aceitável em teste, mas aqui é o "banco" da aplicação, inclusive com dados de pagamento.

**Impacto:** perda total de dados a cada deploy/restart.

**Correção:** arquivo persistente ou banco real; `:memory:` só para testes.

---

# Projeto 3 — `task-manager-api` (Python/Flask — Task Manager)

Este projeto **já tem** separação de camadas (`models/`, `routes/`, `services/`, `utils/`) — mas isso não garante qualidade. Os problemas aqui são mais sutis: segurança, duplicação e regra de negócio no lugar errado.

## 3.1 — [CRITICAL] Hash de senha com MD5 (algoritmo quebrado)
**Onde:** `models/user.py:29` (`set_password`) e `:32` (`check_password`) — `hashlib.md5(pwd.encode()).hexdigest()`.

**Por que é um problema:** MD5 é criptograficamente quebrado, rápido de bruteforce e sem salt. Rainbow tables recuperam senhas comuns instantaneamente. Para senha, MD5 é praticamente texto puro.

**Impacto:** senhas recuperáveis em caso de vazamento do banco.

**Correção:** `bcrypt`/`argon2`/`werkzeug.security` com salt e custo configurável.

## 3.2 — [CRITICAL] Senha exposta no `to_dict()` do usuário
**Onde:** `models/user.py:16-25` — `to_dict()` inclui `'password': self.password`; propaga para `GET /users/<id>` (`user_routes.py:33`), criação (`:85`) e login (`:209`).

**Por que é um problema:** a serialização padrão do usuário devolve o hash da senha em toda resposta que usa `to_dict()`. Mesmo sendo hash, expor o hash facilita ataques offline e é vazamento de dado que nunca deveria sair do servidor.

**Impacto:** hash de senha trafega para o cliente em várias rotas.

**Correção:** remover `password` do `to_dict()`; se precisar do hash internamente, usar um serializador separado que nunca inclua o campo.

## 3.3 — [CRITICAL] Segredos hardcoded (SECRET_KEY e senha de e-mail)
**Onde:** `app.py:13` (`SECRET_KEY = 'super-secret-key-123'`) e `services/notification_service.py:9-10` (`email_user`/`email_password = 'senha123'`).

**Por que é um problema:** segredos no código-fonte vazam no Git. A senha de SMTP em texto puro permite a qualquer um com o repo enviar e-mails em nome do serviço.

**Impacto:** comprometimento de sessões e da conta de e-mail.

**Correção:** variáveis de ambiente / secret manager para todos os segredos.

## 3.4 — [HIGH] Autenticação fake e sem proteção nas rotas
**Onde:** `user_routes.py:210` — `'token': 'fake-jwt-token-' + str(user.id)`; e **nenhuma** rota (criar/editar/deletar task, deletar usuário, relatórios) exige autenticação.

**Por que é um problema:** o "token" é uma string previsível que não prova nada (não é assinado, não expira). E como nenhum endpoint valida autenticação/autorização, qualquer um deleta usuários (`user_routes.py:134`) ou lê relatórios. O `is_admin()` (`user.py:34`) existe mas nunca é chamado.

**Impacto:** qualquer cliente executa ações privilegiadas sem login.

**Correção:** JWT real assinado com expiração; middleware/decorator de autenticação e autorização por role nas rotas sensíveis.

## 3.5 — [HIGH] Lógica de negócio duplicada e espalhada (`is_overdue`)
**Onde:** o cálculo de "overdue" (due_date no passado e status != done/cancelled) está reimplementado inline em pelo menos 5 lugares:
`task_routes.py:30-39`, `:71-80`, `:284-287`; `user_routes.py:171-180`; `report_routes.py:34-37` e `:132-135`. Existe `Task.is_overdue()` em `models/task.py:50-60` mas **quase nunca é usado**.

**Por que é um problema:** a mesma regra de negócio, copiada em vários arquivos com aninhamento `if` profundo. Se a definição de "atrasado" mudar, é preciso caçar 5+ cópias — e elas já podem divergir. Viola DRY e "regra de negócio pertence ao model/service".

**Impacto:** inconsistência garantida no médio prazo, manutenção cara.

**Correção:** usar sempre `task.is_overdue()`; remover as cópias inline. Idealmente centralizar num service.

## 3.6 — [MEDIUM] N+1 na listagem de tasks e em relatórios
**Onde:** `task_routes.py:41-57` — para cada task, `User.query.get()` e `Category.query.get()` individuais. Também `report_routes.py:53-68` — para cada usuário, uma nova `Task.query.filter_by(user_id=...)`.

**Por que é um problema:** com N tasks, faz 2N queries extras. Os relacionamentos já existem (`Task.user`, `Task.category` em `task.py:20-21`), mas o código ignora e refaz queries manuais. SQLAlchemy resolveria com eager loading (`joinedload`).

**Impacto:** performance degrada linearmente com o volume.

**Correção:** `Task.query.options(joinedload(Task.user), joinedload(Task.category))` ou usar os relacionamentos já mapeados.

## 3.7 — [MEDIUM] Serialização de task duplicada (model vs. rotas)
**Onde:** `Task.to_dict()` existe em `task.py:23-36`, mas `task_routes.py:16-59` e `user_routes.py:162-181` remontam o dicionário campo a campo manualmente, em vez de usar `to_dict()`.

**Por que é um problema:** três formas diferentes de serializar a mesma entidade, que já divergem (uma inclui `overdue`, outra `user_name`, outra campos parciais). Duplicação clássica; mudar um campo exige editar vários lugares.

**Impacto:** respostas inconsistentes entre endpoints, manutenção cara.

**Correção:** uma única fonte de serialização (o `to_dict()` do model, ou um schema marshmallow), estendida com campos derivados quando necessário.

## 3.8 — [MEDIUM] Validação de task duplicada em 3 lugares
**Onde:** as mesmas regras (status válido, prioridade 1–5, título 3–200) aparecem em `task_routes.py:96-114` (create), `:166-184` (update) **e** em `utils/helpers.py:57-108` (`process_task_data`, que existe mas não é usado pelas rotas).

**Por que é um problema:** há um utilitário de validação pronto (`process_task_data`) que as rotas ignoram, reimplementando tudo à mão e duplicando entre create/update. DRY violado e o utilitário vira código morto.

**Impacto:** inconsistência de validação e esforço de manutenção triplicado.

**Correção:** usar `process_task_data` (ou um schema) nas duas rotas; remover a duplicação.

## 3.9 — [LOW] `except:` "pelado" engolindo erros
**Onde:** `task_routes.py:62` (`except:` no `get_tasks`), `:236`; `helpers.py:46-50` (`parse_date` com `try/except:` aninhado); `report_routes`/`user_routes` com `except:` sem tipo.

**Por que é um problema:** `except:` sem tipo captura **tudo**, inclusive `KeyboardInterrupt`/`SystemExit`, e mascara a causa real do erro (retorna "Erro interno" genérico sem log). Dificulta muito o debug.

**Impacto:** erros silenciados, diagnóstico quase impossível.

**Correção:** capturar exceções específicas (`except Exception as e:` no mínimo) e logar `e`.

## 3.10 — [LOW] Imports não usados e `print` como log
**Onde:** `app.py:7` (`import os, sys, json, datetime` — `os/sys/json` sem uso), `task_routes.py:7` (`json, os, sys, time` sem uso), `helpers.py:1-7` (`os, json, sys, math, hashlib` sem uso); e `print(...)` como log em `task_routes.py:149,219,234`, `user_routes.py:83,147`.

**Por que é um problema:** imports mortos poluem e sugerem dependências inexistentes; `print` não é logging (sem nível/timestamp/destino). São ruídos de baixa gravidade, mas indicam falta de padronização.

**Impacto:** legibilidade e observabilidade ruins.

**Correção:** remover imports não usados (linter: flake8/ruff) e trocar `print` por `logging`.

## 3.11 — [LOW] `type(x) == list` e comparações booleanas verbosas
**Onde:** `helpers.py:103` e `task_routes.py:141,210` (`if type(tags) == list`); `user.py:34-38`, `task.py:38-48` (`if ...: return True else: return False`).

**Por que é um problema:** `type(x) == list` deveria ser `isinstance(x, list)` (mais correto e pythônico). Os `if/else` que só retornam `True/False` podem ser a própria expressão booleana. São detalhes de idiomática/legibilidade.

**Correção:** `isinstance(tags, list)`; `return self.role == 'admin'`.

---

# Resumo por projeto

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| 1 — code-smells-project | 4 | 3 | 3 | 3 | 13 |
| 2 — ecommerce-api-legacy | 4 | 3 | 2 | 2 | 11 |
| 3 — task-manager-api | 3 | 2 | 3 | 3 | 11 |

> Todos os projetos superam o mínimo exigido (≥5 problemas, com ≥1 CRITICAL/HIGH, ≥2 MEDIUM e ≥2 LOW).
