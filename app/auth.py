from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.util import deprecated
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from app.schemas import User as UserSchema
from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.config import get_secret_key, ALGORITHM

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
ADMIN_ROLE, SELLER_ROLE, BUYER_ROLE = 'admin', 'seller', 'buyer'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    """Transform password to hash"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check saved and input password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(token_data: dict, token_type: str):
    """Create access or refresh token"""
    to_encode = token_data.copy()
    expire_timedelta = (timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                if token_type == ACCESS_TOKEN_TYPE else
                timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    issued_at = datetime.now(timezone.utc)
    to_encode.update({
        "iat": issued_at,
        "exp": issued_at + expire_timedelta,
        "token_type": token_type
    })
    return jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)


def create_access_token(user: UserSchema):
    """Create access JWT with Payload (sub, role, id, exp, token_type)"""
    data = {"sub": user.email, "role": user.role, "id": user.id}
    return create_jwt(data, token_type=ACCESS_TOKEN_TYPE)


def create_refresh_token(user: UserSchema):
    """Create refresh JWT with Payload (sub, role, id, exp, token_type)"""
    data = {"id": user.id}
    return create_jwt(data, token_type=REFRESH_TOKEN_TYPE)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_async_db)):
    """Check token and returned user from db"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise credentials_exception
    user_stmt = select(UserModel).where(UserModel.email == email,
                                        UserModel.is_active == True)
    result = await db.scalars(user_stmt)
    db_user = result.first()
    if db_user is None:
        raise credentials_exception
    return db_user


def check_role(user, chosen_role):
    if user.role != chosen_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Only {chosen_role}s can perform this action")


async def get_current_seller(current_user: UserModel = Depends(get_current_user)):
    """Validate current user role is 'seller'"""
    check_role(current_user, SELLER_ROLE)
    return current_user


async def get_current_admin(current_user: UserModel = Depends(get_current_user)):
    """Validate current user role is 'admin'"""
    check_role(current_user, ADMIN_ROLE)
    return current_user


async def get_current_buyer(current_user: UserModel = Depends(get_current_user)):
    """Validate current user role is 'buyer'"""
    check_role(current_user, BUYER_ROLE)
    return current_user