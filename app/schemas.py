from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, EmailStr, SecretStr
from datetime import datetime


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


class Review(BaseModel):
    id: Annotated[int, Field(
        description="Unique review ID"
    )]

    user_id: Annotated[int, Field(
        description="User ID of review"
    )]

    product_id: Annotated[int, Field(
        description="Product ID of review"
    )]

    comment: Annotated[str | None, Field(
        max_length=1000,
        default=None,
        description="Review text",
    )]

    comment_date: Annotated[datetime, Field(
        default_factory=datetime.now,
        description="Review datetime"
    )]

    grade: Annotated[int, Field(
        ge=1,
        le=5,
        description="Review grade"
    )]

    is_active: Annotated[bool, Field(
        description="Is the active status of review"
    )]


class ReviewCreate(BaseModel):
    product_id: Annotated[int, Field(
        description="Product id of this review"
    )]

    comment: Annotated[str | None, Field(
        default=None,
        description="Review text (up to 1000 symbols)"
    )]

    grade: Annotated[int, Field(
        ge=1,
        le=5,
        description="Review grade (from 1 to 5)"
    )]


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


#CART SCHEMAS

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


