// Service de Usuário — exclusão transacional que remove dependências (T5 / AP-12).
// Antes, o DELETE de users deixava enrollments/payments órfãos no banco.
const { run } = require('../database/connection');

async function deleteUser(id) {
    await run('BEGIN');
    try {
        await run(
            'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
            [id],
        );
        await run('DELETE FROM enrollments WHERE user_id = ?', [id]);
        await run('DELETE FROM users WHERE id = ?', [id]);
        await run('COMMIT');
    } catch (err) {
        await run('ROLLBACK');
        throw err;
    }
}

module.exports = { deleteUser };
