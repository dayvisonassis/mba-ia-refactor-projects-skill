# Skill `refactor-arch` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `refactor-arch` Claude Code skill — a 3-phase (Analysis → Audit → Refactor) architectural auditing and refactoring skill that works stack-agnostically across the 3 legacy projects.

**Architecture:** One lean `SKILL.md` orchestrator + 5 on-demand `references/` files (one per required knowledge area). Phase 1 and 2 are read-only; Phase 3 modifies code only after an explicit `[y/n]` confirmation gate. Phase 3 adapts depth to the project's current organization (monolith → full MVC scaffold; already-layered → targeted fixes).

**Tech Stack:** Markdown (skill + references). Target projects use Python/Flask and Node.js/Express. No build step — the deliverable is the skill's markdown content.

## Global Constraints

- Skill lives at `code-smells-project/.claude/skills/refactor-arch/` (Claude Code convention); invoked via `/refactor-arch`.
- Skill name is exactly `refactor-arch`; main file is exactly `SKILL.md` (both mandatory, must not be renamed).
- `SKILL.md` + all `references/` written in **English**; audit reports the skill emits are in **Portuguese**.
- Exactly 5 reference files, mapping 1:1 to the required knowledge areas.
- Anti-patterns catalog: **≥ 8 anti-patterns** spanning all 4 severities (CRITICAL, HIGH, MEDIUM, LOW) + a dedicated **deprecated-APIs** section.
- Refactoring playbook: **≥ 8 transformation patterns**, each with before/after code.
- Phase 2 MUST pause and request confirmation before Phase 3 modifies any file.
- Phase 3 MUST validate the result (app boots + endpoints respond).
- Skill must be technology-agnostic — no hardcoded reference to a single project.
- Keep `SKILL.md` lean (~few hundred lines); heavy detail belongs in `references/`.
- Every file reference in the skill uses relative paths and includes line numbers where citing code.
- Style follows the `sdd-skills` repo: rich `name`+`description` frontmatter, canonical sections (Persona & Scope → Objective → Inputs → ... → Workflow), structured tables.

## Source of Truth

The manual analysis in `explicacao_problemas_encontrados.md` (repo root) is the authoritative list of real problems found in the 3 projects. Every anti-pattern in the catalog and every transformation in the playbook MUST be grounded in a real finding documented there. Read it before writing Tasks 3 and 6.

## File Structure

```
code-smells-project/.claude/skills/refactor-arch/
├── SKILL.md                        # Task 7 (orchestrator; written last, references the 5 files)
└── references/
    ├── project-analysis.md         # Task 2 — Phase 1 detection heuristics
    ├── anti-patterns-catalog.md    # Task 3 — Phase 2 catalog (≥8 + deprecated APIs)
    ├── report-template.md          # Task 4 — Phase 2 report format (PT)
    ├── architecture-guidelines.md  # Task 5 — Phase 3 target MVC rules
    └── refactoring-playbook.md      # Task 6 — Phase 3 transformations (≥8, before/after)
```

**Build order rationale:** references first (Tasks 2–6), then `SKILL.md` last (Task 7) so its References Index points to files that already exist. Task 1 creates the folder skeleton. Task 8 is an end-to-end dry-run consistency check.

---

### Task 1: Skill folder skeleton

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/references/` (directory)

**Interfaces:**
- Consumes: nothing.
- Produces: the directory tree that Tasks 2–7 write into.

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p "code-smells-project/.claude/skills/refactor-arch/references"
```

- [ ] **Step 2: Verify the directory exists**

Run: `ls -la "code-smells-project/.claude/skills/refactor-arch"`
Expected: shows a `references` subdirectory.

