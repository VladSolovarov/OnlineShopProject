from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(String(1000), default=None, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(
        'User',
        back_populates='reviews'
    )

    product: Mapped["Product"] = relationship(
        'Product',
        back_populates='reviews'
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),
    )