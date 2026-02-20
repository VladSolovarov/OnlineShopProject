from fastapi import HTTPException

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin
from app.routers.db_operations import check_email, create_and_get_user, authenticate_user, update_role_by_email, \
    update_role_by_id
from app.models import User as UserModel
from app.schemas import UserCreate, User as UserSchema, UserRoleUpdate
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


@router.put('{user_id}/update_role', response_model=UserSchema)
async def update_role(user_id: int,
                      update: UserRoleUpdate,
                      db: AsyncSession = Depends(get_async_db),
                      current_admin: UserModel = Depends(get_current_admin)):
    db_user = await update_role_by_id(user_id, update.new_role, db)
    return db_user