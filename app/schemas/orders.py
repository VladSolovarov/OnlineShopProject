from datetime import datetime
from typing import Annotated

from _decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.products import Product


class OrderItem(BaseModel):
    id: Annotated[int, Field(
        description="Order item id"
    )]

    product_id: Annotated[int, Field(
        description="Product ID"
    )]

    quantity: Annotated[int, Field(
        gt=0,
        description="Product quantity"
    )]

    unit_price: Annotated[Decimal, Field(
        ge=0,
        description="Product price at the time of purchase"
    )]

    total_price: Annotated[Decimal, Field(
        ge=0,
        description="Price of the items (all current products)"
    )]

    product: Annotated[Product | None, Field(
        default=None,
        description="Product INFO"
    )]

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: Annotated[int, Field(
        description="Order ID"
    )]

    user_id: Annotated[int, Field(
        description="User ID"
    )]

    status: Annotated[str, Field(
        description="Current order status"
    )]

    total_amount: Annotated[Decimal, Field(
        ge=0,
        description="Total order price"
    )]

    created_at: Annotated[datetime, Field(
        description="When the order was created datetime"
    )]

    updated_at: Annotated[datetime, Field(
        description="Last update datetime"
    )]

    items: Annotated[list[OrderItem], Field(
        default_factory=list,
        description="List of order items"
    )]

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    items: Annotated[list[Order], Field(
        default_factory=list,
        description="Items list on current page"
    )]

    total: Annotated[int, Field(
        description="Amount of orders"
    )]

    page: Annotated[int, Field(
        gt=0,
        description="Current page"
    )]

    page_size: Annotated[int, Field(
        gt=0,
        description="Page size"
    )]

    model_config = ConfigDict(from_attributes=True)


class OrderCheckoutResponse(BaseModel):
    order: Annotated[Order, Field(
        description='Created order'
    )]

    confirmation_url: Annotated[str | None, Field(
        default=None,
        description='URL to pay the order in YooKassa'
    )]
