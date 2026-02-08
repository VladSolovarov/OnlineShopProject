from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.db_depends import get_db

from app.models.categories import Category as CategoryModel
from app.schemas import CategoryCreate, Category as CategorySchema

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)

@router.get('/', response_model=list[CategorySchema], status_code=200)
async def get_all_categories(db: Session = Depends(get_db)):
    """Returns a list of all categories"""
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    return db.scalars(stmt).all()


@router.post('/', response_model=CategorySchema, status_code=201)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create category"""
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                           CategoryModel.is_active == True)
        parent = db.scalars(stmt).first()
        if parent is None:
            raise HTTPException(status_code=400,
                                detail='Parent category not found')
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put('/{category_id}', response_model=CategorySchema, status_code=200)
async def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """Update category by id"""
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.is_active == True)
    db_category = db.scalars(stmt).first()
    if db_category is None:
        raise HTTPException(status_code=404,
                            detail="Category not found")
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                                  CategoryModel.is_active == True)
        parent = db.scalars(parent_stmt).first()
        if parent is None:
            raise HTTPException(status_code=400,
                                detail="Parent category not found")
    db.execute(update(CategoryModel)
           .where(CategoryModel.id == category_id)
           .values(**category.model_dump()))
    db.refresh(db_category)
    return db_category


@router.delete('/{category_id}', status_code=200)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Set is_active=False of Category by id"""
    stmt = select(CategoryModel).where(CategoryModel.id == category_id,
                                       CategoryModel.id == True)
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=404,
                            detail='Category not found')

    db.execute(update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False))
    db.commit()

    return {"status": "success", "message": "Category marked as inactive"}