from fastapi import HTTPException
from sqlalchemy import select, delete

from decimal import Decimal

from sqlalchemy.orm import selectinload

from app.models import CartItem as CartItemModel, User as UserModel
from app.schemas import (
    Cart as CartSchema, CartItemCreate, CartItemUpdate
)
from app.services.products import get_product_by_id
from sqlalchemy.ext.asyncio import AsyncSession


async def get_cart_item(user_id: int, product_id: int, db: AsyncSession):
    cart_stmt = (
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(CartItemModel.user_id == user_id,
               CartItemModel.product_id == product_id)
    )
    cart_db = (await db.scalars(cart_stmt)).first()
    return cart_db


async def get_items_from_user_cart(user: UserModel, db: AsyncSession):
    cart_stmt = (
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(CartItemModel.user_id == user.id)
        .order_by(CartItemModel.id)
    )
    cart_items = (await db.scalars(cart_stmt)).all()
    if not cart_items:
        raise HTTPException(status_code=400,
                            detail='Cart is empty')
    return cart_items


async def get_user_cart(user: UserModel, db: AsyncSession):
    items = await get_items_from_user_cart(user, db)
    total_quantity, total_price_decimal = 0, Decimal('0.00')
    for item in items:
        total_quantity += item.quantity
        total_price_decimal += item.quantity * item.product.price
    return CartSchema(
        user_id=user.id,
        items=items,
        total_quantity=total_quantity,
        total_price=total_price_decimal
    )


async def create_or_update_cart(
        payload: CartItemCreate,
        user: UserModel,
        db: AsyncSession
):
    await get_product_by_id(payload.product_id, db)
    cart_item = await get_cart_item(user.id, payload.product_id, db)
    if cart_item is not None:
        cart_item.quantity += payload.quantity
    else:
        cart_item = CartItemModel(
            user_id=user.id,
            product_id=payload.product_id,
            quantity=payload.quantity
        )
        db.add(cart_item)
    await db.commit()
    updated_item = await get_cart_item(user.id, payload.product_id, db)
    return updated_item


async def update_and_get_cart_item_by_product_id(
        product_id: int,
        payload: CartItemUpdate,
        user: UserModel,
        db: AsyncSession
):
    await get_product_by_id(product_id, db)
    cart_item = await get_cart_item(user.id, product_id, db)
    if cart_item is None:
        raise HTTPException(status_code=404,
                            detail="Cart item not found")
    cart_item.quantity += payload.quantity
    await db.commit()
    updated_item = await get_cart_item(user.id, product_id, db)
    return updated_item


async def delete_cart_item(
        product_id: int,
        user: UserModel,
        db: AsyncSession
):
    cart_item = await get_cart_item(user.id, product_id, db)
    if cart_item is None:
        raise HTTPException(status_code=404,
                            detail="Cart item not found")
    await db.delete(cart_item)
    await db.commit()


async def clear_all_items_from_user_cart(
        user: UserModel,
        db: AsyncSession
):
    await db.execute(delete(CartItemModel)
                     .where(CartItemModel.user_id == user.id)
    )
    await db.commit()



