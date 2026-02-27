from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Review as ReviewModel, User as UserModel, Product as ProductModel
from app.routers.operations.products_operations import get_product_by_id
from app.schemas import Review as ReviewSchema, ReviewCreate
from sqlalchemy import select, update
from sqlalchemy.sql import func
from app.db_depends import get_async_db


async def get_reviews_from_db(db: AsyncSession, product_id: int | None = None):
    if product_id is None:
        reviews_stmt = select(ReviewModel).where(ReviewModel.is_active == True)
    else:
        reviews_stmt = select(ReviewModel).where(ReviewModel.is_active == True,
                                                 ReviewModel.product_id == product_id)

    reviews = (await db.scalars(reviews_stmt)).all()
    return reviews


async def get_review_by_id(review_id: int, db: AsyncSession):
    review_stmt = select(ReviewModel).where(ReviewModel.id == review_id,
                                            ReviewModel.is_active == True)
    db_review = (await db.scalars(review_stmt)).first()
    if db_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found or inactive")
    return db_review


async def create_and_get_review(review: ReviewCreate,
                                db: AsyncSession,
                                current_buyer: UserModel):
    db_review = ReviewModel(**review.model_dump(), user_id=current_buyer.id)
    db.add(db_review)
    await update_product_rating(db, db_review.product_id)
    await db.refresh(db_review)
    return db_review


async def check_admin_or_author(db: AsyncSession, current_user: UserModel):
    if current_user.role != 'admin':
        review_stmt = select(ReviewModel).where(ReviewModel.user_id == current_user.id,
                                                ReviewModel.is_active == True)
        db_review = (await db.scalars(review_stmt)).first()
        if db_review is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='User must be an author or admin')


async def delete_and_get_review(db_review: ReviewModel, db: AsyncSession):
    await db.execute(update(ReviewModel)
                     .where(ReviewModel.id == db_review.id,
                            ReviewModel.is_active == True)
                     .values(is_active=False)
                     )
    await update_product_rating(db, db_review.product_id)
    await db.refresh(db_review)
    return db_review


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()