- [ ] **Step 3: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "chore: scaffold refactor-arch skill folder"
```
Note: an empty dir may not stage; if so, this commit happens together with Task 2.

---

### Task 2: `project-analysis.md` (Phase 1 knowledge)

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/references/project-analysis.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the detection heuristics Phase 1 of `SKILL.md` (Task 7) will cite.

**Required content (this file MUST contain):**
1. **Language detection** heuristics — signal files per language: `requirements.txt`/`*.py` → Python; `package.json`/`*.js` → Node.js. Table form.
2. **Framework detection** — `flask` import / `Flask(__name__)` → Flask; `express` in deps / `require('express')` → Express. Table form.
3. **Database detection** — `sqlite3` / `SQLALCHEMY_DATABASE_URI` / `.db` files / `CREATE TABLE` statements; how to enumerate tables.
4. **Architecture mapping** — how to classify: monolithic (all logic in few files) vs. layered (folders like `models/`, `routes/`, `services/`). Signals for each.
5. **Domain inference** — infer domain from table names / route paths / entity names (e.g. `produtos, pedidos` → E-commerce).
6. **Counting method** — how to count source files and DB tables (state the grep/glob method, per `sdd-skills` "state the method used" rule).
7. **Phase 1 output contract** — the exact summary block to print (matches the enunciado example: Language / Framework / Dependencies / Domain / Architecture / Source files / DB tables).

- [ ] **Step 1: Write the file with all 7 required content blocks above**

Write `project-analysis.md` covering each numbered item as a titled section with tables. Keep it stack-agnostic (Python/Flask and Node/Express both covered explicitly, but heuristics generalizable).

- [ ] **Step 2: Verify required sections are present**

Run:
```bash
grep -iE "language detection|framework detection|database detection|architecture|domain|counting|output contract" "code-smells-project/.claude/skills/refactor-arch/references/project-analysis.md" | wc -l
```
Expected: ≥ 7 (all seven blocks present).

- [ ] **Step 3: Verify both stacks are covered**

Run:
```bash
grep -icE "flask|express" "code-smells-project/.claude/skills/refactor-arch/references/project-analysis.md"
```
Expected: ≥ 2 (both Flask and Express mentioned).

- [ ] **Step 4: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "feat(skill): add project-analysis reference (Phase 1 heuristics)"
```

---

