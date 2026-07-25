// Service de Relatório — uma única query com JOIN no lugar do N+1 assíncrono (T8 / AP-08).
// Substitui os contadores manuais frágeis (coursesPending/enrPending) do AppManager.
const { all } = require('../database/connection');

async function financialReport() {
    const rows = await all(`
        SELECT c.id AS course_id, c.title AS course,
               u.name AS student, p.amount AS paid, p.status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u       ON u.id = e.user_id
        LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id
    `);

    const byCourse = new Map();
    for (const row of rows) {
        if (!byCourse.has(row.course_id)) {
            byCourse.set(row.course_id, { course: row.course, revenue: 0, students: [] });
        }
        const entry = byCourse.get(row.course_id);
        if (row.student) {
            if (row.status === 'PAID') entry.revenue += row.paid;
            entry.students.push({ student: row.student, paid: row.paid || 0 });
        }
    }
    return Array.from(byCourse.values());
}

module.exports = { financialReport };
