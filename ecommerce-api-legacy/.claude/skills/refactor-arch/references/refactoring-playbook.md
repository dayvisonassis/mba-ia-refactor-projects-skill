# Reference — Refactoring Playbook (Phase 3 transformations)

Concrete transformation recipes applied in **Phase 3**. Each recipe fixes one or more catalog
anti-patterns (`Fixes: AP-NN`), with a **Before** and **After** code block. Examples cover both
Python/Flask and Node/Express. Apply only the recipes relevant to the findings that were confirmed at
the gate.

---

## T1 — String-concat SQL → parameterized query
`Fixes: AP-01`

**Before**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**After**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))
```
Rationale: the driver escapes values; user text can never become SQL. Build dynamic filters by
appending `?` placeholders and extending a params list, never by concatenating input.

---

## T2 — Hardcoded secret → environment variable
`Fixes: AP-02`

**Before**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
```javascript
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_1234567890abcdef" };
```
**After**
```python
# config/settings.py
import os
SECRET_KEY = os.environ["SECRET_KEY"]          # required, no default in prod
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```
```javascript
// config/index.js
module.exports = {
  dbPass: process.env.DB_PASS,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  port: process.env.PORT || 3000,
};
```
Rationale: secrets stay out of source/Git; `/health` and other responses never echo them. Provide a
`.env.example` documenting the required vars.

---

## T3 — Plaintext / MD5 / homemade hash → strong salted hash
`Fixes: AP-03`

**Before**
```python
import hashlib
self.password = hashlib.md5(pwd.encode()).hexdigest()   # broken
```
```javascript
function badCrypto(pwd) { /* base64 loop, truncated to 10 chars */ }
```
**After**
```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)             # salted, strong
# verify:
check_password_hash(self.password, attempt)
```
```javascript
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(pwd, 12);
const ok = await bcrypt.compare(attempt, hash);
```
Rationale: salted, slow hashing resists brute-force. **Never** serialize the password field back to
clients (remove it from `to_dict()` / responses).

---

## T4 — God Class → split into MVC layers
`Fixes: AP-04, AP-12`

**Before**
```javascript
class AppManager {              // connection + schema + seed + ALL routes + business rules
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* CREATE TABLE ... + INSERT seed */ }
  setupRoutes(app) { app.post('/api/checkout', /* payment + enroll + audit inline */); /* ... */ }
}
```
**After**
```javascript
// database/connection.js  → connection + schema/seed
// models/enrollmentModel.js, models/paymentModel.js  → data access
// services/checkoutService.js  → business rule (transactional)
// controllers/checkoutController.js  → orchestrates the request
// routes/index.js  → router.post('/api/checkout', checkoutController.create)
// app.js  → composition root wiring the above
```
Rationale: one responsibility per module → testable, low-risk changes, reusable. Wrap multi-step
writes in a transaction (see T5).

---

## T5 — Business logic in controller/model → dedicated Service (+ transaction)
`Fixes: AP-05, AP-12`

**Before**
```python
# models.py — data layer doing business rules
def criar_pedido(usuario_id, itens):
    for item in itens:
        # stock validation + total calc + insert + stock decrement all here
        ...
```
**After**
```python
# services/pedido_service.py
def criar_pedido(usuario_id, itens):
    with connection.transaction() as tx:          # explicit transaction
        _validar_estoque(itens, tx)               # business rule
        total = _calcular_total(itens, tx)        # business rule
        pedido_id = pedido_model.inserir(usuario_id, total, tx)
        pedido_model.inserir_itens(pedido_id, itens, tx)
        pedido_model.baixar_estoque(itens, tx)
    return {"pedido_id": pedido_id, "total": total}
```
```javascript
// services/checkoutService.js — async + transaction
async function checkout({ userId, courseId, card }) {
  await db.run('BEGIN');
  try {
    const status = await paymentService.charge(card, course.price); // isolated, not cc.startsWith("4")
    const enrId = await enrollmentModel.create(userId, courseId);
    await paymentModel.create(enrId, course.price, status);
    await db.run('COMMIT');
    return enrId;
  } catch (e) { await db.run('ROLLBACK'); throw e; }
}
```
Rationale: rules become unit-testable without HTTP/DB wiring; partial failures roll back (no orphan
enrollment). Payment approval derives from a real result, isolated in a service — never from a card
prefix.

---

## T6 — Global connection → per-request connection / injection
`Fixes: AP-06`

**Before**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
    return db_connection
```
**After**
```python
# database/connection.py
from flask import g
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
# app.teardown_appcontext(close_db)
```
Rationale: one connection per request avoids cross-thread races; no shared mutable global; testable
by swapping the provider.

