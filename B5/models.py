"""ORM models"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

CURRENCY = "VND"


class Base(DeclarativeBase):
    pass


def utcnow():
    return datetime.now(timezone.utc)


def iso(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def money(amount):
    return {"amount": amount, "currency": CURRENCY}


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(100))
    bio: Mapped[Optional[str]] = mapped_column(Text)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    def to_dict(self):  # do not expose email
        return {"id": self.id, "displayName": self.display_name, "createdAt": iso(self.created_at)}


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (CheckConstraint("price_vnd >= 0"), CheckConstraint("stock >= 0"))

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    price_vnd: Mapped[int]
    stock: Mapped[int] = mapped_column(default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    category: Mapped[Category] = relationship()
    author_links: Mapped[list["BookAuthor"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", order_by="BookAuthor.author_id"
    )
    reviews: Mapped[list["Review"]] = relationship(cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price": money(self.price_vnd),
            "stock": self.stock,
            "inStock": self.stock > 0,
            "category": self.category.to_dict(),
            "authors": [link.to_dict() for link in self.author_links],
            "createdAt": iso(self.created_at),
        }


class BookAuthor(Base):  # Another temporary stub
    def to_dict(self):
        pass


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5"),
        UniqueConstraint("book_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int]
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "bookId": self.book_id,
            "userId": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "createdAt": iso(self.created_at),
        }
