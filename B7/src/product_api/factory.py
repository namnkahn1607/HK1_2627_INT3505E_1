from flask import Flask

from . import models
from .api.products import products_bp
from .config import DefaultConfig
from .errors import register_error_handlers
from .extensions import db, migrate


def create_app(config=DefaultConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(products_bp)
    register_error_handlers(app)
    return app
