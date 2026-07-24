# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# 📋 Entrega do Desafio

> A partir daqui começa a documentação da solução. As seções acima são o enunciado original do desafio.

## Análise Manual

Análise manual dos 3 projetos legados. Para cada projeto foram identificados os problemas de maior impacto arquitetural, classificados por severidade (CRITICAL / HIGH / MEDIUM / LOW). A explicação didática detalhada de **cada** achado — com trecho de código, causa e correção — está em [explicacao_problemas_encontrados.md](explicacao_problemas_encontrados.md).

### Projeto 1 — `code-smells-project` (Python/Flask — API de E-commerce)

Monolito com pastas nomeadas como camadas (`controllers`, `models`), mas sem separação real de responsabilidades.

| # | Severidade | Problema | Localização |
|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection generalizado (queries montadas por concatenação de strings) | `models.py` (28, 48-49, 110, 291, ...) |
| 2 | **CRITICAL** | Endpoint que executa SQL arbitrário do cliente + reset de banco sem auth | `app.py:59-78`, `app.py:47-57` |
| 3 | **CRITICAL** | `SECRET_KEY` hardcoded e exposta na resposta do `/health` | `app.py:7`, `controllers.py:289` |
| 4 | **CRITICAL** | Senhas em texto puro (armazenadas, comparadas e retornadas ao cliente) | `models.py:110,127-128,83`; `database.py:76-78` |
| 5 | **HIGH** | Conexão de banco global mutável compartilhada entre threads | `database.py:4-11` |
| 6 | **HIGH** | Regra de negócio (estoque/total) dentro da camada de dados (`criar_pedido`) | `models.py:133-169` |
| 7 | **HIGH** | Efeitos colaterais (e-mail/SMS/push via `print`) dentro do controller | `controllers.py:208-210,248-250` |
| 8 | **MEDIUM** | Problema N+1 na listagem de pedidos | `models.py:171-201,203-233` |
| 9 | **MEDIUM** | Validação duplicada entre criar e atualizar produto | `controllers.py:24-96` |
| 10 | **MEDIUM** | `DEBUG=True` fixo + `host=0.0.0.0` (Werkzeug debugger exposto → RCE) | `app.py:8,88` |
| 11 | **LOW** | Concatenação `+ str(...)` em vez de f-strings | `controllers.py` (diversos) |
| 12 | **LOW** | Magic numbers e listas mágicas (categorias, status, faixas de desconto) | `controllers.py:47-52,242`; `models.py:257-262` |
| 13 | **LOW** | `print` como log + `except Exception` genérico vazando detalhes | `controllers.py` (diversos) |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API com checkout)

"Frankenstein LMS": uma God Class (`AppManager`) com conexão, schema, seed, rotas e regra de negócio, tudo junto.

| # | Severidade | Problema | Localização |
|---|---|---|---|
| 1 | **CRITICAL** | God Class concentrando DB, seed, rotas e regra de negócio | `AppManager.js:4-141` |
| 2 | **CRITICAL** | Segredos de produção hardcoded (senha de DB, chave `pk_live` do gateway) | `utils.js:1-7` |
| 3 | **CRITICAL** | Número de cartão e chave do gateway logados em texto puro (viola PCI-DSS) | `AppManager.js:45` |
| 4 | **CRITICAL** | "Criptografia" caseira de senha (base64 truncado, sem salt) | `utils.js:17-23`; `AppManager.js:68` |
| 5 | **HIGH** | Callback hell no checkout, sem transação (matrícula órfã se pagamento falha) | `AppManager.js:37-77` |
| 6 | **HIGH** | Aprovação de pagamento fake baseada no prefixo do cartão | `AppManager.js:47` |
| 7 | **HIGH** | Exclusão de usuário deixa matrículas/pagamentos órfãos | `AppManager.js:131-137` |
| 8 | **MEDIUM** | Relatório financeiro com N+1 assíncrono e contadores manuais frágeis | `AppManager.js:80-129` |
| 9 | **MEDIUM** | Nomes crípticos (`usr`, `eml`, `cc`) e ausência de validação de entrada | `AppManager.js:29-35` |
| 10 | **LOW** | Estado global mutável exportado (`globalCache`, `totalRevenue`) e código morto | `utils.js:9-10,25` |
| 11 | **LOW** | Banco `:memory:` perde todos os dados a cada restart | `AppManager.js:7` |

