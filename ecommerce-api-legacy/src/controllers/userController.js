// Controller de Usuário — orquestra o request; exclusão transacional no service.
const userService = require('../services/userService');

async function remove(req, res, next) {
    try {
        await userService.deleteUser(req.params.id);
        return res.json({ msg: 'Usuário e dependências (matrículas/pagamentos) removidos.' });
    } catch (err) {
        return next(err);
    }
}

module.exports = { remove };
