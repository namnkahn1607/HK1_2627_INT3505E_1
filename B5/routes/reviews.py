"""/books/{id}/reviews"""

from flask import Blueprint, jsonify

from models import Book, Review, User
from routes.common import commit, get_or_404, get_session, json_body, require_ref

bp = Blueprint("reviews", __name__, url_prefix="/api/v1/books/<int:book_id>/reviews")


@bp.post("")
def create_review(book_id):
    s = get_session()
    get_or_404(s, Book, book_id, "book")
    body = json_body("review_input")
    require_ref(s, User, body["userId"], "userId")
    review = Review(book_id=book_id, user_id=body["userId"], rating=body["rating"], comment=body.get("comment"))
    s.add(review)
    commit(s, "this user has already reviewed this book")
    return jsonify(review.to_dict()), 201
