// Camada de conexão — banco em arquivo persistente (T / AP-06) e API baseada em
// Promise para permitir async/await e transações (T5 / AP-08).
const sqlite3 = require('sqlite3').verbose();
const config = require('../config');
const { hashPassword } = require('../utils/crypto');

const db = new sqlite3.Database(config.dbPath);

function run(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function (err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
}

function all(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
}

async function initDb() {
    await run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT)`);
    await run(`CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)`);
    await run(`CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)`);
    await run(`CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)`);
    await run(`CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)`);

    const { c } = await get('SELECT COUNT(*) AS c FROM users');
    if (c === 0) {
        // Senha armazenada com hash salgado (nunca em texto puro).
        await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
        await run("INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)",
            ['Clean Architecture', 997.00, 'Docker', 497.00]);
        await run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
        await run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
    }
}

module.exports = { db, run, get, all, initDb };
