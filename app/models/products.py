from decimal import Decimal

from sqlalchemy import String, Boolean, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_stock_positive'),
        CheckConstraint('price >= 0', name='check_price_positive')
    )


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200))
    stock: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
