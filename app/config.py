from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


class SecretKeyConfig(ConfigBase):
    KEY: SecretStr
    model_config = SettingsConfigDict(env_prefix="SECRET_")


class YookassaConfig(ConfigBase):
    SECRET_KEY: SecretStr
    SHOP_ID: str
    RETURN_URL: str = "http://localhost:8000/"
    model_config = SettingsConfigDict(env_prefix="YOOKASSA_")


key_cfg = SecretKeyConfig()
yookassa_cfg = YookassaConfig()
ALGORITHM = "HS256"


def get_secret_key() -> str:
    return key_cfg.KEY.get_secret_value()


def get_yookassa_key() -> str:
    return yookassa_cfg.SECRET_KEY.get_secret_value()


