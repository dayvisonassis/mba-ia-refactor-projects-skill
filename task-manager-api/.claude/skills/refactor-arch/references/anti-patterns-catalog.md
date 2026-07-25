# Reference — Anti-Patterns Catalog (Phase 2)

The knowledge Phase 2 (Audit) cross-references the code against. Each entry has a **stable ID**
(`AP-NN`), a **severity**, a **concrete detection signal** (greppable — not "bad code"), why it
matters, and the modern fix (which the playbook expands with before/after code).

Severity scale (from the challenge):

| Severity | Meaning |
|---|---|
| **CRITICAL** | Security/architecture failure that breaks the system, leaks sensitive data, or destroys separation of responsibilities. |
| **HIGH** | Strong MVC/SOLID violation that badly hurts maintainability and testability. |
| **MEDIUM** | Standardization, code duplication, or moderate performance (e.g. N+1). |
| **LOW** | Readability, naming, magic numbers. |

When auditing, cite **exact `file:line`** for every match. Order findings CRITICAL → LOW.

---

## Catalog

### AP-01 — SQL Injection via string concatenation — `CRITICAL`
**Detection signal:** `execute("... " + var)`, f-string/template-string with a variable inside SQL,
`query += " AND ... '" + termo + "'"`.
**Why:** user input becomes SQL code → auth bypass, data exfiltration, data destruction (OWASP #1).
**Fix:** parameterized queries (`execute("... WHERE id = ?", (id,))`). → Playbook T1.
**Seen in:** `models.py:28,48-49,110,291`.

### AP-02 — Hardcoded secrets — `CRITICAL`
**Detection signal:** literal `SECRET_KEY = "..."`, `pk_live_...`, `dbPass: "..."`, SMTP password in
source; secret returned in an HTTP response.
**Why:** secrets leak through Git/history to anyone with repo access; live payment keys mean direct
financial compromise.
**Fix:** read from environment / secret manager; never serialize secrets. → Playbook T2.
**Seen in:** `app.py:7`, `controllers.py:289` (leaked via `/health`); `utils.js:1-7`; `app.py:13` + `notification_service.py:9-10`.

### AP-03 — Insecure password storage — `CRITICAL`
**Detection signal:** plaintext password stored/compared in SQL; `hashlib.md5(...)`; homemade
"crypto" (base64 loops, truncation); password serialized back to the client.
**Why:** a DB leak exposes every account; MD5/base64 are trivially reversible; passwords are reused
across services.
**Fix:** strong salted hash (`werkzeug.security`, `bcrypt`, `argon2`); never return the password
field. → Playbook T3.
**Seen in:** `models.py:110,127-128,83`; `utils.js:17-23`; `models/user.py:29,32`.

### AP-04 — God Class / God Method — `CRITICAL`
**Detection signal:** one class/file that opens the DB connection **and** defines schema/seed **and**
registers routes **and** holds business rules; very large single file.
**Why:** zero MVC separation, impossible to test in isolation, every change risks everything.
**Fix:** split into Models / Controllers / Services / Routes; inject dependencies. → Playbook T4.
**Seen in:** `AppManager.js:4-141`.

### AP-05 — Business logic in the wrong layer — `HIGH`
**Detection signal:** stock/total/pricing calculations inside a *model* function; payment approval,
notifications, or orchestration inside a *controller*/route.
**Why:** violates SRP and MVC — data layer should only persist/query; controllers should only
orchestrate. Rules trapped in the wrong layer can't be reused or unit-tested.
**Fix:** move rules into a dedicated **Service** layer. → Playbook T5.
**Seen in:** `models.py:133-169` (order rules in model); `controllers.py:208-210,248-250` (notifications in controller); `AppManager.js:47` (payment rule in route).

### AP-06 — Global mutable state — `HIGH`
**Detection signal:** module-level `db_connection = None` reused across requests; global cache/counter
exported and mutated; `check_same_thread=False`.
**Why:** race conditions and hidden coupling under concurrency; untestable; memory growth.
**Fix:** per-request connection (`flask.g` + teardown) or a pool; scoped cache with TTL; dependency
injection. → Playbook T6.
**Seen in:** `database.py:4-11`; `utils.js:9-10`.

### AP-07 — Missing / fake authentication — `HIGH`
**Detection signal:** predictable/unsigned "token" (`"fake-jwt-token-" + id`); no auth
decorator/middleware on sensitive routes; a role check function that is defined but never called.
**Why:** anyone can perform privileged actions (delete users, read reports) with no proof of identity.
**Fix:** real signed token with expiry (JWT/`itsdangerous`) + an auth/authorization decorator on
sensitive routes. → Playbook T7.
**Seen in:** `user_routes.py:210` and unprotected routes across the project.

### AP-08 — N+1 queries — `MEDIUM`
**Detection signal:** a DB query **inside** a `for` / `forEach` loop; per-row `.query.get()` /
`db.get(...)` instead of a JOIN or eager load; nested per-item lookups.
**Why:** latency grows linearly with data; one request → hundreds of round-trips.
**Fix:** single JOIN / aggregation, or ORM eager loading (`joinedload`). → Playbook T8.
**Seen in:** `models.py:171-201,203-233`; `AppManager.js:80-129`; `task_routes.py:41-57`, `report_routes.py:53-68`.

### AP-09 — Duplicated validation / serialization (DRY) — `MEDIUM`
**Detection signal:** the same validation block copied in create **and** update; an entity serialized
by hand in multiple routes while a `to_dict()` / validator util already exists but is ignored.
**Why:** rules drift apart silently; a change must be made in several places; dead utilities.
**Fix:** one shared validator/schema and one serialization source. → Playbook T9.
**Seen in:** `controllers.py:24-96`; `task_routes.py:96-114,166-184` + ignored `helpers.py:57-108`; `task.py:23-36` vs hand-built dicts in routes.

### AP-10 — Magic numbers / literal lists — `LOW`
**Detection signal:** unnamed numeric thresholds (`> 10000`, `0.1`, name length `2`/`200`); status/
category lists hardcoded inline and duplicated across files.
**Why:** intent is unclear and values duplicate; changing a rule means hunting the constant.
**Fix:** named constants / config. → Playbook (see T10 context).
**Seen in:** `models.py:257-262`; `controllers.py:47-52,242`.

### AP-11 — `print`/`console.log` as logging + broad/bare `except` — `LOW`
**Detection signal:** `print("ERRO: " + str(e))` / `console.log` used for logging; `except:` with no
type, or `except Exception` that returns `str(e)` to the client; no centralized error handler.
**Why:** no log level/timestamp/destination; bare `except` swallows `KeyboardInterrupt`/`SystemExit`
and masks root causes; internal details leak to clients.
**Fix:** `logging` module + a centralized error handler; catch specific exceptions. → Playbook T10.
**Seen in:** `controllers.py` (throughout); `task_routes.py:62,236`, `helpers.py:46-50`.

### AP-12 — Missing transaction / referential integrity — `HIGH`
**Detection signal:** multi-step write (insert A then insert B) with no `BEGIN/COMMIT/ROLLBACK`;
deleting a parent row without removing/−cascading its children.
**Why:** partial failures leave orphaned/inconsistent data (e.g. enrollment without payment; users
deleted but their payments remain).
**Fix:** wrap multi-step writes in an explicit transaction; FK cascade or transactional cleanup. → Playbook T4/T5 context.
**Seen in:** `AppManager.js:37-77` (no tx on checkout), `AppManager.js:131-137` (orphan delete).

---

## Deprecated / At-risk APIs

The audit must **flag obsolete APIs and recommend the modern equivalent**.

| Deprecated / unsafe API | Problem | Modern replacement |
|---|---|---|
| `hashlib.md5(pwd)` for passwords | Broken, unsalted, fast to brute-force | `werkzeug.security.generate_password_hash` / `bcrypt` / `argon2` |
| `datetime.utcnow()` | Deprecated in Python 3.12+ (naive UTC) | `datetime.now(datetime.UTC)` (timezone-aware) |
| `sqlite3` callback pyramid (Node) | Callback hell, no async flow, no transactions | Promise-based access + `async/await` (`util.promisify` / `better-sqlite3`) |
| `type(x) == list` | Fragile type check, ignores subclasses | `isinstance(x, list)` |
| Flask `app.run(debug=True)` in prod | Exposes Werkzeug debugger → RCE | `debug` driven by env var, off by default |
| SQLite `:memory:` as the app DB | Data lost on every restart | Persistent file / real DB (`:memory:` only for tests) |
| Homemade `badCrypto` / base64 "hash" | Not cryptographic; reversible | `bcrypt` / `argon2` |

Report each applicable one as a finding (severity per the table above — password hashing is CRITICAL,
`type(x)==list` is LOW), citing the exact `file:line`.