### Projeto 3 — `task-manager-api` (Python/Flask — Task Manager)

Já possui separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas com problemas de segurança, duplicação e regra de negócio no lugar errado.

| # | Severidade | Problema | Localização |
|---|---|---|---|
| 1 | **CRITICAL** | Hash de senha com MD5 (algoritmo quebrado, sem salt) | `models/user.py:29,32` |
| 2 | **CRITICAL** | Senha (hash) exposta no `to_dict()` e propagada em várias rotas | `models/user.py:16-25`; `user_routes.py:33,85,209` |
| 3 | **CRITICAL** | Segredos hardcoded (`SECRET_KEY`, senha de SMTP) | `app.py:13`; `notification_service.py:9-10` |
| 4 | **HIGH** | Autenticação fake (`fake-jwt-token-`) e nenhuma rota protegida | `user_routes.py:210`; rotas em geral |
| 5 | **HIGH** | Regra de negócio `is_overdue` duplicada inline em 5+ lugares | `task_routes.py:30-39,71-80,284-287`; `user_routes.py:171-180`; `report_routes.py:34-37,132-135` |
| 6 | **MEDIUM** | N+1 na listagem de tasks e nos relatórios (ignora relacionamentos mapeados) | `task_routes.py:41-57`; `report_routes.py:53-68` |
| 7 | **MEDIUM** | Serialização de task duplicada (model `to_dict()` vs. rotas montando à mão) | `task.py:23-36`; `task_routes.py:16-59`; `user_routes.py:162-181` |
| 8 | **MEDIUM** | Validação de task duplicada em 3 lugares (util `process_task_data` ignorado) | `task_routes.py:96-114,166-184`; `helpers.py:57-108` |
| 9 | **LOW** | `except:` "pelado" engolindo e mascarando erros | `task_routes.py:62,236`; `helpers.py:46-50` |
| 10 | **LOW** | Imports não usados e `print` como log | `app.py:7`; `task_routes.py:7,149,219`; `helpers.py:1-7` |
| 11 | **LOW** | `type(x) == list` (em vez de `isinstance`) e `if/else` retornando booleano | `helpers.py:103`; `user.py:34-38`; `task.py:38-48` |

### Resumo dos achados

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| 1 — code-smells-project | 4 | 3 | 3 | 3 | 13 |
| 2 — ecommerce-api-legacy | 4 | 3 | 2 | 2 | 11 |
| 3 — task-manager-api | 3 | 2 | 3 | 3 | 11 |

Todos os projetos atendem ao mínimo exigido pelo desafio: ≥ 5 problemas, sendo ≥ 1 CRITICAL/HIGH, ≥ 2 MEDIUM e ≥ 2 LOW.

## Construção da Skill

### Decisões de design

A skill vive em `.claude/skills/refactor-arch/` e segue a anatomia recomendada: um **`SKILL.md` enxuto**
(orquestrador, ~130 linhas) + **5 arquivos de referência** carregados sob demanda, cada um mapeando 1:1
com uma das áreas de conhecimento obrigatórias:

| Arquivo | Área de conhecimento | Papel |
|---|---|---|
| `references/project-analysis.md` | Análise de projeto | Heurísticas de detecção (linguagem, framework, banco, arquitetura) + contrato de saída da Fase 1 |
| `references/anti-patterns-catalog.md` | Catálogo de anti-patterns | 12 anti-patterns (`AP-01`..`AP-12`) com sinal de detecção + severidade + seção de APIs deprecated |
| `references/report-template.md` | Template de relatório | Formato do relatório da Fase 2 (PT), ordenado por severidade, com o gate `[y/n]` |
| `references/architecture-guidelines.md` | Guidelines de arquitetura | Regras das camadas MVC + estratégia adaptativa |
| `references/refactoring-playbook.md` | Playbook de refatoração | 12 transformações com código antes/depois (Python **e** JS) |

