// Hashing de senha com scrypt (node:crypto) — salgado e timing-safe (T3 / AP-03).
// Substitui a "criptografia" caseira badCrypto (base64 truncado, sem salt).
const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(password), salt, 64).toString('hex');
    return `${salt}:${derived}`;
}

function verifyPassword(password, stored) {
    const [salt, key] = String(stored).split(':');
    if (!salt || !key) return false;
    const derived = crypto.scryptSync(String(password), salt, 64);
    const keyBuf = Buffer.from(key, 'hex');
    return keyBuf.length === derived.length && crypto.timingSafeEqual(keyBuf, derived);
}

module.exports = { hashPassword, verifyPassword };
