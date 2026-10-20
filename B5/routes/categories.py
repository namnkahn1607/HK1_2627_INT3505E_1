"""/categories
Books are filtered by category (/books?category=)
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from models import Category
from routes.common import commit, get_session, json_body

bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")

CATEGORY_SORTS = {"id": Category.id, "name": Category.name}


@bp.post("")
def create_category():
    s = get_session()
    body = json_body("category_input")
    category = Category(name=body["name"])
    s.add(category)
    commit(s, "a category this name already exists")
    return jsonify(category.to_dict()), 201, {"Location": f"/api/v1/categories/{category.id}"}