Escolhas principais:

- **`SKILL.md` como prompt, references como conhecimento.** O `SKILL.md` só orquestra as 3 fases, define
  o gate de confirmação e o self-audit; o conhecimento pesado (sinais de detecção, exemplos de código)
  fica nas references, carregadas quando a fase precisa.
- **Idioma:** skill e references em **inglês** (linguagem técnica, reaproveitável); relatórios de
  auditoria e este README em **português**.
- **Gate de confirmação obrigatório.** As Fases 1 e 2 são read-only; a Fase 3 só modifica arquivos após
  o humano digitar `y`. Isso está escrito explicitamente no `SKILL.md` e foi respeitado nas 3 execuções.
- **Estratégia adaptativa** (ver seção C): monolito → scaffold MVC completo; projeto já em camadas →
  correção pontual + camadas faltantes, sem reescrever o que já está bom.

### Anti-patterns incluídos e por quê

O catálogo tem **12 anti-patterns nas 4 severidades**, todos extraídos dos problemas reais dos 3
projetos-alvo (nada inventado):

| ID | Anti-pattern | Severidade | Presente em |
|---|---|---|---|
| AP-01 | SQL Injection por concatenação | CRITICAL | Projeto 1 |
| AP-02 | Segredos hardcoded / vazados | CRITICAL | Projetos 1, 2, 3 |
| AP-03 | Senha insegura (texto puro / MD5 / hash caseiro) | CRITICAL | Projetos 1, 2, 3 |
| AP-04 | God Class / God Method | CRITICAL | Projeto 2 |
| AP-05 | Regra de negócio na camada errada | HIGH | Projetos 1, 2 |
| AP-06 | Estado global mutável | HIGH | Projetos 1, 2 |
| AP-07 | Autenticação ausente / fake | HIGH | Projeto 3 |
| AP-08 | N+1 queries | MEDIUM | Projetos 1, 2, 3 |
| AP-09 | Validação/serialização duplicada | MEDIUM | Projetos 1, 3 |
| AP-10 | Magic numbers / listas mágicas | LOW | Projetos 1, 2 |
| AP-11 | `print`/`console.log` como log + `except` pelado | LOW | Projetos 1, 3 |
| AP-12 | Falta de transação / integridade referencial | HIGH | Projeto 2 |

Além disso, uma seção dedicada a **APIs deprecated** cobre `hashlib.md5` para senha, `datetime.utcnow()`
(deprecated no Python 3.12+), callbacks aninhados do `sqlite3` (vs. async/await), `type(x) == list`
(vs. `isinstance`), `app.run(debug=True)` em produção e SQLite `:memory:` como banco da aplicação —
cada um com o equivalente moderno recomendado.

### Como a skill é agnóstica de tecnologia

- A detecção parte de **sinais concretos** (arquivos de manifesto, imports, statements SQL), não de um
  projeto específico — Python/Flask e Node/Express estão cobertos explicitamente, mas as heurísticas
  generalizam.
