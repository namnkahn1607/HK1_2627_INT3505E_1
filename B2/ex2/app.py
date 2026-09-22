# PUT replace entirely + PATCH partly + DELETE remove.

from flask import Flask, jsonify, request, make_response

BOOKS = [
    {
        "id": 001,
        "title": "Computer System: A Programmer's Perspective",
        "author": ["Randal E. Bryant", "David R. O'Hallaron"],
        "ibsn": 1033001482
    },
    {
        "id": 002,
        "title": "Operating Systems: Three Easy Pieces",
        "author": ["Remzi H. Arpaci-Dusseau", "Andrea C. Arpaci-Dusseau"],
        "ibsn": 1985086591,
    },
    {
        "id": 004,
        "title": "Engineering a Compiler",
        "author": ["Keith D. Cooper", "Linda Torczon"],
        "ibsn": 1028154120
    }
]

app = Flask(__name__)

@app.get("/books/<int:bid>")
def fetch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify({"error": "book not found"}), 404

    response = make_response(jsonify(BOOKS[i]), 200)
    response.headers["Cache-Control"]="max-age=60"
    return response

@app.put("/books/<int:bid>")
def pud(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify({"error": "book not found"}), 404

    p = request.get_json(silent=True) or {}

    title = (p.get("title") or "").strip()
    author = p.get("author") or []
    ibsn = p.get("ibsn") or 100000000
    price = p.get("price") or 0.0
    if not title or not author:
        return jsonify({"error": "title and author are required"}), 422
    if price < 0.0:
        return jsonify({"error": "price cannot be negative"}), 422

    BOOKS[i] = {
        "id": bid,
        "title": title,
        "author": author,
        "ibsn": ibsn,
        "price": price
    }
    return jsonify(BOOKS[i]), 200

@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify({"error": "book not found"}), 404
    
    p = request.get_json(silent=True) or {}

    if p.get("price", 0.0) < 0.0:
        return jsonify({"error": "price cannot be negative"}), 422

    for k in "title author isbn price".split():
        if k in p:
            BOOKS[i][k] = p[k]
    return jsonify(BOOKS[i]), 200

@app.delete("/books/<int:bid>")
def delete(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify({"error": "book not found"}), 404

    BOOKS.pop(i)
    return "", 204

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
