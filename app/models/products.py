from datetime import datetime
from decimal import Decimal

from sqlalchemy import (String, Boolean, Index,
                        Numeric, CheckConstraint, ForeignKey,
                        text, DateTime, func, Computed)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.database import Base


class Product(Base):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_stock_positive'),
        CheckConstraint('price >= 0', name='check_price_positive'),
        Index('ix_products_tsv_gin', 'tsv', postgresql_using='gin'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False, index=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0.00,
                                            server_default=text('0'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(), onupdate=func.now(), nullable=False)

    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('english', coalesce(name, '')), 'A')
            || setweight(to_tsvector('russian', coalesce(name, '')), 'A')
            || setweight(to_tsvector('english', coalesce(description, '')), 'B')
            || setweight(to_tsvector('russian', coalesce(description, '')), 'B')
            """,
            persisted=True,
        ),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        'Category',
        back_populates='products'
    )

    seller: Mapped['User'] = relationship(
        'User',
        back_populates='products'
    )

    reviews: Mapped[list['Review']] = relationship(
        'Review',
        back_populates='product',
        uselist=True
    )

    cart_items: Mapped[list['CartItem']] = relationship(
        'CartItem',
        back_populates='product',
        uselist=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    order_items: Mapped[list['OrderItem']] = relationship(
        'OrderItem',
        uselist=True,
        back_populates='product'
    )
