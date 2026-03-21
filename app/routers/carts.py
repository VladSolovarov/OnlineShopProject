from fastapi import APIRouter, Depends, Response

from decimal import Decimal

from app.models import (
    CartItem as CartItemModel,
    User as UserModel
)
from app.schemas import (
    Cart as CartSchema, CartItem as CartItemSchema,
    CartItemCreate, CartItemUpdate
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.auth import get_current_user
from app.routers.operations.carts_operations import (
    get_items_from_user_cart, get_user_cart, create_or_update_cart,
    update_and_get_cart_item_by_product_id, delete_cart_item,
    clear_all_items_from_user_cart
)

router = APIRouter(
    prefix='/cart',
    tags=['cart']
)


@router.get('/', response_model=CartSchema)
async def get_cart(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    cart_schema = await get_user_cart(current_user, db)
    return cart_schema


@router.post('/items', response_model=CartItemSchema, status_code=201)
async def add_item_to_cart(
        payload: CartItemCreate,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    updated_item = await create_or_update_cart(payload, current_user, db)
    return updated_item


@router.put('/items/{product_id}', response_model=CartItemSchema)
async def update_cart_item(
        product_id: int,
        payload: CartItemUpdate,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    updated_item = await update_and_get_cart_item_by_product_id(
        product_id, payload, current_user, db
    )
    return updated_item


@router.delete('/items/{product_id}', status_code=204)
async def remove_item_from_cart(
        product_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    await delete_cart_item(product_id, current_user, db)
    return Response(status_code=204)


@router.delete('/', status_code=204)
async def clear_cart(
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    await clear_all_items_from_user_cart(current_user, db)
    return Response(status_code=204)