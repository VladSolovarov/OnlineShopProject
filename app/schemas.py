from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, EmailStr, SecretStr


class CategoryCreate(BaseModel):
    """Uses to create and update categories. (PUT, POST)"""
    name: Annotated[str, Field(
        min_length=2,
        max_length=50,
        description="Category name (2-50 symbols)"
    )]

    parent_id: Annotated[int | None, Field(
        default=None,
        description="Parent category ID"
    )]


class Category(BaseModel):
    """Get category data. (GET)"""
    id: Annotated[int, Field(
        description="Unique category ID"
    )]

    name: Annotated[str, Field(
        description="Category name"
    )]

    parent_id: Annotated[int | None, Field(
        default=None,
        description="Parent category ID"
    )]

    is_active: Annotated[bool, Field(
        description="Is active category"
    )]

    model_config=ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """Uses to create and update products. (POST, PUT)"""
    name: Annotated[str, Field(
        min_length=3,
        max_length=100,
        description="Product name (3-100 symbols)"
    )]

    description: Annotated[str | None, Field(
        default=None,
        max_length=500,
        description="Product description (up to 500 symbols)"
    )]

    price: Annotated[Decimal, Field(
        gt=0,
        decimal_places=2,
        description="Product price (greater than 0)"
    )]

    image_url: Annotated[str | None, Field(
        default=None,
        max_length=200,
        description="Product image url"
    )]

    stock: Annotated[int, Field(
        ge=0,
        description="Product count in stock"
    )]

    category_id: Annotated[int, Field(
        description="Category ID of product"
    )]


class Product(BaseModel):
    """Get product data. (GET)"""
    id: Annotated[int, Field(
        description="Unique product ID"
    )]

    name: Annotated[str, Field(
        description="Product name"
    )]

    description: Annotated[str | None, Field(
        default=None,
        description="Product description"
    )]

    price: Annotated[Decimal, Field(
        gt=0,
        decimal_places=2,
        description="Product price (greater than 0)"
    )]

    image_url: Annotated[str | None, Field(
        default=None,
        description="Product image url"
    )]

    stock: Annotated[int, Field(
        description="Product count in stock"
    )]

    category_id: Annotated[int, Field(
        description="Category ID of product"
    )]

    is_active: Annotated[bool, Field(
        description="Is active product"
    )]

    model_config = ConfigDict(from_attributes=True)


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
        description="Is user active"
    )]
    role: Annotated[str, Field(
        description="What role does user have"
    )]

    model_config = ConfigDict(from_attributes=True)