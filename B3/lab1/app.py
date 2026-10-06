from datetime import datetime, timezone

from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

POSTS = {
    1: {"id": 1, "author_id": 1, "title": "Hello REST", "body": "First post",
        "tags": ["intro"], "created_at": "2026-09-30T00:00:00+00:00"},
}
next_id = 2


def error(status, message):
    return jsonify(error={"message": message}), status


def validate(data, partial=False):
    if not isinstance(data, dict):
        return None, "Body must be a JSON object"
    clean = {}
    for field in ("title", "body"):
        if field in data or not partial:
            v = data.get(field)
            if not isinstance(v, str) or not v.strip():
                return None, f"'{field}' must be a non-empty string"
            clean[field] = v.strip()
    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            return None, "'tags' must be a list of strings"
        clean["tags"] = [t.strip().lower() for t in tags]
    elif not partial:
        clean["tags"] = []
    return clean, None


@app.get("/api/v1/posts")
def list_posts():
    items = sorted(POSTS.values(), key=lambda p: p["id"], reverse=True)
    tag = request.args.get("tag")
    if tag:
        items = [p for p in items if tag.lower() in p["tags"]]
    return jsonify(data=items, total=len(items))


@app.post("/api/v1/posts")
def create_post():
    global next_id
    data = request.get_json(silent=True)
    clean, err = validate(data)
    if err:
        return error(422, err)
    if data.get("author_id") is None:  # type: ignore
        return error(422, "'author_id' is required")
    post = {"id": next_id, "author_id": data["author_id"], **clean, # type: ignore
            "created_at": datetime.now(timezone.utc).isoformat()}
    POSTS[next_id] = post
    next_id += 1
    return jsonify(post), 201, {"Location": url_for("get_post", post_id=post["id"])}


@app.get("/api/v1/posts/<int:post_id>")
def get_post(post_id):
    post = POSTS.get(post_id)
    return jsonify(post) if post else error(404, f"Post {post_id} not found")


@app.route("/api/v1/posts/<int:post_id>", methods=["PUT", "PATCH"])
def update_post(post_id):
    post = POSTS.get(post_id)
    if not post:
        return error(404, f"Post {post_id} not found")
    clean, err = validate(request.get_json(silent=True), partial=request.method == "PATCH")
    if err:
        return error(422, err)
    post.update(clean) # type: ignore
    return jsonify(post)


@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id):
    if POSTS.pop(post_id, None) is None:
        return error(404, f"Post {post_id} not found")
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
