from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db_depends import get_async_db

from app.models import (
    Order as OrderModel, OrderItem as OrderItemModel,
    User as UserModel
)
from app.routers.operations.carts_operations import get_items_from_user_cart
from app.routers.operations.orders_operations import (
    load_order_with_items,
    add_items_to_order,
    create_and_get_order_list,
    get_order_by_id
)
from app.schemas import Order as OrderSchema, OrderList


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post('/checkout', response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def checkout_order(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    items = await get_items_from_user_cart(current_user, db)
    created_order = await add_items_to_order(items, current_user, db)
    return created_order


@router.get('/', response_model=OrderList)
async def list_orders(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=10, ge=1, le=100),
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    return await create_and_get_order_list(page, page_size, current_user, db)


@router.get('/{order_id}', response_model=OrderSchema)
async def get_order(
        order_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    return await get_order_by_id(order_id, current_user, db)