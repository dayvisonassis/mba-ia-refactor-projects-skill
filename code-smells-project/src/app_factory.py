"""Application factory — monta e conecta as camadas (composition root)."""
import logging

from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.database.connection import close_db, init_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import api


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)
    app.teardown_appcontext(close_db)

    app.register_blueprint(api)
    register_error_handlers(app)

    with app.app_context():
        init_db()

    return app
