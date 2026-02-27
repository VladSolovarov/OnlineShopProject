import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_password, hash_password
from app.config import get_secret_key, ALGORITHM
from app.models import User as UserModel
from app.schemas import UserCreate


credentials_exception = HTTPException(status_code=401,
                                            detail="Could not validate refresh token",
                                            headers={"WWW-Authenticate": "Bearer"})


async def check_new_email(email, db: AsyncSession):
    user_stmt = select(UserModel).where(UserModel.email == email)
    db_user = (await db.scalars(user_stmt)).first()
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email is already registered")


async def get_user_by_id(user_id, db: AsyncSession):
    user_stmt = select(UserModel).where(UserModel.id == user_id,
                                        UserModel.is_active == True)
    db_user = (await db.scalars(user_stmt)).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found or inactive")
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


async def update_role_by_email_and_get_user(email: str, new_role: str, db: AsyncSession):
    db_user = await get_user_by_email(email, db)
    await db.execute(update(UserModel)
                     .where(UserModel.email == email)
                     .values(role=new_role)
                     )
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_role_by_id_and_get_user(user_id: int, new_role: str, db: AsyncSession):
    db_user = await get_user_by_id(user_id, db)
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
