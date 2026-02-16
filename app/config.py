import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


class SecretKeyConfig(ConfigBase):
    KEY: SecretStr
    model_config = SettingsConfigDict(env_prefix="SECRET_")


key_cfg = SecretKeyConfig()
ALGORITHM = "HS256"


def get_secret_key() -> str:
    return key_cfg.KEY.get_secret_value()



