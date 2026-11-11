from sqlalchemy import event

from product_api.extensions import db

P = "/api/v1/products"
O = "/api/v1/orders"


def make_product(client, sku="ABC-1", **extra):
    body = {"sku": sku, "name": "Item", "price_cents": 100, **extra}
    return client.post(P, json=body)


# ─── POST ───
def test_create_product(client):
    r = make_product(client, qty_in_stock=5)
    assert r.status_code == 201
    assert r.json["sku"] == "ABC-1" and r.json["qty_in_stock"] == 5


def test_create_duplicate_sku_returns_409(client):
    make_product(client)
    r = make_product(client)
    assert r.status_code == 409
    assert r.json["error"] == "conflict"


def test_create_invalid_returns_422(client):
    r = client.post(P, json={"sku": "x", "name": "", "price_cents": -1})
    assert r.status_code == 422
    assert r.json["error"] == "validation_error"


# ─── GET / PATCH / DELETE / reserve ───
def test_get_missing_returns_404(client):
    r = client.get(f"{P}/999")
    assert r.status_code == 404 and r.json["error"] == "not_found"


def test_list_pagination(client):
    for i in range(3):
        make_product(client, sku=f"SKU-{i}")
    r = client.get(f"{P}?page=2&size=2")
    assert r.json["total"] == 3 and r.json["page"] == 2
    assert len(r.json["items"]) == 1


def test_patch_only_changes_given_fields(client):
    pid = make_product(client).json["id"]
    r = client.patch(f"{P}/{pid}", json={"name": "New"})
    assert r.json["name"] == "New" and r.json["price_cents"] == 100


def test_soft_delete_hides_product(client):
    pid = make_product(client).json["id"]
    assert client.delete(f"{P}/{pid}").status_code == 204
    assert client.get(f"{P}/{pid}").status_code == 404
    assert client.get(P).json["total"] == 0


def test_reserve_decreases_stock_and_rejects_oversell(client):
    pid = make_product(client, qty_in_stock=2).json["id"]
    r = client.post(f"{P}/{pid}/reserve", json={"qty": 2})
    assert r.status_code == 200 and r.json["qty_in_stock"] == 0
    r = client.post(f"{P}/{pid}/reserve", json={"qty": 1})
    assert r.status_code == 409 and r.json["error"] == "out_of_stock"


# ─── Orders ───
def test_create_order_computes_total(client):
    pid = make_product(client).json["id"]
    r = client.post(O, json={"items": [{"product_id": pid, "qty": 3}]})
    assert r.status_code == 201 and r.json["total_cents"] == 300


def test_create_order_unknown_product_returns_404(client):
    r = client.post(O, json={"items": [{"product_id": 999, "qty": 1}]})
    assert r.status_code == 404


def test_list_orders_has_no_n_plus_1(app, client):
    pid = make_product(client).json["id"]
    for _ in range(5):
        client.post(O, json={"items": [{"product_id": pid, "qty": 1}] * 2})

    statements = []

    def count(statement):
        statements.append(statement)

    with app.app_context():
        engine = db.engine
    event.listen(engine, "before_cursor_execute", count)
    r = client.get(O)
    event.remove(engine, "before_cursor_execute", count)

    assert len(r.json) == 5 and all(len(o["items"]) == 2 for o in r.json)
    assert len(statements) == 2


# ─── Health ───
def test_health_endpoints(client):
    assert client.get("/healthz").status_code == 200
    r = client.get("/ready")
    assert r.status_code == 200 and r.json["checks"]["db"] == "ok"
