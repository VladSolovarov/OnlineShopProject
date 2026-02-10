from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import (CategoryCreate,
                         Category as CategorySchema,
                         Product as ProductSchema, ProductCreate)


async def get_products_from_db(db: Session, category_id: int | None = None):
    if category_id is not None:
        await check_category(category_id, db)
        stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                          ProductModel.is_active == True)
    else:
        stmt = select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
                                                              CategoryModel.is_active == True,
                                                              ProductModel.stock > 0)
    products = db.scalars(stmt).all()
    return products


async def check_category(category_id: int, db: Session) -> None:
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                                CategoryModel.is_active == True)
    if db.scalars(category_stmt).first() is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Category not found or inactive')


async def get_product_by_id(product_id: int, db: Session):
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    db_product = db.scalars(stmt).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail='Product not found or inactive')
    return db_product


async def create_and_get_product(product: ProductCreate, db: Session):
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


async def update_and_get_product(product_id: int, product: ProductCreate, db: Session):
    db_product = await get_product_by_id(product_id, db)
    await check_category(db_product.category_id, db)
    db.execute(update(ProductModel)
               .where(ProductModel.id == product_id)
               .values(**product.model_dump())
               )

    db.commit()
    db.refresh(db_product)
    return db_product


async def delete_product_by_id(product_id: int, db: Session):
    await get_product_by_id(product_id, db)
    db.execute(update(ProductModel)
               .where(ProductModel.id == product_id,
                      ProductModel.is_active == True)
               .values(is_active=False)
               )
    db.commit()