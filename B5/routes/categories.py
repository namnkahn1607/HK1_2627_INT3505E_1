"""/categories
Books are filtered by category (/books?category=)
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from models import Category

bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")

CATEGORY_SORTS = {"id": Category.id, "name": Category.name}
