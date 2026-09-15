# Read JSON from request body.
# Reads JSON from client, validates, creates the resource then returns
# 201 Created.
#
# NOTE: Never return stacktrace/HTTP upon error.
#       Explicitly return {"error":"..."} with 4xx/5xx status code.
#
# Valid -> 201 : curl -X POST localhost:5000/students \
#                     -H "Content-Type: application/json" \
#                     -d '{"name":"nlnk", "gpa": 3.6}'
# Missing "name" -> 400 : curl -X POST localhost:5000/students \
#                              -H "Content-Type: application/json" \
#                              -d '{"gpa": 4.0}'

from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
STUDENTS = []

@app.route("/students", methods=["POST"])
def submit_student():
    body = request.get_json(silent=True) or {}

    name = body.get("name")
    if not name:
        return jsonify({"error":"name is mandatory"}), 400

    student = {
        "id": str(uuid4()), # Random 128-bit ID
        "name": name,
        "gpa": body.get("gpa", 0.0) # Default to 0.0 upon missing field
    }
    STUDENTS.append(student)

    # Response should have header Location pointing to new resource.
    return student, 201

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
