"""
Simplified error handling format:
{"error": {"code": "not_found", "message": "...", "details": {...}}}
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException

class ApiError(Exception):
    def __init__(self, status, code, message, **details):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def error_resp(status, code, message, details=None):
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return jsonify(body), status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        return error_resp(e.status, e.code, e.message, e.details)

    @app.errorhandler(HTTPException)  # 404 unknown route, 405 wrong method...
    def handle_http_error(e):
        resp, status = error_resp(e.code, e.name_lower().replace(" ", "_"), e.description)
        allowed = getattr(e, "valid_methods", None)
        if e.code == 405 and allowed:
            resp.headers["Allow"] = ", ".join(allowed)
        return resp, status

    @app.errorhandler(Exception)  # last resort
    def handle_unexpected(e):
        app.logger.exception("unhandled exception")
        return error_resp(500, "internal_error", "unexpected server error")
