from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category as CategoryModel
from app.schemas import CategoryCreate


async def get_categories_from_db(db: AsyncSession):
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    return result.all()


async def get_category_by_id(category_id, db: AsyncSession):
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=404,
                            detail="Category not found or inactive")
    return db_category


async def check_category(category_id: int, db: AsyncSession) -> None:
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                                CategoryModel.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Category not found or inactive')


async def create_and_get_category(category: CategoryCreate, db: AsyncSession):
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def update_and_get_category(category_id: int, category: CategoryCreate, db: AsyncSession):
    db_category = await get_category_by_id(category_id, db)
    if category.parent_id is not None:
        await check_category(category.parent_id, db)

    await db.execute(update(CategoryModel)
               .where(CategoryModel.id == category_id)
               .values(**category.model_dump())
               )

    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category_by_id(category_id: int, db: AsyncSession):
    await get_category_by_id(category_id, db)
    await db.execute(update(CategoryModel)
               .where(CategoryModel.id == category_id,
                      CategoryModel.is_active == True)
               .values(is_active=False)
               )
    await db.commit()
