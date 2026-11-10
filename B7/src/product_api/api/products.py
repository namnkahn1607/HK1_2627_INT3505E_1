from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from ..errors import Conflict, NotFound, OutOfStock
from ..extensions import db
from ..models import Product
from .schemas import ProductIn, ProductOut, ProductPatch, ReserveIn

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
    return jsonify(ProductOut().dump(_get_active(id)))


@products_bp.post("")
def create_product():
    body = ProductIn().load(request.get_json())
    p = Product(**body) # type: ignore
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("sku already exists")
    return jsonify(ProductOut().dump(p)), 201


@products_bp.post("/<int:id>/reserve")
def reserve_product(id):
    qty = ReserveIn().load(request.get_json())["qty"] # type: ignore
    p = _get_active(id)
    result = db.session.execute(
        db.update(Product)
        .where(Product.id == id, Product.qty_in_stock >= qty)
        .values(qty_in_stock=Product.qty_in_stock - qty)
    )
    if result.rowcount == 0: # type: ignore
        db.session.rollback()
        raise OutOfStock(f"only {p.qty_in_stock} left")
    db.session.commit()
    return jsonify(ProductOut().dump(p))


@products_bp.delete("/<int:id>")
def delete_product(id):
    p = _get_active(id)
    p.archived = True
    db.session.commit()
    return "", 204


@products_bp.patch("/<int:id>")
def patch_product(id):
    body = ProductPatch().load(request.get_json())
    p = _get_active(id)
    for k, v in body.items(): # type: ignore
        setattr(p, k, v)
    db.session.commit()
    return jsonify(ProductOut().dump(p))
