// Service de Pagamento — ISOLA a decisão de aprovação (T5 / AP-05).
//
// ATENÇÃO: este é um STUB de gateway. Numa integração real, `charge` faria uma
// chamada assíncrona ao gateway de pagamento e derivaria o status da resposta da
// transação. Aqui usamos um placeholder determinístico apenas para desenvolvimento.
//
// Correções aplicadas:
//  - A regra saiu de dentro do controller (não fica mais inline no fluxo HTTP).
//  - NUNCA loga o número do cartão nem a chave do gateway (AP-02 / PCI-DSS).

async function charge({ cardNumber, amount }) {
    // Placeholder de desenvolvimento — substituir por chamada real ao gateway.
    // (Mantém o comportamento documentado no api.http: cartões Visa "4..." aprovam.)
    const approved = String(cardNumber || '').startsWith('4');
    return { status: approved ? 'PAID' : 'DENIED' };
}

module.exports = { charge };
