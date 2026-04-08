from typing import Annotated

from _decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.products import Product


class CartItemBase(BaseModel):
    product_id: Annotated[int, Field(
        description='Product ID'
    )]

    quantity: Annotated[int, Field(
        ge=1,
        description="Product quantity"
    )]


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Annotated[int, Field(
        ge=1,
        description="New quantity"
    )]


class CartItem(BaseModel):
    id: Annotated[int, Field(
        description='Cart ID'
    )]

    quantity: Annotated[int, Field(
        ge=1,
        description="Quantity of the product"
    )]

    product: Annotated[Product, Field(
        description='Product INFO'
    )]

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    user_id: Annotated[int, Field(
        description="Cart owner user ID"
    )]

    items: Annotated[list[CartItem], Field(
        default_factory=list,
        description="List of items in the cart"
    )]

    total_quantity: Annotated[int, Field(
        ge=0,
        description="Total items quantity in the cart"
    )]

    total_price: Annotated[Decimal, Field(
        ge=0,
        description="Total items price in the cart"
    )]