---

## T7 — Fake/absent auth → signed token + auth decorator
`Fixes: AP-07`

**Before**
```python
return jsonify({'token': 'fake-jwt-token-' + str(user.id)})   # predictable, unsigned
# ...and no route checks it
```
**After**
```python
# services/auth_service.py
from itsdangerous import TimedSerializer  # or PyJWT
def issue_token(user):
    return serializer.dumps({"uid": user.id, "role": user.role})

# middlewares/auth.py
def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        data = _verify(request.headers.get("Authorization"))
        if not data: return jsonify({"erro": "não autorizado"}), 401
        g.current_user = data
        return fn(*a, **kw)
    return wrapper

@user_bp.delete("/users/<int:id>")
@admin_required
def deletar_usuario(id): ...
```

**Do not stop at one route.** The mistake this transformation must prevent is protecting the obvious
verb (`DELETE`) and leaving its siblings open. Derive a **policy for the whole resource** first, then
apply it. Write the table out before touching code:

| Resource | GET | POST | PUT/PATCH | DELETE |
|---|---|---|---|---|
| `users` | public | public (self-signup, **no privilege fields** — see T13) | self **or** admin | admin |
| `reports` | authenticated | — | — | — |
| `tasks` | public | authenticated | owner or admin | owner or admin |

Then apply the decorators across every row, not just the one in the example above:

```python
@user_bp.put("/users/<int:user_id>")
@login_required                      # <- was public: this is the gap T7 used to miss
def atualizar_usuario(user_id):
    if g.current_user["uid"] != user_id and g.current_user["role"] != "admin":
        return jsonify({"erro": "não autorizado"}), 403
    ...
```

Rationale: token is signed and expiring; sensitive routes require a valid identity/role. Public
routes stay open; clients authenticate via `/login` then send the token. **The coverage rule from
AP-07 is the acceptance test:** no write verb on a resource may be less protected than the most
protected write verb on that same resource.

---

## T8 — N+1 loop queries → single JOIN / eager loading
`Fixes: AP-08`

**Before**
```python
for row in pedidos:                         # 1 query
    itens = q("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))  # N
    for item in itens:
        prod = q("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))  # N*M
```
**After**
```python
cursor.execute("""
  SELECT p.id, p.total, i.produto_id, i.quantidade, pr.nome
  FROM pedidos p
  JOIN itens_pedido i ON i.pedido_id = p.id
  JOIN produtos pr    ON pr.id = i.produto_id
""")                                         # single round-trip, assembled in memory
```
```python
# SQLAlchemy variant
Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```
Rationale: constant number of round-trips instead of growing linearly with the data.

---

## T9 — Duplicated validation/serialization → single schema / source
`Fixes: AP-09`

**Before**
```python
# create route and update route each re-implement the same checks;
# routes hand-build the task dict while Task.to_dict() already exists.
```
**After**
```python
# one validator reused by create + update
def validar_produto(dados):
    erros = []
    if not (NOME_MIN <= len(dados.get("nome","")) <= NOME_MAX): erros.append("nome inválido")
    if dados.get("categoria") not in CATEGORIAS_VALIDAS: erros.append("categoria inválida")
    return erros

# one serialization source
return jsonify(task.to_dict())               # extend with derived fields when needed
```
Rationale: DRY — a rule changes in exactly one place; responses stay consistent across endpoints.
Reuse an existing util (e.g. `process_task_data`) instead of duplicating it.

---

## T10 — `print`/bare-`except` → `logging` + centralized error handler
`Fixes: AP-11`

