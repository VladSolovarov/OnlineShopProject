from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select, update


from app.schemas import Product as ProductSchema, ProductCreate
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel

from app.routers.db_operations import get_products_from_db, check_category, get_product_by_id, create_and_get_product, \
    update_and_get_product, delete_product_by_id

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
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new product"""
    await check_category(product.category_id, db)
    return await create_and_get_product(product, db)


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=200)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get all products from category by category_id"""
    await check_category(category_id, db)
    products = await get_products_from_db(db, category_id)
    return products


@router.get("/{product_id}", response_model=ProductSchema, status_code=200)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get details of product by id"""
    db_product = await get_product_by_id(product_id, db)
    await check_category(db_product.category_id, db)
    return db_product


@router.put("/{product_id}", response_model=ProductSchema, status_code=200)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """Update product by id"""
    db_product = await get_product_by_id(product_id, db)
    await check_category(db_product.category_id, db)
    return await update_and_get_product(product_id, product, db)


@router.delete("/{product_id}", status_code=200)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Set is_active=False of Product by id"""
    await delete_product_by_id(product_id, db)
    return {"status": "success", "message": "Product marked as inactive"}

