# Status codes + error validation.
#
# 1XX - Informational
# 2XX - Success
# 3XX - Redirection
# 4XX - Client-side error
# 5XX - Server-side error

from flask import Flask

ORDERS = {}  # Simulates database

app = Flask(__name__)

@app.route("/order/<id>", method=["DELETE"])
def remove_order(order_id):
    order = ORDERS.get(order_id)

    if order is None:
        return {"error": "order not found"}, 404
    if order["status"] in ["shipped", "delivered"]:
        return {"error": "order is being served - cannot remove"}, 409

    ORDERS.pop(order_id, None)
    return "", 204  # Success, no body

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
