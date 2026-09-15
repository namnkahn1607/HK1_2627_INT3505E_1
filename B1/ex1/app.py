# Endpoint returning JSON, not HTML.
# Returns JSON so that any client could parse, only the browser can render HTML.
# NOTE: Not to confuse API with website!
#
# Run: curl -i http://127.0.0.1:5000
# -i or --include means including the HTTP response header.

from flask import Flask

app = Flask(__name__)

# "/" is the root path (endpoint).
# It defaults to the function index() declared below as its handler.
@app.route("/")
def index():
    # Flask 3.x auto-converts to JSON without the need to jsonify().
    return {"message": "Hello, This is API!"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
