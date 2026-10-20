"""/books"""

from flask import Blueprint, jsonify, request

from models import Book, Category
from routes.common import commit, get_or_404, get_session, json_body, require_ref

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")


def _apply(session, book, body):
    require_ref(session, Category, body["categoryId"], "categoryId")
    book.title = body["title"]
    book.isbn = body["isbn"]
    book.price_vnd = body["price"]["amount"]
    book.stock = body["stock"]
    book.category_id = body["categoryId"]


@bp.post("")
def create_book():
    s = get_session()
    body = json_body("book_input")
    book = Book()
    _apply(s, book, body)
    s.add(book)
    commit(s, "a book with this isbn already exists")
    return jsonify(book.to_dict()), 201, {"Location": f"/api/v1/books/{book.id}"}


@bp.get("/<int:book_id>")
def get_book(book_id):
    return jsonify(get_or_404(get_session(), Book, book_id, "book").to_dict())


@bp.put("/<int:book_id>")  # full replace of the scalar fields; authors are managed via /authors
def replace_book(book_id):
    s = get_session()
    book = get_or_404(s, Book, book_id, "book")
    _apply(s, book, json_body("book_input"))
    commit(s, "a book with this isbn already exists")
    return jsonify(book.to_dict())


@bp.delete("/<int:book_id>")
def delete_book(book_id):
    s = get_session()
    s.delete(get_or_404(s, Book, book_id, "book"))  # ORM cascade removes author links + reviews
    commit(s, "book is referenced by existing orders and cannot be deleted")
    return "", 204