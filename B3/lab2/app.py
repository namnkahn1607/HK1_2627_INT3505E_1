from flask import Flask, request, jsonify
from uuid import uuid4

user = [
    {
        "id" : 1000,
        "name" : "ok"
    }
]

app = Flask(__name__)


class ApiErr(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        super().__init__(title)
        self.status, self.title, self.detail, self.type_path = status, title, detail, type_path
        self.type = f"/error/{type_path}" if type_path else "about:oblank"
        self.extra = extra


def find_user(id):
    return next((u for u in user if u["id"] == id), None)


@app.errorhandler(ApiErr)
def handle_api_err(err: ApiErr):
    body = {
        "status": err.status,
        "title": err.title,
        "detail": err.detail if err.detail else "",
        "type": f"/error/{err.type_path}" if err.type_path else "about:oblank",
        "instance": request.path,
        "trade_id": str(uuid4())
    }

    resp = jsonify(body)
    resp.status_code = err.status
    resp.headers["Content-Type"] = "application/problem+json"

    return resp


@app.get("/users/<int:id>")
def get_user(id:int):
    user = find_user(id)
    if not user:
        raise ApiErr(status=404, title="User not found", type_path="user-not-found", resource_id=id)
    return jsonify(user)


if __name__ == "__main__":
    app.run()
