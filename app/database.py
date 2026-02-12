from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )

class DatabaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='DATABASE_')

    URL: SecretStr


DATABASE_URL = "sqlite:///ecommerce.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
#Async connection to PostgreSQL
DATABASE_URL = DatabaseConfig.URL.get_secret_value()

async_engine = create_async_engine(DATABASE_URL,
                                   echo=True)

async_session_maker = async_sessionmaker(async_engine,
                                         expire_on_commit=False,
                                         class_=AsyncSession)


class Base(DeclarativeBase):
    pass