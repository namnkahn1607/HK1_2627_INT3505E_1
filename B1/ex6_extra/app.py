from flask import Flask, jsonify, request

_next = 2000000000
BOOKS = [
    {
        "id": 1033001482,
        "title": "Computer System: A Programmer's Perspective",
        "author": ["Randal E. Bryant", "David R. O'Hallaron"],
        "year": 2015
    },
    {
        "id": 1985086591,
        "title": "Operating Systems: Three Easy Pieces",
        "author": ["Remzi H. Arpaci-Dusseau", "Andrea C. Arpaci-Dusseau"],
        "year": 2018
    },
    {
        "id": 1028154120,
        "title": "Engineering a Compiler",
        "author": ["Keith D. Cooper", "Linda Torczon"],
        "year": 2011
    }
]

def find(book_id):
    return next((book for book in BOOKS if book["id"] == book_id), None)

def validate_year(year) -> tuple[bool, str | None]:
    if type(year) is not int:
        return False, "'year' must be an integer"
    if year < 1900:
        return False, "'year' must be >= 1900"
    return True, None

app = Flask(__name__)

@app.route("/books", methods=["GET"])
def list_books():
    results = list(BOOKS)

    # (a) /books?q=...
    q = request.args.get("q", "").strip().lower()
    if q:
        results = [
            book for book in BOOKS
            if q in book["title"].lower()
        ]

    # (b) ?sort=title
    sort_param = request.args.get("sort", "").strip()
    if sort_param:
        reverse = sort_param.startswith("-")
        sort_key = sort_param.lstrip("-")
        if sort_key not in {"title", "year", "id"}:
            return jsonify({"error": "invalid sort parameter"}), 400
        
        if sort_key == "title":
            results.sort(key=lambda b: str(b["title"]).lower(), reverse=reverse)
        else:
            results.sort(key=lambda b: int(b[sort_key]), reverse=reverse)

    lim = int(request.args.get("limit", 100))
    return jsonify(BOOKS[:lim]), 200

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
    t, a, y = body.get("title"), body.get("author"), body.get("year")
    if not t or not a or not y:
        return {"error": "need title + author"}, 400

    # (c) year must be >= 1900
    valid, err_msg = validate_year(y)
    if not valid:
        return jsonify({"error": err_msg}), 400

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
