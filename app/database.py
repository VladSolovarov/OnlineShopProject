from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import SettingsConfigDict

from app.config import ConfigBase


class DatabaseConfig(ConfigBase):
    URL: SecretStr
    model_config = SettingsConfigDict(env_prefix='DATABASE_')


#Async connection to PostgreSQL
db_cfg = DatabaseConfig()
DATABASE_URL = db_cfg.URL.get_secret_value()

async_engine = create_async_engine(DATABASE_URL,
                                   echo=True)

async_session_maker = async_sessionmaker(async_engine,
                                         expire_on_commit=False,
                                         class_=AsyncSession)


class Base(DeclarativeBase):
    pass