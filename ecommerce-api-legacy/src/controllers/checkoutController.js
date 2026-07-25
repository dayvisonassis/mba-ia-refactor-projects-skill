// Controller de Checkout — orquestra o request; validação de entrada (T9 / AP-09).
// O contrato externo do body é preservado (usr/eml/pwd/c_id/card), mas mapeado
// internamente para nomes descritivos.
const checkoutService = require('../services/checkoutService');

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

async function create(req, res, next) {
    try {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

        if (!name || !email || !courseId || !cardNumber) {
            return res.status(400).json({ error: 'Campos obrigatórios: usr, eml, c_id, card' });
        }
        if (!EMAIL_RE.test(email)) {
            return res.status(400).json({ error: 'E-mail inválido' });
        }

        const { enrollmentId } = await checkoutService.checkout({
            name, email, password, courseId, cardNumber,
        });
        return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    } catch (err) {
        if (err.statusCode) return res.status(err.statusCode).send(err.message);
        return next(err);
    }
}

module.exports = { create };
