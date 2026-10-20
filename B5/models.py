"""ORM models"""

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

CURRENCY = "VND"


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(100))

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

