# Reference — Audit Report Template (Phase 2 output)

The canonical shape of the **Phase 2 audit report**. This is what the skill prints for the human to
review at the confirmation gate, and what gets saved to `reports/audit-project-N.md`.

## Rules for filling it

- The report body is written in **Portuguese** (the reader-facing artifact); this reference is in English.
- **Every finding cites an exact `arquivo:linha`** (a range like `models.py:1-350` is fine).
- Findings are **ordered by severity: CRITICAL → HIGH → MEDIUM → LOW**. Within a severity, group by file.
- The **Summary** line counts findings per severity and must match the number of findings listed.
- Reference the anti-pattern by its catalog ID where useful (e.g. `(AP-01)`), but keep titles human-readable.
- Flag **deprecated APIs** as findings when applicable (see catalog's Deprecated section).
- The report ends with the total and the **mandatory confirmation prompt**. The skill then **stops**.

## Template

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: {project_name}
Stack:   {language} + {framework}
Files:   {n} analyzed | ~{loc} lines of code

## Summary
CRITICAL: {c} | HIGH: {h} | MEDIUM: {m} | LOW: {l}

## Findings

### [CRITICAL] {Título do problema}  ({AP-NN})
File: {arquivo:linha}
Description: {o que está errado, de forma concreta}
Impact: {consequência real — segurança, dados, manutenção, performance}
Recommendation: {correção — referência à transformação do playbook}

### [CRITICAL] {próximo finding CRITICAL}
File: {arquivo:linha}
...

### [HIGH] {...}
...

### [MEDIUM] {...}
...

### [LOW] {...}
...

================================
Total: {N} findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Filled example (excerpt)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] SQL Injection generalizado  (AP-01)
File: models.py:28,48-49,110,291
Description: Queries montadas por concatenação de string com entrada do usuário.
Impact: Bypass de login (' OR '1'='1), vazamento e destruição de dados.
Recommendation: Migrar todas as queries para parâmetros (?, tuplas). Ver Playbook T1.

### [CRITICAL] Endpoint que executa SQL arbitrário + reset sem auth  (AP-02/AP-04)
File: app.py:59-78, app.py:47-57
Description: POST /admin/query roda SQL cru do corpo; POST /admin/reset-db apaga tudo sem auth.
Impact: Comprometimento total do banco por design.
Recommendation: Remover os endpoints. Operações admin só via script protegido.
...

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

The skill must **not** modify any file until the human answers `y`. On `n`, it ends cleanly.
