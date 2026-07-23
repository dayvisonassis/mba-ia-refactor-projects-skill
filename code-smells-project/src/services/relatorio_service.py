"""Service de Relatório — regra de desconto usando constantes nomeadas (T12 / AP-10)."""
from src.config.constants import FAIXAS_DESCONTO
from src.models import pedido_model


def relatorio_vendas():
    metricas = pedido_model.metricas_vendas()
    faturamento = metricas["faturamento"]

    desconto = 0
    for limite, taxa in FAIXAS_DESCONTO:
        if faturamento > limite:
            desconto = faturamento * taxa
            break

    total = metricas["total_pedidos"]
    por_status = metricas["por_status"]

    return {
        "total_pedidos": total,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": por_status.get("pendente", 0),
        "pedidos_aprovados": por_status.get("aprovado", 0),
        "pedidos_cancelados": por_status.get("cancelado", 0),
        "ticket_medio": round(faturamento / total, 2) if total > 0 else 0,
    }
