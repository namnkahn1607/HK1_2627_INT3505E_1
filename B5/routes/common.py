"""Helpers shared by all routes."""

import json
from pathlib import Path

from flask import current_app, g, request
from jsonschema import Draft202012Validator

from errors import ApiError

def _load_schemas():
    validators = {}
    for path in (Path(__file__).resolve().parent.parent / "schemas").glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validators[path.stem] = Draft202012Validator(schema)
    return validators


SCHEMAS = _load_schemas()


def get_session():
    """Each request use one SQLAlchemy session. Closed upon teardown."""
    if "db" not in g:
        # Default to app's own factory in case db is not configured manually.
        g.db = current_app.extensions["session_factory"]()
    return g.db


def close_session():
    db = g.pop("db", None)
    if db is not None:
        db.close()

def json_body(schema_name):
    """Parse request body and validate against the defined JSON schema."""
    payload = request.get_json(silent=True)
    if payload is None:
        raise ApiError(400, "invalid_json", "body must be a valid JSON with Content-Type: application/json")

    errors = sorted(SCHEMAS[schema_name].iter_errors(payload), key=lambda e: [str(p) for p in e.path])
    if errors:
        raise ApiError(
            400,
            "validation_failed",
            "request body does not match schema",
            errors=[{"field": "/".join(str(p) for p in e.path), "message": e.message} for e in errors],
        )
    return payload
