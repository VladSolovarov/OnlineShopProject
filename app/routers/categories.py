from fastapi import APIRouter, Depends

from app.routers.db_operations import create_and_get_category, update_and_get_category, get_categories_from_db, \
    check_category, delete_category_by_id
from app.schemas import CategoryCreate, Category as CategorySchema

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.get('/', response_model=list[CategorySchema], status_code=200)
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """Get a list of all categories"""
    return await get_categories_from_db(db)


@router.post('/', response_model=CategorySchema, status_code=201)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new category"""
    if category.parent_id is not None:
        await check_category(category.parent_id, db)
    return await create_and_get_category(category, db)


@router.put('/{category_id}', response_model=CategorySchema, status_code=200)
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """Update category by id"""
    return await update_and_get_category(category_id, category, db)


@router.delete('/{category_id}', status_code=200)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """Set is_active=False of Category by id"""
    await delete_category_by_id(category_id, db)
    return {"status": "success", "message": "Category marked as inactive"}