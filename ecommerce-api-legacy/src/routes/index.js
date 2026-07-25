// Camada de Routes — apenas declara as rotas e delega aos controllers.
// Mantém o contrato original: /api/checkout, /api/admin/financial-report, /api/users/:id.
const express = require('express');
const checkoutController = require('../controllers/checkoutController');
const reportController = require('../controllers/reportController');
const userController = require('../controllers/userController');

function registerRoutes(app) {
    const router = express.Router();

    router.post('/checkout', checkoutController.create);
    router.get('/admin/financial-report', reportController.financial);
    router.delete('/users/:id', userController.remove);

    app.use('/api', router);
}

module.exports = registerRoutes;
