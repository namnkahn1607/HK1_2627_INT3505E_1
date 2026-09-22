# Pagination, filtering, HATEOAS links and Cache-Control.

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

DEFAULT_SIZE, MAX_SIZE = 20, 100

@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be integer"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    # Filter
    flt = BOOKS

    a = request.args.get("author")
    if a:
        flt = [b for b in flt if b["author"].lower() == a.lower()]

    q = (request.args.get("q") or "").lower()
    if q:
        flt = [b for b in flt if q in b["title"].lower()]

    # Pagination
    total = len(flt)
    start = (page - 1) * size
    end = start + size
    items = flt[start:end]
    last = (total + size - 1) // size

    # HATEOAS links
    def u(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {"href": u(page)},
        "first": {"href": u(1)},
        "last": {"href": u(max(last, 1))},
    }

    if page > 1:
        links["prev"] = {"href": u(page - 1)}
    if end < total:
        links["next"] = {"href": u(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": last,
        },
        "_links": links
    }

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp
