# N + 1 problem demo.

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
app.config['SQLALCHEMY_ECHO'] = True  # Show real SQL query in console
db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    books = db.relationship('Book', backref='author')  # Default: lazy='select'

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

@app.route('/seed')
def seed():
    db.create_all()
    for i in range(5):
        a = Author(name=f"Author {i}")  # type: ignore
        a.books = [Book(title=f"Book {i}-{j}") for j in range(3)]  # type: ignore
        db.session.add(a)
    db.session.commit()
    return "seeded"

# BUG: 1 query to get authors, another N queries to get books for each author.
@app.route('/nplus1')
def nplus1():
    authors = Author.query.all()
    return jsonify([{a.name: [b.title for b in a.books]} for a in authors])

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
