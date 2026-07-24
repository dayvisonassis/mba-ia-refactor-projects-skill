// Configuração da aplicação — carregada de variáveis de ambiente (T2 / AP-02).
// Nenhum segredo hardcoded. Defina as variáveis em produção; os defaults abaixo
// servem apenas para desenvolvimento local (e não contêm segredos reais).
module.exports = {
    port: process.env.PORT || 3000,
    dbPath: process.env.DB_PATH || 'lms.db',
    dbUser: process.env.DB_USER,
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,
};
