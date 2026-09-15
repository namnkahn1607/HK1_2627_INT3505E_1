# CRUD in-memory.
#
# Schema: { "id": int, "title": str, "author": str }
# 200 - list / detail / update
# 201 - create (+Location header)
# 204 - delete (no body)
# 400 - missing "title" or "author" field
# 404 - unknown "id"

from flask import Flask, jsonify, request

_next = 1
BOOKS = [
    {
        "id": 1033001482,
        "title": "Computer System: A Programmer's Perspective",
        "author": ["Randal E. Bryant", "David R. O'Hallaron"]
    },
    {
        "id": 1985086591,
        "title": "Operating Systems: Three Easy Pieces",
        "author": ["Remzi H. Arpaci-Dusseau", "Andrea C. Arpaci-Dusseau"]
    },
    {
        "id": 1028154120,
        "title": "Engineering a Compiler",
        "author": ["Keith D. Cooper", "Linda Torczon"]
    }
]

def find(book_id):
    return next((book for book in BOOKS if book["id"] == book_id), None)

app = Flask(__name__)

@app.route("/books", methods=["GET"])
def list_books():
    n = int(request.args.get("limit", 100))
    return jsonify(BOOKS[:n], 200)

@app.route("/books/<int:bid>", methods=["GET"])
def get_book(bid):
    book = find(bid)
    if not book:
        return {"error": "book not found"}, 404
    return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a = body.get("title"), body.get("author")
    if not t or not a:
        return {"error": "need title + author"}, 400

    book = {"id": _next, "title": t, "author": a}
    BOOKS.append(book)
    _next += 1

    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}

@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return {"error": "book not found"}, 404

    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {})
        return jsonify(book), 200

    BOOKS.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
