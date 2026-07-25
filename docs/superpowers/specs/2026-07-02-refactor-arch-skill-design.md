# Design — Skill `refactor-arch`

> Skill de auditoria e refatoração arquitetural para o desafio de MBA. Analisa, audita e
> refatora qualquer projeto backend para o padrão MVC, de forma agnóstica de tecnologia.
> Baseada no estilo das skills do repositório [sdd-skills](https://github.com/dayvisonassis/sdd-skills)
> (persona stack-agnostic, seções canônicas, tabelas com `arquivo:linha`, SKILL.md enxuto + `references/` sob demanda).

## Decisões de design (confirmadas)

| Decisão | Escolha |
|---|---|
| Ferramenta | Claude Code — skill em `.claude/skills/refactor-arch/`, invocada por `/refactor-arch` |
| Granularidade de references | 5 arquivos, mapeamento 1:1 com as áreas de conhecimento do enunciado |
| Idioma | SKILL.md + references em **inglês**; relatórios de auditoria e README em **português** |
| Estratégia da Fase 3 | **Adaptativa por contexto**: monolito → estrutura MVC completa; projeto já em camadas → correção + melhoria sem reescrever |

## 1. Arquitetura geral

Skill de 3 fases sequenciais. O `SKILL.md` é o núcleo enxuto (orquestra as fases, define o gate de confirmação e o self-audit); os 5 arquivos em `references/` carregam o conhecimento de domínio sob demanda.

```
.claude/skills/refactor-arch/
├── SKILL.md                        # núcleo: persona, 3 fases, gate de confirmação, self-audit, índice de referências
└── references/
    ├── project-analysis.md         # Fase 1 — heurísticas de detecção (linguagem/framework/DB/arquitetura)
    ├── anti-patterns-catalog.md    # Fase 2 — catálogo (≥8 anti-patterns + APIs deprecated) com sinais e severidade
    ├── report-template.md          # Fase 2 — formato canônico do relatório de auditoria (PT)
    ├── architecture-guidelines.md  # Fase 3 — regras do MVC alvo (Models, Views/Routes, Controllers)
    └── refactoring-playbook.md     # Fase 3 — ≥8 transformações com código antes/depois
```

O SKILL.md segue as seções canônicas do padrão `sdd-skills`:
**Persona & Scope → Objective → Inputs → The 3 Phases → Criteria → Negative Instructions → Error Handling → Workflow → Self-Audit Checklist → References Index.**

## 2. As 3 fases

| Fase | Entrada | Saída | Modifica código? | Reference principal |
|---|---|---|---|---|
| **1 — Análise** | codebase | resumo impresso (stack, framework, domínio, arquitetura, contagem de arquivos e tabelas) | ❌ | `project-analysis.md` |
| **2 — Auditoria** | resultado F1 + catálogo | relatório de auditoria estruturado (PT) ordenado por severidade + **pausa pedindo confirmação `[y/n]`** | ❌ | `anti-patterns-catalog.md`, `report-template.md` |
| **3 — Refatoração** | relatório aprovado + playbook | estrutura MVC + validação (boot da app + endpoints respondendo) | ✅ (só após `y`) | `architecture-guidelines.md`, `refactoring-playbook.md` |

### Gate de confirmação (obrigatório)

A Fase 3 **só** executa após o humano digitar `y`. A Fase 2 termina imprimindo o total de findings e a pergunta `Proceed with refactoring (Phase 3)? [y/n]`. Se `n`, a skill encerra sem tocar em nenhum arquivo. Isso vem direto do enunciado e do princípio "análise nunca modifica" das skills `architecture-analyzer`/`deep-analyzer`.

## 3. Estratégia adaptativa da Fase 3

A skill inspeciona o estado atual antes de refatorar e escolhe a profundidade:

- **Monolito** (ex: `code-smells-project`, `ecommerce-api-legacy`) → cria a estrutura MVC completa: `config/`, `models/`, `views/` (ou `routes/`), `controllers/`, `middlewares/`, entry point (composition root).
- **Já em camadas** (ex: `task-manager-api`) → corrige os anti-patterns encontrados e melhora a estrutura existente **sem** reescrever o que já está adequado (ex: extrai services, remove senha da serialização, centraliza `is_overdue`).

Em ambos os casos o resultado deve respeitar as `architecture-guidelines.md` e preservar o contrato dos endpoints originais.

## 4. Conteúdo-chave dos references

### `anti-patterns-catalog.md` (≥ 8 anti-patterns, 4 severidades + APIs deprecated)

Extraído da análise manual real dos 3 projetos (ver `explicacao_problemas_encontrados.md`). Cobertura mínima:

| Anti-pattern | Severidade | Sinal de detecção |
|---|---|---|
| SQL Injection (concatenação de string em query) | CRITICAL | `execute("... " + var)` / template string com input em SQL |
| Hardcoded secrets | CRITICAL | `SECRET_KEY=`, `pk_live_`, senha/chave literal no código |
| Senha insegura (texto puro / MD5 / hash caseiro) | CRITICAL | `md5(`, senha gravada/comparada sem hash forte |
| God Class / God Method | CRITICAL/HIGH | classe/arquivo com DB + rotas + regra de negócio juntos |
| Business logic na camada errada | HIGH | regra de negócio dentro de model/controller |
| Global mutable state | HIGH | conexão/cache global reaproveitado entre requests |
| N+1 queries | MEDIUM | query dentro de loop `for`/`forEach` |
| Validação/serialização duplicada (DRY) | MEDIUM | mesma validação repetida em create/update |
| Magic numbers / listas mágicas | LOW | número/lista sem constante nomeada |
| `print`/`console.log` como log + `except:` genérico | LOW | ausência de logger, catch sem tipo |

Seção dedicada a **APIs deprecated**: `hashlib.md5` para senha, `datetime.utcnow()` (deprecated em Python 3.12+), callbacks do `sqlite3` (vs. Promise/async), `type(x) == list` (vs. `isinstance`).

### `refactoring-playbook.md` (≥ 8 transformações, antes/depois)

Cada transformação usa exemplos reais dos 3 projetos:
1. Concatenação SQL → query parametrizada
2. Secret hardcoded → variável de ambiente
3. Senha texto puro/MD5 → `bcrypt`/`werkzeug.security`
4. God Class → separação em camadas MVC
5. Regra de negócio no controller/model → Service dedicado
6. N+1 → JOIN / eager loading
7. Conexão global → conexão por request / injeção
8. Validação duplicada → validador/schema único
9. Callback hell → `async/await` + transação
10. `print` → `logging` + error handler centralizado

## 5. Validação (Fase 3)

Inspirado no doc `requisitos_para_criar_skill.md` (health check como apoio ao harness), a skill valida objetivamente após refatorar:
- a aplicação **inicia sem erros** (boot);
- os **endpoints originais respondem** (o `/health` e as rotas mapeadas na Fase 1);
- **zero anti-patterns** remanescentes do relatório.

Reporta um checklist ✓/✗ ao final (formato do exemplo do enunciado, PHASE 3: REFACTORING COMPLETE).

## 6. Reuso da base `sdd-skills`

| Padrão reaproveitado | Origem |
|---|---|
| Frontmatter `name` + `description` orientado a "quando usar" | todas as skills |
| Seções canônicas (Persona/Objective/Inputs/Criteria/Negative/Workflow) | `architecture-analyzer`, `deep-analyzer` |
| Tabela de anti-patterns com severidade e `arquivo:linha` | `architecture-analyzer` §9.2, `deep-analyzer` §7 |
| Persona "Expert Architect, stack-agnostic" + análise ≠ modificação | `architecture-analyzer`, `deep-analyzer` |
| SKILL.md enxuto + `references/` sob demanda | `docs/requisitos_para_criar_skill.md` §4 e §7 |
| Validação objetiva via health check | `docs/requisitos_para_criar_skill.md` §2 e §3 |

## 7. Entregáveis do desafio (contexto — fora do escopo deste spec de criação da skill)

Após a skill pronta, a execução gera: código refatorado dos 3 projetos, `reports/audit-project-{1,2,3}.md`, e as seções B/C/D do README. Este spec cobre a **criação da skill**; a execução nos projetos será um passo posterior.

## Critérios de aceite do design

- [ ] `SKILL.md` implementa as 3 fases com gate de confirmação antes da Fase 3.
- [ ] 5 arquivos em `references/` cobrindo as 5 áreas obrigatórias.
- [ ] Catálogo com ≥ 8 anti-patterns nas 4 severidades + seção de APIs deprecated.
- [ ] Playbook com ≥ 8 transformações com exemplos antes/depois.
- [ ] Skill agnóstica — sem acoplamento a um projeto específico (testável nos 3).
- [ ] SKILL.md enxuto (~algumas centenas de linhas), detalhes nos references.
