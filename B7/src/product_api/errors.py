from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status, error = 500, "internal_error"

    def __init__(self, detail=""):
        super().__init__(detail)
        self.detail = detail


class NotFound(ApiError):
    status, error = 404, "not_found"


class Conflict(ApiError):
    status, error = 409, "conflict"


class OutOfStock(Conflict):
    error = "out_of_stock"


def _json(status, error, detail):
    return jsonify({"error": error, "detail": detail}), status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api(e):
        return _json(e.status, e.error, e.detail)

    @app.errorhandler(ValidationError)  # Marshmallow load() fail -> 422
    def _validation(e):
        return _json(422, "validation_error", e.messages)

    @app.errorhandler(HTTPException)
    def _http(e):
        return _json(e.code, e.name.lower().replace("", "_"), e.description)

    @app.errorhandler(Exception)  # Unexpected error -> log + 500
    def _unhandled(e):
        app.logger.exception("unhandled")
        return _json(500, "internal_error", "unexpected error")
