from typing import Annotated

from _decimal import Decimal

from fastapi import Form
from pydantic import BaseModel, Field, ConfigDict


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

    stock: Annotated[int, Field(
        ge=0,
        description="Product count in stock"
    )]

    category_id: Annotated[int, Field(
        description="Category ID of product"
    )]

    @classmethod
    def as_form(
            cls,
            name: Annotated[str, Form(...)],
            price: Annotated[Decimal, Form(...)],
            stock: Annotated[int, Form(...)],
            category_id: Annotated[int, Form(...)],
            description: Annotated[str | None, Form()] = None,
    ) -> "ProductCreate":
        return cls(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )


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
        description="Is the active status of product"
    )]

    rating: Annotated[Decimal, Field(
        default=Decimal('0.00'),
        ge=0,
        le=5,
        decimal_places=2,
        description="Product rating from reviews"
    )]

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """Pagination list for products"""
    items: Annotated[list[Product], Field(
        description="Products for current page"
    )]

    total: Annotated[int, Field(
        ge=0,
        description="Amount of pages"
    )]

    page_size: Annotated[int, Field(
        gt=0,
        description="Amount of products per page"
    )]

    page: Annotated[int, Field(
        gt=0,
        description="Current page number"
    )]

    model_config = ConfigDict(from_attributes=True)
