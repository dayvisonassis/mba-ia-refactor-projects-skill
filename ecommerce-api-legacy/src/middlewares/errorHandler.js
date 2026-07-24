// Middleware de tratamento de erros centralizado (T10 / AP-11).
// Detalhe do erro fica no log (stderr); o cliente recebe mensagem genérica.
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    console.error('Erro não tratado:', err.message);
    res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
