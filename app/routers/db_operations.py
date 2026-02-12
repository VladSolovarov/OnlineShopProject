from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import (CategoryCreate,
                         Category as CategorySchema,
                         Product as ProductSchema, ProductCreate)

from sqlalchemy.ext.asyncio import AsyncSession


#PRODUCT ROUTERS
async def get_products_from_db(db: AsyncSession, category_id: int | None = None):
    if category_id is not None:
        await check_category(category_id, db)
        stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                          ProductModel.is_active == True)
    else:
        stmt = select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
                                                              CategoryModel.is_active == True,
                                                              ProductModel.stock > 0)
    result = await db.scalars(stmt)
    products = result.all()
    return products


async def get_product_by_id(product_id: int, db: AsyncSession):
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    result = await db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail='Product not found or inactive')
    return db_product


async def create_and_get_product(product: ProductCreate, db: AsyncSession):
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def update_and_get_product(product_id: int, product: ProductCreate, db: AsyncSession):
    db_product = await get_product_by_id(product_id, db)
    await check_category(db_product.category_id, db)
    await db.execute(update(ProductModel)
               .where(ProductModel.id == product_id)
               .values(**product.model_dump())
               )

    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product_by_id(product_id: int, db: AsyncSession):
    await get_product_by_id(product_id, db)
    await db.execute(update(ProductModel)
               .where(ProductModel.id == product_id,
                      ProductModel.is_active == True)
               .values(is_active=False)
               )
    await db.commit()

#CATEGORY ROUTERS
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