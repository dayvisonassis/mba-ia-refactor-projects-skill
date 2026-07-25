# Reference — Architecture Guidelines (Phase 3 target)

The target the refactoring converges toward: a clean **MVC** layering with supporting layers. The
playbook transforms code toward these rules; Phase 3 enforces them. **Preserve the external contract
of the original endpoints** at all times.

---

## 1. Target layers and responsibilities

| Layer | Responsibility | Must NOT do |
|---|---|---|
| **Models** | Represent entities + data access (persist/query). One entity per module. | No HTTP, no routing, no business rules. |
| **Views / Routes** | Declare routes; parse request, shape response. Thin. | No business logic, no direct DB/SQL. |
| **Controllers** | Orchestrate one request: validate input, call services/models, build the response. | No SQL, no heavy rules inline. |
| **Services** | Business rules (stock/total, checkout, payment, notifications, auth token issuing). | No HTTP request/response objects. |
| **Config** | Load settings/secrets from environment. | No hardcoded secrets. |
| **Middlewares** | Cross-cutting concerns: centralized error handling, auth, logging. | No per-route business logic. |
| **Entry point** | Composition root: wire layers together, start the server. | No business logic. |

## 2. Dependency direction

Dependencies flow in **one direction** — outer layers depend on inner ones, never the reverse:

```
Routes/Views  →  Controllers  →  Services  →  Models  →  Database
                                    │
                     Config ────────┘ (injected)        Middlewares wrap the pipeline
```

- A **Model** must not import a Controller or a Route.
- A **Route** must not run SQL or business rules.
- Secrets come from **Config**, injected — never read ad-hoc deep in a model.

## 3. Target folder structure

Reference shape (adapt names to the framework's idiom — `views/` for Flask blueprints, `routes/` for
Express routers). Both stacks map to the same layer set:

```
src/
├── config/           # settings loaded from env (SECRET_KEY, DB creds, gateway keys)
├── database/         # connection management (per-request / pool) + schema/seed
├── models/           # one module per entity — parameterized data access
├── services/         # business rules
├── controllers/      # request orchestration
├── views/ | routes/  # route declarations (blueprints / routers)
├── middlewares/      # centralized error handler, auth, logging
└── app.py | app.js   # composition root (entry point)
```

**Flask ↔ Express mapping:** Flask blueprint == Express router (Views/Routes); `flask.g` per-request
connection == a request-scoped/pooled Express DB handle; `werkzeug.security` == `bcrypt`; a Flask
error handler (`@app.errorhandler`) == Express error middleware `(err, req, res, next)`.

## 4. Adaptive strategy (choose depth by the Phase 1 classification)

The refactoring depth **depends on the current architecture** found in Phase 1:

- **Monolithic** (e.g. all logic in flat files, or a God Class) → build the **full MVC scaffold**
  above from scratch, moving each responsibility into its layer.
- **Already-layered** (folders like `models/routes/services/utils` exist) → do **targeted
  improvement**: fix the anti-patterns and fill the missing pieces (config module, services, error
  handler, auth) **without rewriting parts that are already adequate**. Do not churn working code for
  the sake of uniformity.

In **both** cases:
- The **external endpoint contract is preserved** — same paths, same methods, same success responses
  (auth may add a required token on sensitive routes; document it).
- Configuration is extracted (no hardcoded secrets), models abstract data, routes/views are separated
  from logic, controllers concentrate the flow, error handling is centralized, and there is a clear
  entry point.

## 5. Definition of done (structure)

A refactored project satisfies:
- [ ] Config module, no hardcoded secrets.
- [ ] Models abstract data access (parameterized / ORM), no business rules.
- [ ] Views/Routes separated from logic.
- [ ] Controllers concentrate the request flow.
- [ ] Business rules live in Services.
- [ ] Centralized error handling.
- [ ] Clear entry point (composition root).
- [ ] App boots without errors and original endpoints still respond.
