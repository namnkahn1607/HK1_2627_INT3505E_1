"""Helpers shared by all routes."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

def _load_schemas():
    validators = {}
    for path in (Path(__file__).resolve().parent.parent / "schemas").glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validators[path.stem] = Draft202012Validator(schema)
    return validators

SCHEMAS = _load_schemas()
