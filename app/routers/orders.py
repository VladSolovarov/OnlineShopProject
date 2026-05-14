from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db_depends import get_async_db

from app.models import (
    User as UserModel
)
from app.services.carts import get_items_from_user_cart
from app.services import (
    add_items_to_order,
    create_and_get_order_list,
    get_order_by_id,
    get_order_payment_info
)
from app.schemas import Order as OrderSchema, OrderList, OrderCheckoutResponse

router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post('/checkout', response_model=OrderCheckoutResponse, status_code=status.HTTP_201_CREATED)
async def checkout_order(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    items = await get_items_from_user_cart(current_user, db)
    order_response = await add_items_to_order(items, current_user, db)
    return order_response


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


@router.get('/{order_id}/status')
async def get_order_status(
        order_id: int,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
) -> dict:
    return await get_order_payment_info(order_id, current_user, db)