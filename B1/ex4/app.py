# Path params + query string.
# Path params are used to point to a specific resource. Cannot bypass.
# Ex: /user/42, /orders/ord_234
#
# Query string is used to filter/sort/paging.
# Ex: ?limit=12&sort=-updated
#
# NOTE: Verbs should not be allowed in URL.

from flask import Flask, jsonify, request

BOOKS = [
    {
        "id": "0133001482",
        "title": "Computer System: A Programmer's Perspective",
        "author": ["Randal E. Bryant", "David R. O'Hallaron"]
    },
    {
        "id": "198508659X",
        "title": "Operating Systems: Three Easy Pieces",
        "author": ["Remzi H. Arpaci-Dusseau", "Andrea C. Arpaci-Dusseau"]
    },
    {
        "id": "0128154120",
        "title": "Engineering a Compiler",
        "author": ["Keith D. Cooper", "Linda Torczon"]
    }
]

def find_by_id(book_id: str) -> dict | None:
    for book in BOOKS:
        if book["id"] == book_id:
            return book

    return None

app = Flask(__name__)

@app.route("/book")
def list_book():
    limit = int(request.args.get("limit", 20))
    q = request.args.get("q", "").strip().lower()
    items = [book for book in BOOKS if q in book["title"].lower()]
    del items[limit:]
    return jsonify({"items": items}), 200

@app.route("/book/<book_id>")
def get_book(book_id):
    book = find_by_id(book_id)
    if book is None:
        return jsonify({"error": "book not found"}), 404
    return jsonify(book), 200

@app.route("/items/<int:item_id>")
def get_item(item_id: int):
    return jsonify({"id": item_id}), 200

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
