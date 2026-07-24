// Model de Course — apenas acesso a dados.
const { get, all } = require('../database/connection');

async function findActiveById(id) {
    return get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

async function findAll() {
    return all('SELECT * FROM courses');
}

module.exports = { findActiveById, findAll };
