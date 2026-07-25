"""Entry point da aplicação — usa a factory em src/ (composition root).

Executar com: `python app.py`
Configuração via variáveis de ambiente (ver src/config/settings.py).
"""
from src.app_factory import create_app
from src.config import settings

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://{settings.HOST}:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
