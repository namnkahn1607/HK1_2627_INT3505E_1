# GET list + POST create.

from flask import Flask, jsonify, request, make_response

_next_id = 1
BOOKS = []

app = Flask(__name__)

@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)
    }), 200

@app.post("/books")
def create_book():
    global _next_id
    if not request.is_json:
        return jsonify({"error": "expected JSON"}), 415

    p = request.get_json(silent=True) or {}

    t = (p.get("title") or "").strip()
    a = p.get("author") or []
    if not t or not a:
        return jsonify({"error": "title and author required"}), 422

    book = {"id": _next_id, "title": t, "author": a}
    BOOKS.append(book)
    _next_id += 1

    response = make_response(jsonify(book), 201)
    response.headers["Location"] = f"/books/{book['id']}"
    return response

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