### Task 3: `anti-patterns-catalog.md` (Phase 2 knowledge)

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md`
- Read first: `explicacao_problemas_encontrados.md` (source of truth)

**Interfaces:**
- Consumes: findings documented in `explicacao_problemas_encontrados.md`.
- Produces: the anti-pattern IDs + severities that `report-template.md` (Task 4) and the playbook (Task 6) reference. Use stable IDs: `AP-01`..`AP-NN`.

**Required content:**
- **≥ 8 anti-patterns**, each an entry with: stable ID, name, **severity** (one of CRITICAL/HIGH/MEDIUM/LOW), **detection signal** (concrete, greppable — e.g. `execute("... " + var)`), why it's a problem, and which target-project finding it maps to.
- All 4 severities represented at least once.
- A dedicated **"Deprecated / At-risk APIs"** section listing at least: `hashlib.md5` for passwords, `datetime.utcnow()` (deprecated Python 3.12+), `sqlite3` callback style vs. async, `type(x) == list` vs `isinstance` — each with the modern replacement.

Minimum catalog (grounded in the manual analysis):

| ID | Anti-pattern | Severity | Detection signal |
|----|--------------|----------|------------------|
| AP-01 | SQL Injection via string concat | CRITICAL | `execute("..." + var)` / f-string with input in SQL |
| AP-02 | Hardcoded secrets | CRITICAL | `SECRET_KEY =`, `pk_live_`, literal password/key |
| AP-03 | Insecure password storage | CRITICAL | plaintext insert/compare, `md5(`, homemade hash |
| AP-04 | God Class / God Method | CRITICAL | one file/class with DB + routing + business logic |
| AP-05 | Business logic in wrong layer | HIGH | business rules inside model/controller |
| AP-06 | Global mutable state | HIGH | global connection/cache reused across requests |
| AP-07 | Missing auth / fake auth | HIGH | no auth middleware; predictable/unsigned token |
| AP-08 | N+1 queries | MEDIUM | query inside `for`/`forEach` loop |
| AP-09 | Duplicated validation/serialization | MEDIUM | same validation repeated in create/update |
| AP-10 | Magic numbers / literal lists | LOW | unnamed number/list constant |
| AP-11 | `print`/`console.log` as logging + bare `except:` | LOW | no logger; catch without type |

- [ ] **Step 1: Read the source of truth**

Run: `sed -n '1,400p' explicacao_problemas_encontrados.md` (or Read the file) to ground each anti-pattern in a real finding.

- [ ] **Step 2: Write the catalog**

Write `anti-patterns-catalog.md` with the ≥8 entries (use the table above as the minimum, expand each into a full entry with detection signal + why + example location) plus the "Deprecated / At-risk APIs" section.

- [ ] **Step 3: Verify anti-pattern count**

Run:
```bash
grep -cE "^\|\s*AP-[0-9]" "code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md"
```
Expected: ≥ 8. (If entries are written as headings instead of table rows, count `grep -cE "AP-[0-9]{2}"` and expect ≥ 8 unique IDs.)

- [ ] **Step 4: Verify all 4 severities present**

Run:
```bash
for s in CRITICAL HIGH MEDIUM LOW; do grep -q "$s" "code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md" && echo "$s ok" || echo "$s MISSING"; done
```
Expected: four `ok` lines.

- [ ] **Step 5: Verify deprecated-APIs section present**

Run:
```bash
grep -iE "deprecated|at-risk|md5|utcnow|isinstance" "code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md" | wc -l
```
Expected: ≥ 3.

- [ ] **Step 6: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "feat(skill): add anti-patterns catalog with deprecated-APIs section"
```

---

### Task 4: `report-template.md` (Phase 2 output format)

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/references/report-template.md`

**Interfaces:**
- Consumes: anti-pattern IDs/severities from Task 3.
- Produces: the canonical report shape Phase 2 of `SKILL.md` emits and that gets saved to `reports/audit-project-N.md`.

**Required content:**
- The report is in **Portuguese**.
- Header block: `ARCHITECTURE AUDIT REPORT`, Project, Stack, Files/LOC.
- **Summary** line: `CRITICAL: n | HIGH: n | MEDIUM: n | LOW: n`.
- **Findings** section: each finding has `[SEVERITY] Title`, `File: path:line`, `Description`, `Impact`, `Recommendation`.
- Findings **ordered by severity** (CRITICAL → LOW) — state this rule explicitly.
- Footer: `Total: N findings` and the confirmation prompt `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`.
- Match the visual format of the enunciado example (the `====` banners).

- [ ] **Step 1: Write the template**

Write `report-template.md` containing the literal template (with placeholder tokens like `{project}`, `{n}`, `{path:line}`) and a short "how to fill it" note stating the severity ordering rule and that each finding needs exact `file:line`.

- [ ] **Step 2: Verify the mandatory finding fields are documented**

Run:
```bash
grep -iE "File:|Description|Impact|Recommendation|Summary|Total:" "code-smells-project/.claude/skills/refactor-arch/references/report-template.md" | wc -l
```
Expected: ≥ 6.

- [ ] **Step 3: Verify the confirmation prompt is present**

Run:
```bash
grep -iE "\[y/n\]|Proceed with refactoring" "code-smells-project/.claude/skills/refactor-arch/references/report-template.md"
```
Expected: at least one match.

- [ ] **Step 4: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "feat(skill): add audit report template (PT, ordered by severity)"
```

---

### Task 5: `architecture-guidelines.md` (Phase 3 target rules)

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/references/architecture-guidelines.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the target MVC layer rules the playbook (Task 6) transforms toward and Phase 3 enforces.

**Required content:**
1. **Target layers** and responsibilities:
   - **Models** — data/entities + persistence access; no HTTP, no routing.
   - **Views/Routes** — routing + request/response only; no business logic.
   - **Controllers** — orchestrate the request flow; delegate to services/models.
   - **Services** (where business rules live), **Config** (no hardcoded secrets), **Middlewares** (centralized error handling), **Entry point** (composition root).
2. **Dependency rules** — allowed direction (routes → controllers → services → models); what a layer must NOT do.
3. **Target folder structure** (matches enunciado example: `config/`, `models/`, `views/`, `controllers/`, `middlewares/`, entry point).
4. **Adaptive strategy** — explicit rule: monolith → full scaffold; already-layered project → targeted improvement without rewriting adequate parts. Endpoints' external contract MUST be preserved.
5. **Stack-agnostic note** — how the same layer map applies to both Flask and Express.

- [ ] **Step 1: Write the guidelines**

Write `architecture-guidelines.md` with the 5 blocks above, using a text dependency-flow diagram (like `architecture-analyzer` §3) and a target folder tree.

- [ ] **Step 2: Verify all layers documented**

Run:
```bash
for l in Model View Controller Service Config Middleware; do grep -iq "$l" "code-smells-project/.claude/skills/refactor-arch/references/architecture-guidelines.md" && echo "$l ok" || echo "$l MISSING"; done
```
Expected: six `ok` lines.

- [ ] **Step 3: Verify adaptive strategy documented**

Run:
```bash
grep -iE "monolith|already-layered|adaptive|preserve" "code-smells-project/.claude/skills/refactor-arch/references/architecture-guidelines.md" | wc -l
```
Expected: ≥ 2.

- [ ] **Step 4: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "feat(skill): add MVC architecture guidelines with adaptive strategy"
```

---

### Task 6: `refactoring-playbook.md` (Phase 3 transformations)

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md`
- Read first: `explicacao_problemas_encontrados.md` (for real before/after examples)

**Interfaces:**
- Consumes: anti-pattern IDs from Task 3; layer rules from Task 5.
- Produces: the transformation recipes Phase 3 applies. Each recipe references the anti-pattern ID it fixes (`Fixes: AP-01`).

**Required content — ≥ 8 transformations, each with:** title, `Fixes: AP-NN`, a **Before** code block and an **After** code block, and a one-line rationale. Minimum set:

1. String-concat SQL → parameterized query (`Fixes: AP-01`)
2. Hardcoded secret → environment variable (`Fixes: AP-02`)
3. Plaintext/MD5 password → `bcrypt`/`werkzeug.security` hashing (`Fixes: AP-03`)
4. God Class → split into MVC layers (`Fixes: AP-04`)
5. Business logic in controller/model → dedicated Service (`Fixes: AP-05`)
6. Global connection → per-request connection / injection (`Fixes: AP-06`)
7. N+1 loop queries → single JOIN / eager loading (`Fixes: AP-08`)
8. Duplicated validation → single validator/schema (`Fixes: AP-09`)
9. Callback hell → `async/await` + transaction (`Fixes: AP-05`/Express)
10. `print` + bare `except` → `logging` + centralized error handler (`Fixes: AP-11`)

- [ ] **Step 1: Read source of truth for real snippets**

Read `explicacao_problemas_encontrados.md` to pull authentic before-snippets (e.g. `models.py:110` login concat, `AppManager.js:45` card logging).

- [ ] **Step 2: Write the playbook**

Write `refactoring-playbook.md` with ≥ 8 transformations (use the list above), each with Before/After fenced code blocks and a `Fixes: AP-NN` tag. Cover both Python and JS examples.

- [ ] **Step 3: Verify transformation count**

Run:
```bash
grep -cE "Fixes:\s*AP-[0-9]" "code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md"
```
Expected: ≥ 8.

- [ ] **Step 4: Verify before/after code blocks exist**

Run:
```bash
grep -ciE "before|after" "code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md"
```
Expected: ≥ 16 (a Before + After per transformation).

- [ ] **Step 5: Verify both stacks covered**

Run:
```bash
grep -ciE "```python|```js|```javascript" "code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md"
```
Expected: ≥ 2 (Python and JS code blocks both present).

- [ ] **Step 6: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "feat(skill): add refactoring playbook with before/after transformations"
```

---

### Task 7: `SKILL.md` (orchestrator — written last)

**Files:**
- Create: `code-smells-project/.claude/skills/refactor-arch/SKILL.md`

**Interfaces:**
- Consumes: all 5 reference files (Tasks 2–6) — links to them in the References Index.
- Produces: the invocable skill. This is the entry point `/refactor-arch` runs.

**Required content (canonical `sdd-skills` sections):**
1. **Frontmatter** — `name: refactor-arch`; rich `description` (what it does + when to use: "audit and refactor any backend project to MVC, stack-agnostic, 3 phases with a confirmation gate").
2. **Persona & Scope** — Expert Software Architect, stack-agnostic; Phases 1–2 are read-only, Phase 3 modifies only after confirmation.
3. **Objective** — the 5 capabilities from the enunciado.
4. **Inputs** — target project path; source files; manifests.
5. **The 3 Phases** — for each: what it reads, what reference it loads, what it outputs.
   - Phase 1 → loads `references/project-analysis.md`, prints the summary block.
   - Phase 2 → loads `anti-patterns-catalog.md` + `report-template.md`, emits PT report ordered by severity, then **STOPS at `[y/n]`**.
   - Phase 3 → only after `y`; loads `architecture-guidelines.md` + `refactoring-playbook.md`; applies adaptive strategy; then **validates** (boot + endpoints) and prints the PHASE 3 checklist.
6. **Confirmation Gate** — explicit: never modify a file before `y`.
7. **Validation** — how to confirm the app boots and endpoints respond (health check + original routes).
8. **Criteria** — read every file, exact `file:line`, findings ordered by severity, ≥5 findings, preserve endpoint contract.
9. **Negative Instructions** — don't modify in Phase 1/2; don't skip the gate; don't break endpoints; don't hardcode a single project.
10. **Error Handling** — the `Status: ERROR` block pattern.
11. **Workflow** — numbered end-to-end steps.
12. **Self-Audit Checklist** — the agent reviews its own output before finishing.
13. **References Index** — links to the 5 files with a one-line purpose each.

- [ ] **Step 1: Write `SKILL.md`**

Write the file with all 13 sections. Keep it lean (target < 350 lines); push detail into the references it links. Frontmatter must be valid YAML with `name` and `description`.

- [ ] **Step 2: Verify frontmatter is correct**

Run:
```bash
head -5 "code-smells-project/.claude/skills/refactor-arch/SKILL.md"
```
Expected: opens with `---`, contains `name: refactor-arch` and a `description:` line.

- [ ] **Step 3: Verify the 3 phases and the gate are present**

Run:
```bash
grep -iE "phase 1|phase 2|phase 3|\[y/n\]|confirmation" "code-smells-project/.claude/skills/refactor-arch/SKILL.md" | wc -l
```
Expected: ≥ 4.

- [ ] **Step 4: Verify References Index links all 5 files**

Run:
```bash
grep -cE "references/(project-analysis|anti-patterns-catalog|report-template|architecture-guidelines|refactoring-playbook)\.md" "code-smells-project/.claude/skills/refactor-arch/SKILL.md"
```
Expected: ≥ 5.

- [ ] **Step 5: Verify leanness**

Run:
```bash
wc -l "code-smells-project/.claude/skills/refactor-arch/SKILL.md"
```
Expected: < 350 lines (soft cap; if larger, move detail to references).

- [ ] **Step 6: Commit**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "feat(skill): add SKILL.md orchestrator with 3 phases and confirmation gate"
```

---

### Task 8: End-to-end consistency check (dry run)

**Files:**
- Modify: none (read-only verification; fixes go into the relevant reference file if issues found).

**Interfaces:**
- Consumes: all 6 skill files.
- Produces: confidence that the skill is internally consistent and agnostic before real execution on the 3 projects.

- [ ] **Step 1: Verify no anti-pattern ID is referenced without being defined**

Run:
```bash
CAT="code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md"
PB="code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md"
comm -23 <(grep -oE "AP-[0-9]{2}" "$PB" | sort -u) <(grep -oE "AP-[0-9]{2}" "$CAT" | sort -u)
```
Expected: empty output (every `AP-NN` used in the playbook is defined in the catalog). If not empty, add the missing entry to the catalog.

- [ ] **Step 2: Verify the skill has no accidental hardcoding to one project**

Run:
```bash
grep -riE "code-smells-project|loja\.db|produtos|frankenstein" "code-smells-project/.claude/skills/refactor-arch/" | grep -vE "example|e\.g\.|exemplo|Fixes:" | wc -l
```
Expected: 0 outside clearly-marked examples. Review any hits — project names must only appear as illustrative examples, never as required inputs.

- [ ] **Step 3: Verify all 5 knowledge areas are covered by a reference file**

Run:
```bash
ls "code-smells-project/.claude/skills/refactor-arch/references/" | sort
```
Expected: exactly `anti-patterns-catalog.md`, `architecture-guidelines.md`, `project-analysis.md`, `refactoring-playbook.md`, `report-template.md`.

- [ ] **Step 4: Manually trace Phase 1→2→3 through the SKILL.md**

Read `SKILL.md` top to bottom and confirm: Phase 1 outputs feed Phase 2; Phase 2 stops at the gate; Phase 3 runs only after `y` and ends with validation. Fix wording inline in `SKILL.md` if the flow is ambiguous.

- [ ] **Step 5: Commit any fixes**

```bash
git add "code-smells-project/.claude/skills/refactor-arch"
git commit -m "fix(skill): resolve consistency issues found in dry-run check" || echo "no fixes needed"
```

---

## Notes for the implementer

- This plan builds the **skill only**. Running it on the 3 projects (generating `reports/audit-project-{1,2,3}.md`, copying the skill into projects 2 and 3, committing refactored code) is a **separate follow-up** driven by the skill itself.
- The verification steps use `grep`/`wc` as objective content gates because the deliverables are markdown, not executable code — there is no unit-test surface. These gates mirror the enunciado's acceptance minimums (≥8 anti-patterns, ≥8 transformations, all severities, deprecated-APIs section, confirmation gate).
- Ground every catalog entry and playbook recipe in `explicacao_problemas_encontrados.md`. Do not invent anti-patterns that don't occur in the target projects.
