from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload

from ..errors import NotFound
from ..extensions import db
from ..models import Order, OrderItem, Product
from .schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")


@orders_bp.post("")
def create_order():
    body = OrderIn().load(request.get_json())
    order = Order()
    for line in body["items"]: # type: ignore
        p = db.session.get(Product, line["product_id"])
        if p is None or p.archived:
            raise NotFound(f"product {line['product_id']} not found")
        order.items.append(
            OrderItem(product_id=p.id, qty=line["qty"], unit_price_cents=p.price_cents) # type: ignore
        )
    db.session.add(order)
    db.session.commit()
    return jsonify(OrderOut().dump(order)), 201


@orders_bp.get("")
def list_orders():
    stmt = db.select(Order).options(selectinload(Order.items)).order_by(Order.id)
    return jsonify(OrderOut(many=True).dump(db.session.scalars(stmt).all()))


@orders_bp.get("/<int:id>")
def get_order(id):
    stmt = db.select(Order).options(selectinload(Order.items)).where(Order.id == id)
    order = db.session.scalar(stmt)
    if order is None:
        raise NotFound(f"order {id} not found")
    return jsonify(OrderOut().dump(order))
