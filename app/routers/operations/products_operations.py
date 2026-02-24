from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product as ProductModel, Category as CategoryModel, User as UserModel
from app.routers.operations.categories_operations import check_category
from app.schemas import ProductCreate


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


async def create_and_get_product(product: ProductCreate,
                                 db: AsyncSession,
                                 current_seller: UserModel):
    db_product = ProductModel(**product.model_dump(), seller_id=current_seller.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def update_and_get_product(db_product,
                                 product: ProductCreate,
                                 db: AsyncSession):
    await db.execute(update(ProductModel)
               .where(ProductModel.id == db_product.id)
               .values(**product.model_dump())
               )
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def check_product_seller(product, current_seller: UserModel):
    """does current seller own product"""
    if product.seller_id != current_seller.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only update your own products")


async def delete_and_get_product(db_product, db: AsyncSession):
    await db.execute(update(ProductModel)
               .where(ProductModel.id == db_product.id,
                      ProductModel.is_active == True)
               .values(is_active=False)
               )
    await db.commit()
    await db.refresh(db_product)
    return db_product
