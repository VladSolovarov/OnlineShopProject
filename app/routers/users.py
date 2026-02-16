from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.db_operations import check_email, create_and_get_user, authenticate_user
from app.schemas import UserCreate, User as UserSchema
from app.db_depends import get_async_db

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession=Depends(get_async_db)):
    await check_email(user, db)
    db_user = await create_and_get_user(user, db)
    return db_user


@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    access_token = await authenticate_user(form_data, db)
    return {"access_token": access_token,
            "token_type": "bearer"}