- O catálogo descreve os anti-patterns por **sinal greppável** independente de linguagem (ex.: "query
  string montada com input"), e o playbook traz exemplos **em Python e em JS**.
- As guidelines de arquitetura mapeam as mesmas camadas MVC para os dois stacks (blueprint Flask ==
  router Express; `werkzeug.security` == scrypt/bcrypt; error handler do Flask == middleware de erro
  do Express).
- Prova prática: a **mesma skill, copiada sem alteração**, rodou nos 3 projetos (2 Flask + 1 Express)
  e produziu relatório + refatoração válidos em todos.

### Desafios encontrados e como resolvi

- **Preservar o contrato dos endpoints × corrigir a falha.** No Projeto 1, os endpoints `/admin/query`
  e `/admin/reset-db` **são** a vulnerabilidade — removê-los é a correção. "Endpoints originais
  respondem" passou a significar os endpoints legítimos de negócio, que foram todos preservados.
- **Adicionar autenticação sem quebrar as rotas.** No Projeto 3, autenticar muda o contrato de rotas
  sensíveis. Resolvi protegendo apenas as rotas realmente sensíveis (delete de usuário → admin;
  relatórios → autenticado) e validando com login → token; as rotas públicas seguem abertas.
- **Aprovação de pagamento fake (Projeto 2).** Sem gateway real, isolei a decisão em um `paymentService`
  claramente sinalizado como *stub* — corrige o acoplamento arquitetural (regra fora do controller) sem
  fingir uma cobrança real.
- **Hash de senha sem dependência nova.** Em vez de instalar `bcrypt` (nativo, exige build no Windows),
  usei `werkzeug.security` (Python, já vem com Flask) e `node:crypto` scrypt (Node, stdlib) — salgados e
  fortes, zero instalação extra.
- **Ambiente offline/proxy.** `pip` batia em erro de certificado (proxy corporativo); resolvido com
  `--trusted-host`. Validação HTTP no Windows sofria com esgotamento de sockets; usei o `test_client`
  do Flask e um cliente Node com keep-alive para exercitar todo o stack de forma determinística.

## Resultados

### Resumo dos relatórios de auditoria

Relatórios completos em [reports/audit-project-1.md](reports/audit-project-1.md),
[reports/audit-project-2.md](reports/audit-project-2.md) e
[reports/audit-project-3.md](reports/audit-project-3.md).

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 | 3 | 3 | 3 | 13 |
| 2 — ecommerce-api-legacy | Node/Express | 4 | 3 | 2 | 2 | 11 |
| 3 — task-manager-api | Python/Flask (SQLAlchemy) | 3 | 2 | 3 | 3 | 11 |

Todos superam o mínimo (≥ 5 findings, ≥ 1 CRITICAL/HIGH) exigido pelos critérios de aceite.

### Comparação antes/depois da estrutura

**Projeto 1 — `code-smells-project` (monolito → MVC completo)**

```
ANTES                          DEPOIS
app.py                         app.py                     (entry point)
controllers.py   ─────►        src/config/                (settings, constants — env)
models.py                      src/database/connection.py (conexão por request)
database.py                    src/models/                (SQL parametrizado)
                               src/services/              (regra de negócio + transação)
                               src/controllers/           (orquestração)
                               src/views/routes.py        (blueprint)
                               src/middlewares/           (error handler)
```

**Projeto 2 — `ecommerce-api-legacy` (God Class → MVC completo)**

```
ANTES                          DEPOIS
src/app.js                     src/app.js                 (composition root)
src/AppManager.js  ─────►      src/config/                (env)
src/utils.js                   src/database/connection.js (arquivo persistente + Promise)
                               src/models/                (user/course/enrollment/payment/audit)
                               src/services/              (checkout+transação, report, user, payment stub)
                               src/controllers/           (checkout/report/user)
                               src/routes/                (router)
                               src/middlewares/           (error handler)
                               src/utils/crypto.js        (scrypt)
```

**Projeto 3 — `task-manager-api` (já em camadas → correção adaptativa)**

```
ANTES                          DEPOIS (camadas adicionadas em negrito)
models/ routes/                models/ routes/ services/ utils/  (mantidos e corrigidos)
services/ utils/   ─────►      **config/**                       (settings via env)
                               **middlewares/**                  (auth + error handler)
                               services/auth_service.py          (token assinado)
                               services/task_service.py          (eager loading, sem N+1)
```

### Comportamento em stacks diferentes

- A **mesma skill** detectou corretamente Python/Flask (projetos 1 e 3) e Node/Express (projeto 2),
  inclusive distinguindo o projeto 3 como "já em camadas" e aplicando a estratégia adaptativa.
- O gate de confirmação `[y/n]` funcionou nos 3 — nenhum arquivo foi tocado antes do `y`.
- As transformações do playbook se traduziram bem entre linguagens (query parametrizada em SQLite Python
  e Node; hash salgado com `werkzeug.security` e `node:crypto`; error handler do Flask e middleware do
  Express).

### Logs das aplicações rodando após a refatoração

**Projeto 1 (Flask):**
```
GET /health  → 200 {"counts":{"pedidos":0,"produtos":10,"usuarios":3},"status":"ok","versao":"1.0.0"}   (sem secret_key)
GET /usuarios→ 200 [{...,"email":"admin@loja.com","tipo":"admin"}]                                        (sem senha)
POST /login (senha correta)→ 200 ;  (SQL injection ' OR '1'='1)→ 401
POST /pedidos (2 itens)→ 201 {"pedido_id":1,"total":6269.69} ; (estoque insuficiente)→ 400 (rollback)
POST /admin/query / /admin/reset-db → 404 (removidos)
```

**Projeto 2 (Express):**
```
POST /api/checkout (card 4...)→ 200 {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout (card 5...)→ 400 "Pagamento recusado"
GET /api/admin/financial-report→ 200 [{"course":"Clean Architecture","revenue":997,...}]  (JOIN, sem N+1)
DELETE /api/users/1→ 200 (transacional; revenue do curso do usuário zera, sem órfãos)
Log do servidor: cartão e chave do gateway NÃO aparecem.
```

**Projeto 3 (Flask/SQLAlchemy):**
```
POST /login (admin)→ 200 token assinado "eyJ1aWQiOjEsInJvbGUiOiJhZG1pbiJ9..."  (não é fake-jwt)
GET  /reports/summary (sem token)→ 401 ; (com token admin)→ 200
DELETE /users/3 (token de user comum)→ 403 ; (token admin)→ 200 (transacional)
GET  /tasks→ 200 (joinedload, campo overdue via is_overdue, sem N+1)  ;  /users sem campo password
```

### Checklist de Validação preenchido

Legenda: ✅ atendido nos 3 projetos.

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente        (P1 Python, P2 Node, P3 Python)
- [x] Framework detectado corretamente         (P1 Flask, P2 Express, P3 Flask+SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (E-commerce / LMS / Task Manager)
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nas references
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados       (13 / 11 / 11)
- [x] Detecção de APIs deprecated incluída
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
```

## Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- **Python 3.11+** e **pip** (projetos 1 e 3).
- **Node.js 20+** e **npm** (projeto 2).

### Executar a skill em cada projeto

A skill já está copiada dentro dos 3 projetos. Em cada um, invoque:

```bash
cd code-smells-project     &&  claude "/refactor-arch"
cd ../ecommerce-api-legacy &&  claude "/refactor-arch"
cd ../task-manager-api     &&  claude "/refactor-arch"
```

A skill executa a Fase 1 (análise), a Fase 2 (auditoria) e **pausa** pedindo `[y/n]`. Ao responder `y`,
executa a Fase 3 (refatoração) e valida.

### Rodar e validar cada aplicação refatorada

**Projeto 1 — code-smells-project (Flask):**
```bash
cd code-smells-project
python -m venv venv && ./venv/Scripts/pip install -r requirements.txt   # Linux/Mac: venv/bin/pip
python app.py            # http://127.0.0.1:5000
curl http://127.0.0.1:5000/health
```

**Projeto 2 — ecommerce-api-legacy (Express):**
```bash
cd ecommerce-api-legacy
npm install
npm start                # http://127.0.0.1:3000
curl -X POST http://127.0.0.1:3000/api/checkout -H "Content-Type: application/json" \
  -d '{"usr":"Ana","eml":"ana@x.com","pwd":"senha","c_id":2,"card":"4111222233334444"}'
```

**Projeto 3 — task-manager-api (Flask/SQLAlchemy):**
```bash
cd task-manager-api
python -m venv venv && ./venv/Scripts/pip install -r requirements.txt
python seed.py           # popula o banco
python app.py            # http://127.0.0.1:5000
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}'   # retorna um token assinado
```

> Configuração por variáveis de ambiente (sem segredos no código): `SECRET_KEY`, `FLASK_DEBUG`, `HOST`,
> `PORT`, `DB_PATH`/`DATABASE_URL` (Python) e `PORT`, `DB_PATH`, `DB_PASS`, `PAYMENT_GATEWAY_KEY` (Node).