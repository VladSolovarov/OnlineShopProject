import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update

from app.auth import hash_password, verify_password, create_access_token, create_refresh_token
from app.config import get_secret_key, ALGORITHM
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import (CategoryCreate,
                         Category as CategorySchema,
                         Product as ProductSchema, ProductCreate, UserCreate, UserRoleUpdate)

from sqlalchemy.ext.asyncio import AsyncSession


credentials_exception = HTTPException(status_code=401,
                                            detail="Could not validate refresh token",
                                            headers={"WWW-Authenticate": "Bearer"})
#PRODUCT OPERATIONS
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


#CATEGORY OPERATIONS
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


#USER OPERATIONS
async def check_new_email(email, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.email == email)
    result = (await db.scalars(stmt)).first()
    if result is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email is already registered")

async def get_user_by_id(user_id, db: AsyncSession):
    user_stmt = select(UserModel).where(UserModel.id == user_id,
                                        UserModel.is_active == True)
    db_user = (await db.scalars(user_stmt)).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return db_user



async def get_user_by_email(email, db: AsyncSession):
    user_stmt = select(UserModel).where(UserModel.email == email,
                                        UserModel.is_active == True)
    db_user = (await db.scalars(user_stmt)).first()

    if db_user is None:
        raise credentials_exception

    return db_user


async def authenticate_user(form_data: OAuth2PasswordRequestForm,
                            db: AsyncSession):
    user_stmt = select(UserModel).where(UserModel.email == form_data.username,
                                        UserModel.is_active == True)
    db_user = (await db.scalars(user_stmt)).first()
    if db_user is None or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return db_user


async def create_and_get_user(user: UserCreate, db: AsyncSession):
    db_user = UserModel(email=user.email,
                        hashed_password=hash_password(user.password.get_secret_value()),
                        role=user.role)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_role_by_email(email: str, new_role: str, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.email == email,
                                   UserModel.is_active == True)
    db_user = (await db.scalars(stmt)).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email not found")
    await db.execute(update(UserModel)
                     .where(UserModel.email == email)
                     .values(role=new_role)
                     )
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_role_by_id(user_id: int, new_role: str, db: AsyncSession):
    stmt = select(UserModel).where(UserModel.id == user_id,
                                   UserModel.is_active == True)
    db_user = (await db.scalars(stmt)).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User ID not found")
    await db.execute(update(UserModel)
                     .where(UserModel.id == user_id)
                     .values(role=new_role)
                     )
    await db.commit()
    await db.refresh(db_user)
    return db_user


def get_id_by_refresh_token(refresh_token) -> int:
    """Check refresh token and return user_id"""
    try:
        payload = jwt.decode(refresh_token, get_secret_key(), algorithms=[ALGORITHM])
        user_id: str | None = payload.get("id")
        token_type: str | None = payload.get("token_type")
        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception # Time expired
    except jwt.PyJWTError:
        raise credentials_exception # Something wrong with the token
    return int(user_id)