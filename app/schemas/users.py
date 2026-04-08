from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, SecretStr, ConfigDict


class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(
        max_length=100,
        description="User email"
    )]

    password: Annotated[SecretStr, Field(
        min_length=8,
        description="Password (At least 8 symbols)"
    )]

    role: Annotated[str, Field(
        default="buyer",
        pattern=r"^(buyer|seller)$",
        description="Role ('buyer' or 'seller')"
    )]


class User(BaseModel):
    id: Annotated[int, Field(
        description="Unique user ID"
    )]

    email: Annotated[EmailStr, Field(
        description="Unique user email"
    )]

    is_active: Annotated[bool, Field(
        description="Is the active status of user"
    )]

    role: Annotated[str, Field(
        description="What role does user have"
    )]

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    """Update user role"""
    new_role: Annotated[str, Field(
        pattern=r"^(seller|buyer|admin)$",
        description="New user role"
    )]

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str
