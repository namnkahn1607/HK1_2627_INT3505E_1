"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

from jsonschema import validate, ValidationError
import pytest
from tools import get_book_schema

def test_get_books_empty_db(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data is not None
    assert data == []


def test_get_book_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == "NOT_FOUND"


def test_post_book_missing_title(client):
    response = client.post("/books", json={"author": "Robert C. Martin"})
    assert response.status_code == 400
    data = response.get_json()
    assert data.get("code") == "VALIDATION_ERROR"
    assert "errors" in data
    assert any(err.get("field") == "title" for err in data["errors"])


def test_delete_then_get(client):
    create_res = client.post(
        "/books",
        json={"title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    )
    assert create_res.status_code == 201
    book_id = create_res.get_json()["id"]

    delete_res = client.delete(f"/books/{book_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 404

@pytest.fixture
def leaked_book_fixture(client, sample_book):
    response = client.get(f"/books/{sample_book}")
    assert response.status_code == 200
    data = response.get_json()
    data["password_hash"] = "pbkdf2:sha256:260000$secret$hash"
    return data


def test_response_extra_field_blocked(client, sample_book, leaked_book_fixture):
    schema = get_book_schema()

    response = client.get(f"/books/{sample_book}")
    assert response.status_code == 200
    book_data = response.get_json()
    validate(instance=book_data, schema=schema)

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=leaked_book_fixture, schema=schema)

    assert "password_hash" in str(exc_info.value)
