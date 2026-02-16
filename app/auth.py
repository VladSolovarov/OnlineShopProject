from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.util import deprecated
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.config import get_secret_key, ALGORITHM


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    """Transform password to hash"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check saved and input password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """Create JWT token with Payload (sub, role, id, exp)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_async_db)):
    """Check token and return user from db"""
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