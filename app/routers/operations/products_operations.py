from fastapi import HTTPException, status
from sqlalchemy import select, update, func, and_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product as ProductModel, Category as CategoryModel, User as UserModel
from app.routers.operations.categories_operations import check_category_by_id
from app.schemas import ProductCreate

from enum import Enum

class ProductSortField(str, Enum):
    ID = 'id'
    DATE = 'date'
    PRICE = 'price'
    RATING = 'rating'
    NAME = 'name'


class SortOrder(str, Enum):
    ASC = 'asc'
    DESC = 'desc'


async def get_product_by_id(product_id: int, db: AsyncSession):
    products_stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    db_product = (await db.scalars(products_stmt)).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail='Product not found or inactive')
    return db_product


async def get_total_products(db: AsyncSession) -> int:
    total_stmt = (
        select(func.count())
        .select_from(ProductModel)
        .where(ProductModel.is_active == True)
    )
    total = (await db.scalars(total_stmt)).one_or_none()
    return total or 0


def get_sort(sort_by, order):
    sort_mapping = {
        ProductSortField.ID: ProductModel.id,
        ProductSortField.DATE: ProductModel.created_at,
        ProductSortField.PRICE: ProductModel.price,
        ProductSortField.RATING: ProductModel.rating,
        ProductSortField.NAME: ProductModel.name
    }
    order_func = asc if order == SortOrder.ASC else desc # JUST FOR PRACTICING
    return order_func(sort_mapping[sort_by])


async def get_filters(db: AsyncSession, category_id, min_price,
                      max_price, in_stock, seller_id) -> list:
    filters = [
        ProductModel.is_active == True,
        CategoryModel.is_active == True
    ]
    if category_id is not None:
        await check_category_by_id(category_id, db)
        filters.append(ProductModel.category_id == category_id)
    if min_price is not None:
        filters.append(ProductModel.price >= min_price)
    if max_price is not None:
        filters.append(ProductModel.price <= max_price)
    if in_stock is not None:
        filters.append(ProductModel.stock > 0 if in_stock
                       else ProductModel.stock == 0)
    if seller_id is not None:
        filters.append(ProductModel.seller_id == seller_id)

    return filters


async def get_products_from_db(db: AsyncSession, page: int, page_size: int,
                               filters_sequence: tuple,
                               sort_by: ProductSortField,
                               order: SortOrder):
    """get filtered products"""
    total = await get_total_products(db)
    db_filters = await get_filters(db, *filters_sequence)
    sort_by = get_sort(sort_by, order)

    products_stmt = (
        select(ProductModel)
        .join(CategoryModel)
        .where(and_(*db_filters))
        .order_by(sort_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    db_products = (await db.scalars(products_stmt)).all()
    return {
        "items": db_products,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def create_and_get_product(product: ProductCreate,
                                 db: AsyncSession,
                                 current_seller: UserModel):
    db_product = ProductModel(**product.model_dump(),
                              seller_id=current_seller.id)
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



