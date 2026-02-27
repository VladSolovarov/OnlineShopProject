from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin, create_refresh_token, create_access_token
from app.routers.operations.users_operations import check_new_email, get_user_by_id, \
    authenticate_user, create_and_get_user, update_role_by_id_and_get_user, get_id_by_refresh_token
from app.models import User as UserModel
from app.schemas import UserCreate, User as UserSchema, UserRoleUpdate, RefreshTokenRequest
from app.db_depends import get_async_db

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    await check_new_email(user.email, db)
    db_user = await create_and_get_user(user, db)
    return db_user


@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    db_user = await authenticate_user(form_data, db)
    access_token, refresh_token = create_access_token(db_user), create_refresh_token(db_user)

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.post('/access_token')
async def access_token_by_refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    """Generate new access token by refresh-token"""
    user_id = get_id_by_refresh_token(body.refresh_token)
    db_user = await get_user_by_id(user_id, db)
    access_token = create_access_token(db_user)

    return {"access_token": access_token,
            "token_type": "bearer"}


@router.post('/refresh_token')
async def tokens_by_refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    """Generate new access and refresh tokens by refresh-token"""
    user_id = get_id_by_refresh_token(body.refresh_token)
    db_user = await get_user_by_id(user_id, db)
    access_token, refresh_token = create_access_token(db_user), create_refresh_token(db_user)

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.get('/{user_id}', response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    db_user = await get_user_by_id(user_id, db)
    return db_user


@router.put('/{user_id}/update_role', response_model=UserSchema)
async def update_role(user_id: int,
                      update: UserRoleUpdate,
                      db: AsyncSession = Depends(get_async_db),
                      current_admin: UserModel = Depends(get_current_admin)):
    db_user = await update_role_by_id_and_get_user(user_id, update.new_role, db)
    return db_user
