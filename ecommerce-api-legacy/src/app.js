// Entry point / composition root — monta e conecta as camadas.
// Executar com: `npm start` (node src/app.js).
const express = require('express');
const config = require('./config');
const { initDb } = require('./database/connection');
const registerRoutes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');

async function start() {
    const app = express();
    app.use(express.json());

    await initDb();
    registerRoutes(app);
    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`LMS API rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    console.error('Falha ao iniciar a aplicação:', err);
    process.exit(1);
});
