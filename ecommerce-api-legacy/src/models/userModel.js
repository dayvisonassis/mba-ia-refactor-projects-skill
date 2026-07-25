// Model de User — apenas acesso a dados.
const { run, get } = require('../database/connection');

async function findByEmail(email) {
    return get('SELECT * FROM users WHERE email = ?', [email]);
}

async function findById(id) {
    // Não expõe o campo `pass`.
    return get('SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create(name, email, passHash) {
    const { lastID } = await run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passHash],
    );
    return lastID;
}

module.exports = { findByEmail, findById, create };
