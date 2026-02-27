from fastapi import APIRouter, Depends

from app.auth import get_current_seller
from app.schemas import Product as ProductSchema, ProductCreate
from app.models.users import User as UserModel

from app.routers.operations.products_operations import get_products_from_db, get_product_by_id, create_and_get_product, \
    update_and_get_product, check_product_seller, delete_and_get_product
from app.routers.operations.categories_operations import check_category_by_id

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model = list[ProductSchema], status_code=200)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """Get a list of all products"""
    return await get_products_from_db(db)


@router.post("/", response_model=ProductSchema, status_code=201)
async def create_product(product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_seller: UserModel = Depends(get_current_seller)):
    """Create a new product for current 'seller'"""
    await check_category_by_id(product.category_id, db)
    return await create_and_get_product(product, db, current_seller)


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=200)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get all products from category by category_id"""
    await check_category_by_id(category_id, db)
    products = await get_products_from_db(db, category_id)
    return products


@router.get("/{product_id}", response_model=ProductSchema, status_code=200)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get details of product by id"""
    db_product = await get_product_by_id(product_id, db)
    await check_category_by_id(db_product.category_id, db)
    return db_product


@router.put("/{product_id}", response_model=ProductSchema, status_code=200)
async def update_product(product_id: int,
                         product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_seller: UserModel = Depends(get_current_seller)):
    """Update product by id for current seller"""
    db_product = await get_product_by_id(product_id, db)
    await check_category_by_id(db_product.category_id, db)
    await check_product_seller(db_product, current_seller)
    return await update_and_get_product(db_product, product, db)


@router.delete("/{product_id}", status_code=200)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_seller: UserModel = Depends(get_current_seller)):
    """Set is_active=False of current seller's Product by id"""
    db_product = await get_product_by_id(product_id, db)
    await check_product_seller(db_product, current_seller)
    return await delete_and_get_product(db_product, db)

