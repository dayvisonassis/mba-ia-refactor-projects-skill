// Model de AuditLog — apenas acesso a dados.
const { run } = require('../database/connection');

async function create(action) {
    await run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action],
    );
}

module.exports = { create };
