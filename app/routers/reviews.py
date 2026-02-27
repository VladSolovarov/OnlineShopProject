from fastapi import APIRouter, Depends, status

from app.auth import get_current_buyer, get_current_user
from app.models import Review as ReviewModel
from app.models.users import User as UserModel
from app.routers.operations.products_operations import get_product_by_id
from app.routers.operations.reviews_operations import create_and_get_review, \
    get_reviews_from_db, check_admin_or_author, get_review_by_id, delete_and_get_review
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_async_db
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=['reviews'])


@router.get('/reviews', response_model=list[ReviewSchema])
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    reviews = await get_reviews_from_db(db)
    return reviews


@router.get('/products/{product_id}/reviews', response_model=list[ReviewSchema])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)):
    await get_product_by_id(product_id, db)
    reviews = await get_reviews_from_db(db, product_id)
    return reviews


@router.post('/reviews', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate,
                      db: AsyncSession = Depends(get_async_db),
                      current_buyer: UserModel = Depends(get_current_buyer)):
    await get_product_by_id(review.product_id, db)
    db_review = await create_and_get_review(review, db, current_buyer)
    return db_review


@router.delete('/reviews/{review_id}', response_model=ReviewSchema)
async def delete_review(review_id: int,
                        db: AsyncSession = Depends(get_async_db),
                        current_user=Depends(get_current_user)):
    db_review = await get_review_by_id(review_id, db)
    await check_admin_or_author(db, current_user)
    return await delete_and_get_review(db_review, db)
