from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category as CategoryModel
from app.schemas import CategoryCreate


async def get_categories_from_db(db: AsyncSession):
    categories_stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    categories = (await db.scalars(categories_stmt)).all()
    return categories


async def get_category_by_id(category_id, db: AsyncSession):
    categories_stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    db_category = (await db.scalars(categories_stmt)).first()
    if db_category is None:
        raise HTTPException(status_code=404,
                            detail="Category not found or inactive")
    return db_category


async def check_category_by_id(category_id: int, db: AsyncSession) -> None:
    categories_stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                                CategoryModel.is_active == True)
    db_category = (await db.scalars(categories_stmt)).first()
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
        await check_category_by_id(category.parent_id, db)

    await db.execute(update(CategoryModel)
               .where(CategoryModel.id == category_id)
               .values(**category.model_dump())
               )

    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_and_get_category(db_category: CategoryModel, db: AsyncSession):
    await db.execute(update(CategoryModel)
               .where(CategoryModel.id == db_category.id,
                      CategoryModel.is_active == True)
               .values(is_active=False)
               )
    await db.commit()
    await db.refresh(db_category)
    return db_category
