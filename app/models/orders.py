from datetime import datetime

from sqlalchemy import String, ForeignKey, Numeric, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from decimal import Decimal


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    payment_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='orders'
    )

    items: Mapped[list['OrderItem']] = relationship(
        'OrderItem',
        back_populates='order',
        cascade='all, delete-orphan'
    )


class OrderItem(Base):
    __tablename__ = 'order_items'
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.id', ondelete='CASCADE'), index=True, nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id'), index=True, nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='order_items'
    )

    order: Mapped['Order'] = relationship(
        'Order',
        back_populates='items'
    )



