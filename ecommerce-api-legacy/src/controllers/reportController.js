// Controller de Relatório — orquestra o request; regra/queries ficam no service.
const reportService = require('../services/reportService');

async function financial(req, res, next) {
    try {
        const report = await reportService.financialReport();
        return res.json(report);
    } catch (err) {
        return next(err);
    }
}

module.exports = { financial };