**Before**
```python
try:
    ...
except:                                       # bare — swallows everything
    print("ERRO: " + str(e))
    return jsonify({"erro": str(e)}), 500     # leaks internals
```
**After**
```python
import logging
logger = logging.getLogger(__name__)

# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle(e):
    logger.exception("unhandled error")       # full detail in the log only
    return jsonify({"erro": "erro interno"}), 500

# in code: catch specific types, log e, let the handler format the client response
except ValueError as e:
    logger.warning("validação: %s", e)
    return jsonify({"erro": "dados inválidos"}), 400
```
Rationale: structured logging (level/timestamp/destination); no `KeyboardInterrupt`/`SystemExit`
swallowing; clients get generic messages while details stay in logs.

---

## T11 — Deprecated API → modern equivalent
`Fixes: AP-03 (md5), plus catalog Deprecated table`

**Before**
```python
timestamp = datetime.utcnow()                 # deprecated 3.12+
if type(tags) == list: ...
```
**After**
```python
from datetime import datetime, UTC
timestamp = datetime.now(UTC)                 # timezone-aware
if isinstance(tags, list): ...
```
Rationale: replace obsolete/unsafe calls with the current, correct API (see the catalog's Deprecated
/ At-risk APIs table for the full mapping).

---

## T12 — Magic numbers / inline literal lists → named constants
`Fixes: AP-10`

**Before**
```python
if faturamento > 10000: desconto = faturamento * 0.1
if categoria not in ["informatica", "moveis", "vestuario"]: ...
```
**After**
```python
# config/constants.py
FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario"]
```
Rationale: named, single-sourced values communicate intent and stop duplication drift.

---

## T13 — Client-supplied privilege field → allow-list + authorization
`Fixes: AP-13`

The route being authenticated is **not enough**. Decide, per caller role, *which fields* the client
may write. Everything outside the allow-list is ignored — never echoed back as an error, never
silently applied.

**Before** (Python — public route, value-validated but not authorized)
```python
@user_bp.route('/users', methods=['POST'])          # public
def create_user():
    data = request.get_json()
    role = data.get('role', 'user')                 # <- caller picks their own role
    if role not in VALID_ROLES:                     # validates the VALUE, authorizes NOTHING
        return jsonify({'error': 'Role inválido'}), 400
    user.role = role                                # POST /users {"role":"admin"} -> instant admin
```
**After**
```python
SELF_WRITABLE = {'name', 'email', 'password'}       # what any caller may set on themselves
ADMIN_WRITABLE = SELF_WRITABLE | {'role', 'active'} # privilege fields: admin only

def _allowed_fields(current_user, target_id):
    if current_user and current_user.get('role') == 'admin':
        return ADMIN_WRITABLE
    return SELF_WRITABLE

@user_bp.route('/users', methods=['POST'])          # stays public: self-signup
def create_user():
    data = request.get_json()
    user.role = 'user'                              # forced; never read from the payload
    ...

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required                                     # T7: the route itself is protected
def update_user(user_id):
    caller = g.current_user
    if caller['uid'] != user_id and caller['role'] != 'admin':
        return jsonify({'error': 'Não autorizado'}), 403
    data = request.get_json()
    allowed = _allowed_fields(caller, user_id)
    for field in set(data) & allowed:               # everything else is dropped
        _apply(user, field, data[field])
```

**Before** (JS — spread copies whatever the client sent)
```js
const user = await Users.findById(req.params.id);
Object.assign(user, req.body);        // req.body {"role":"admin"} -> escalation
await user.save();
```
**After**
```js
const SELF_WRITABLE = ['name', 'email', 'password'];
const ADMIN_WRITABLE = [...SELF_WRITABLE, 'role', 'active'];

const allowed = req.user?.role === 'admin' ? ADMIN_WRITABLE : SELF_WRITABLE;
for (const field of allowed) {
    if (field in req.body) user[field] = req.body[field];   // explicit, never a spread
}
```

Rationale: an allow-list fails closed — a new column added to the model is *not* client-writable
until someone deliberately adds it. Ownership fields (`owner_id`, `user_id`, `tenant_id`) belong in
the admin list for the same reason: accepting them from the payload lets a caller move another
subject's resource to themselves.

**Acceptance test:** for every public or self-service write route, send a payload containing each
privilege field and assert the stored value did **not** change.
