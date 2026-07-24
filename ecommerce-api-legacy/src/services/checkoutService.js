// Service de Checkout — regra de negócio com async/await e transação (T5 / AP-05, AP-12).
// Substitui o callback hell aninhado do AppManager; se qualquer passo falhar, faz ROLLBACK
// (não deixa matrícula órfã).
const { run } = require('../database/connection');
const courseModel = require('../models/courseModel');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const paymentService = require('./paymentService');
const { hashPassword } = require('../utils/crypto');

class CheckoutError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
    }
}

async function checkout({ name, email, password, courseId, cardNumber }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new CheckoutError('Curso não encontrado', 404);

    const payment = await paymentService.charge({ cardNumber, amount: course.price });
    if (payment.status === 'DENIED') throw new CheckoutError('Pagamento recusado', 400);

    await run('BEGIN');
    try {
        let user = await userModel.findByEmail(email);
        const userId = user ? user.id : await userModel.create(name, email, hashPassword(password));

        const enrollmentId = await enrollmentModel.create(userId, courseId);
        await paymentModel.create(enrollmentId, course.price, payment.status);
        await auditModel.create(`Checkout curso ${courseId} por ${userId}`);

        await run('COMMIT');
        return { enrollmentId };
    } catch (err) {
        await run('ROLLBACK');
        throw err;
    }
}

module.exports = { checkout, CheckoutError };
