# Multiple HTTP methods.
#
# GET /health : curl -i http://127.0.0.1:5000/health
# POST /echo  : curl -X POST http://127.0.0.1:5000/echo \
#                    -H "Content-Type: application/json" \
#                    -d '{"name":"nlnk", "age":20}'
#
# -X or --request to specify HTTP method, as curl defaults to GET method.
# -H or --header to send a custom HTTP header to a server.
# -d or --data to send specified data to server in the body of an HTTP request.

from flask import Flask, jsonify, request

# Holy crap! Flask can auto-restart server upon changing the app's source code.
app = Flask(__name__)

# GET /health: check is the server is alive.
@app.route("/health") # methods=[...] defaults to GET
def health():
    # jsonify auto set Content-Type to application/json
    return jsonify({"status": "ok"}), 200

# POST /echo: returns what the client sends.
@app.route("/echo", methods=["POST"])
# POST only receives body with the right header Content-Type.
def echo():
    # get_json() default to 200 status code. silent=False if you want it
    # to raise 400.
    data = request.get_json(silent=True) or {}
    return jsonify({"you_sent": data}), 200

if __name__ == "__main__":
    # Do not configure debug=True on production as it turns on traceback and
    # allow remote code execution (bad af).
    app.run(host="127.0.0.1", port=5000, debug=True)
