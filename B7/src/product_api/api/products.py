from flask import Blueprint, jsonify, request

from ..errors import NotFound
from ..extensions import db
from ..models import Product
from .schemas import ProductOut

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")


def _get_active(id):
    p = db.session.get(Product, id)
    if p is None or p.archived:
        raise NotFound(f"product {id} not found")
    return p


@products_bp.get("")
def list_products():
    page = max(1, request.args.get("page", 1, type=int))
    size = min(100, max(1, request.args.get("size", 20, type=int)))
    active = Product.archived.is_(False)

    rows = db.session.scalars(
        db.select(Product).where(active).order_by(Product.id).offset((page - 1) * size).limit(size)
    ).all()
    total = db.session.scalar(db.select(db.func.count()).select_from(Product).where(active))
    return jsonify(items=ProductOut(many=True).dump(rows), page=page, size=size, total=total)


@products_bp.get("/<int:id>")
def get_product(id):
    return jsonify(items=ProductOut().dump(_get_active(id)))
