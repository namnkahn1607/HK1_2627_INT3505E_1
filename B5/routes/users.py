"""/users"""

from flask import Blueprint, jsonify

from models import User
from routes.common import commit, get_session, json_body

bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@bp.post("")
def create_user():
    s = get_session()
    body = json_body("user_input")
    user = User(email=body["email"], display_name=body["displayName"])
    s.add(user)
    commit(s, "this email is already registered")
    return jsonify(user.to_dict()), 201
