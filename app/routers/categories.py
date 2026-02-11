from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.db_depends import get_db

from app.models.categories import Category as CategoryModel
from app.routers.db_operations import create_and_get_category, update_and_get_category, get_categories_from_db, \
    check_category, get_category_by_id, delete_category_by_id
from app.schemas import CategoryCreate, Category as CategorySchema


router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.get('/', response_model=list[CategorySchema], status_code=200)
async def get_all_categories(db: Session = Depends(get_db)):
    """Get a list of all categories"""
    return await get_categories_from_db(db)


@router.post('/', response_model=CategorySchema, status_code=201)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    if category.parent_id is not None:
        await check_category(category.parent_id, db)
    return await create_and_get_category(category, db)


@router.put('/{category_id}', response_model=CategorySchema, status_code=200)
async def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """Update category by id"""
    return await update_and_get_category(category_id, category, db)


@router.delete('/{category_id}', status_code=200)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Set is_active=False of Category by id"""
    await delete_category_by_id(category_id, db)
    return {"status": "success", "message": "Category marked as inactive"}