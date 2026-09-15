#!/usr/env/bash
set -euo pipefail

# GET (list): 200 OK
curl -i http://localhost:5000/books

# GET (detail): 200 OK
curl -i http://localhost:5000/books/1028154120

# POST (create): 201 Created
curl -iX POST http://localhost:5000/books \
     -H "Content-Type: application/json" \
     -d '{"id": 1098119058, "title": "Designing Data-Intensive Application", "author": "Martin Kleppmann"}'

# PUT (update): 200 OK
curl -iX PUT http://localhost:5000/books/1033001482 \
     -H "Content-Type: application/json" \
     -d '{"title": "CS:APP3e"}'
    
# DELETE: 204 No Content
curl -iX DELETE http://localhost:5000/books/1033001482

# POST (create): 400 Bad Request
curl -iX POST http://localhost:5000/books \
     -H "Content-Type: application/json" \
     -d '{}'
