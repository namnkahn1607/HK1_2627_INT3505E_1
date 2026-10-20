"""Helpers shared by all routes."""

import json
from pathlib import Path

from flask import current_app, g
from jsonschema import Draft202012Validator

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
