# Reference — Project Analysis (Phase 1)

Detection heuristics for **Phase 1 (Analysis)**. The goal is to identify the stack, map the current
architecture, infer the domain, and count what exists — **without modifying anything**. State the
method you used to reach each conclusion (which file / which signal), never guess silently.

---

## 1. Language detection

Inspect signal files at the project root and the file extensions present.

| Signal | Language |
|---|---|
| `requirements.txt`, `Pipfile`, `pyproject.toml`, `*.py` files | **Python** |
| `package.json`, `*.js` / `*.mjs` / `*.ts` files, `node_modules/` | **Node.js** |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `go.mod`, `*.go` | Go |
| `composer.json`, `*.php` | PHP |

Method: `ls` the project root, then `glob` for the dominant source extension. The manifest file is
the strongest signal (a `requirements.txt` outranks a stray `.js` config).

## 2. Framework detection

Read the dependency manifest **and** grep the entry point for the framework's import/bootstrap call.

| Signal | Framework |
|---|---|
| `flask` in `requirements.txt`; `from flask import Flask`; `Flask(__name__)` | **Flask** |
| `flask-sqlalchemy`; `SQLAlchemy(...)`, `db.init_app(app)` | Flask + SQLAlchemy |
| `express` in `package.json`; `require('express')`; `express()` | **Express** |
| `fastapi`; `FastAPI()` | FastAPI |
| `django`; `manage.py`, `settings.py` | Django |
| `@nestjs/core` | NestJS |

Report the framework **and its version** when the manifest pins it (e.g. `flask==3.1.1` → `Flask 3.1.1`).
List other runtime dependencies too (e.g. `flask-cors`, `sqlite3`).

## 3. Database detection

| Signal | Database / access layer |
|---|---|
| `import sqlite3` / `require('sqlite3')` / `.db` file / `:memory:` | SQLite (raw driver) |
| `SQLALCHEMY_DATABASE_URI`, `db.Model`, `db.create_all()` | SQLAlchemy ORM |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `mysql2` | MySQL |
| `mongoose`, `pymongo` | MongoDB |

**Enumerating tables/entities:**
- Raw SQL: grep for `CREATE TABLE` statements — each names a table and its columns.
- ORM: list the model classes (`class X(db.Model)`) and their `__tablename__` / attributes.
- Report the table/entity list (e.g. `produtos, usuarios, pedidos, itens_pedido`).

## 4. Architecture mapping (monolith vs. layered)

Classify the current organization — this drives Phase 3's depth (see `architecture-guidelines.md`).

| Observation | Classification |
|---|---|
| All logic in a handful of flat files at root; one class/file mixing DB + routes + rules | **Monolithic** |
| Folders named after layers (`models/`, `routes/`, `services/`, `controllers/`, `utils/`) | **Layered (partial or full)** |
| Layer folders exist **but** business logic still lives in routes / models still hold SQL | **Layered-but-leaky** (common) |

Method: `ls -R` (or glob the tree), then open the entry point and the largest source file to see
whether responsibilities are actually separated or only *named* as if they were. A `controllers/`
folder that still contains SQL is **leaky**, not layered.

## 5. Domain inference

Infer the business domain from concrete names, not assumptions:
- **Table / entity names** — `produtos, pedidos, usuarios` → E-commerce; `tasks, users, categories` →
  Task Manager; `courses, enrollments, payments` → LMS / online courses.
- **Route paths** — `/checkout`, `/api/admin/financial-report` → sales/checkout flow.
- **Seed data** — sample rows often reveal the domain vocabulary.

State the evidence (e.g. *"tables `courses`, `enrollments`, `payments` → LMS with checkout"*).

## 6. Counting method

Report counts and **say how you counted**:
- **Source files:** glob the language's extension, excluding `node_modules/`, `venv/`, `__pycache__/`,
  and the skill folder itself (`.claude/`). E.g. `glob **/*.py` minus vendored dirs.
- **Lines of code:** approximate via `wc -l` over those files.
- **DB tables:** count `CREATE TABLE` statements or ORM model classes (§3).

## 7. Phase 1 output contract

Print exactly this block (fill the values; keep the banner). Values in the app's language; labels in
English to match the enunciado example:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <e.g. Python>
Framework:     <e.g. Flask 3.1.1>
Dependencies:  <e.g. flask-cors>
Domain:        <e.g. E-commerce API (produtos, pedidos, usuários)>
Architecture:  <e.g. Monolítica — tudo em 4 arquivos, sem separação de camadas>
Source files:  <N> files analyzed
DB tables:     <table1, table2, ...>
================================
```

Then proceed to Phase 2. Phase 1 **never** writes to disk.
