from sqlalchemy import String, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


if __name__ == "__main__":
    from sqlalchemy.schema import CreateTable
    from app.models.products import Product
    print(CreateTable(Category.__table__))
    print(CreateTable(Product.__table__))