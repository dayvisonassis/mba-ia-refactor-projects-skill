"""Constantes de domínio — elimina magic numbers e listas mágicas (T12 / AP-10)."""

NOME_MIN_LEN = 2
NOME_MAX_LEN = 200

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

# (limite de faturamento, taxa de desconto) — avaliado de cima para baixo
FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
