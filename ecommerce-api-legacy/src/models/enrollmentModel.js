// Model de Enrollment — apenas acesso a dados.
const { run } = require('../database/connection');

async function create(userId, courseId) {
    const { lastID } = await run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseId],
    );
    return lastID;
}

module.exports = { create };
