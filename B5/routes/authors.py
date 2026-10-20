"""/authors"""

from flask import Blueprint, jsonify

from models import Author
from routes.common import commit, get_session, json_body

bp = Blueprint("authors", __name__, url_prefix="/api/v1/authors")

@bp.post("")
def create_author():
    s = get_session()
    body = json_body("author_input")
    author = Author(name=body["name"])
    s.add(author)
    commit(s, "author could not be created")
    return jsonify(author.to_dict()), 201, {"Location": f"/api/v1/authors/{author.id}"}
