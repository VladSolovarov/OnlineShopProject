from pathlib import Path
from fastapi import (
    HTTPException,
    status, UploadFile
)
from sqlalchemy import select, update, func, and_, asc, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product as ProductModel, Category as CategoryModel, User as UserModel
from app.services.categories import check_category_by_id
from app.schemas import ProductCreate

from enum import Enum
import uuid


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_ROOT = BASE_DIR / "media" / "products"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_IMAGE_SIZE = 1024 * 1024 * 2


class ProductSortField(str, Enum):
    ID = 'id'
    DATE = 'date'
    PRICE = 'price'
    RATING = 'rating'
    NAME = 'name'


class SortOrder(str, Enum):
    ASC = 'asc'
    DESC = 'desc'


async def save_product_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Content type is not allowed (Must be JPG, PNG or WebP)")
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Image size is too large")
    extension = Path(file.filename or '').suffix.lower() or '.jpg'
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / file_name
    file_path.write_bytes(content)
    return f"/media/products/{file_name}"


def remove_product_image(url: str | None) -> None:
    if not url:
        return
    relative_path = url.lstrip('/')
    file_path = BASE_DIR / relative_path
    if file_path.exists():
        file_path.unlink()


async def get_product_by_id(product_id: int, db: AsyncSession):
    products_stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    db_product = (await db.scalars(products_stmt)).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail='Product not found or inactive')
    return db_product


async def get_total_products(db: AsyncSession, filters) -> int:
    total_stmt = (
        select(func.count())
        .select_from(ProductModel)
        .where(*filters)
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
    order_func = asc if order == SortOrder.ASC else desc
    return order_func(sort_mapping[sort_by])


async def get_filters(db: AsyncSession, category_id, min_price,
                      max_price, in_stock, seller_id) -> list:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price",
        )

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


async def get_search_filters_and_rank(search, filters):
    rank_col = None
    if search is not None:
        search = search.strip().lower()
        if search:
            ts_query_en = func.websearch_to_tsquery('english', search)
            ts_query_ru = func.websearch_to_tsquery('russian', search)
            ts_query_any = or_(
                ProductModel.tsv.op('@@')(ts_query_en),
                ProductModel.tsv.op('@@')(ts_query_ru)
            )
            filters.append(ProductModel.tsv.op('@@')(ts_query_any))
            rank_col = func.greatest(
                func.ts_rank_cd(ProductModel.tsv, ts_query_en),
                func.ts_rank_cd(ProductModel.tsv, ts_query_ru)
                ).label('rank')

    return filters, rank_col


async def get_products_from_db(db: AsyncSession, page: int, page_size: int,
                               search: str | None, filters_sequence: tuple,
                               sort_by: ProductSortField,
                               order: SortOrder):
    """get filtered and sorted products on the chosen page"""
    db_filters = await get_filters(db, *filters_sequence)
    db_filters, search_rank = await get_search_filters_and_rank(search, db_filters)

    total = await get_total_products(db, db_filters)
    sort_by = get_sort(sort_by, order)

    products_stmt = (
        select(ProductModel if search_rank is None else ProductModel, search_rank)
        .join(CategoryModel)
        .where(and_(*db_filters))
        .order_by(sort_by if search_rank is None else desc(search_rank), sort_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if search_rank is None:
        db_products = (await db.scalars(products_stmt)).all()
    else:
        db_products = (await db.execute(products_stmt)).all()
        db_products = [prod_rank[0] for prod_rank in db_products]

    return {
        "items": db_products,
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def create_and_get_product(product: ProductCreate,
                                 image: UploadFile | None,
                                 db: AsyncSession,
                                 current_seller: UserModel):
    image_url = await save_product_image(image) if image else None
    db_product = ProductModel(
        **product.model_dump(),
        image_url=image_url,
        seller_id=current_seller.id
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def update_and_get_product(db_product,
                                 product: ProductCreate,
                                 image: UploadFile | None,
                                 db: AsyncSession):
    await db.execute(update(ProductModel)
               .where(ProductModel.id == db_product.id)
               .values(**product.model_dump())
               )
    if image:
        remove_product_image(db_product.image_url)
        db_product.image_url = await save_product_image(image)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def check_product_seller(product, current_seller: UserModel):
    """does current seller own product"""
    if product.seller_id != current_seller.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only update your own products")


async def delete_and_get_product(db_product, db: AsyncSession):
    remove_product_image(db_product.image_url)
    await db.execute(update(ProductModel)
               .where(ProductModel.id == db_product.id,
                      ProductModel.is_active == True)
               .values(is_active=False,
                       image_url=None)
               )

    await db.commit()
    await db.refresh(db_product)
    return db_product



