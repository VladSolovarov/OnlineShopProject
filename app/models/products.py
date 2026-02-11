from decimal import Decimal

from sqlalchemy import String, Boolean, Numeric, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CategoryCreate(Base):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_stock_positive'),
        CheckConstraint('price >= 0', name='check_price_positive')
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)

    category: Mapped["Category"] = relationship(
        'Category',
        back_populates='products'
    )