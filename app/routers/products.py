from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select, update


from app.schemas import Product as ProductSchema, ProductCreate
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.db_depends import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model = list[ProductSchema], status_code=200)
async def get_all_products(db: Session = Depends(get_db)):
    """Get a list of all products"""
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    return db.scalars(stmt).all()


@router.post("/", response_model=ProductSchema, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                       CategoryModel.is_active == True)
    if db.scalars(stmt).first() is None:
        raise HTTPException(status_code=400,
                            detail="Category not found or inactive")
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=200)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """Get all products from category by category_id"""
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                      CategoryModel.is_active == True)
    if db.scalars(category_stmt).first() is None:
        raise HTTPException(status_code=404,
                            detail='Category not found or inactive')
    product_stmt = select(ProductModel).where(ProductModel.category_id == category_id,
                                              ProductModel.is_active == True)
    return db.scalars(product_stmt).all()


@router.get("/{product_id}", response_model=ProductSchema, status_code=200)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get details of product by id"""
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    db_product = db.scalars(stmt).first()
    if db_product is None:
        HTTPException(status_code=404,
                      detail='Product not found or inactive')
    category_stmt = select(CategoryModel).where(CategoryModel.id == db_product.category_id,
                                                CategoryModel.is_active == True)
    category = db.scalars(category_stmt).first()
    if category is None:
        raise HTTPException(status_code=400,
                            detail="Category not found or inactive")
    return db_product


@router.put("/{product_id}", response_model=ProductSchema, status_code=200)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """Update product by id"""
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                              ProductModel.is_active == True)
    db_product = db.scalars(stmt).first()
    if db_product is None:
        raise HTTPException(status_code=404,
                            detail="Product not found or inactive")
    category_stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                                CategoryModel.is_active == True)
    if db.scalars(category_stmt).first() is None:
        raise HTTPException(status_code=400,
                            detail="Category not found or inactive")

    db.execute(update(ProductModel)
               .where(ProductModel.id == product_id)
               .values(**product.model_dump())
               )
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=200)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Set is_active=False of Product by id"""
    stmt = select(ProductModel).where(ProductModel.id == product_id,
                                      ProductModel.is_active == True)
    if db.scalars(stmt).first() is None:
        raise HTTPException(status_code=404,
                            detail="Product not found or already inactive")
    db.execute(update(ProductModel)
               .where(ProductModel.id == product_id)
               .values(is_active=False)
               )
    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}

