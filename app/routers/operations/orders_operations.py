from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order as OrderModel, OrderItem as OrderItemModel, User as UserModel, CartItem as CartItemModel
from app.schemas import OrderList


async def load_order_with_items(order_id: int, db: AsyncSession) -> OrderModel | None:
    order_stmt = (
        select(OrderModel)
        .options(
            selectinload(OrderModel.items)
            .selectinload(OrderItemModel.product),
        )
        .where(OrderModel.id == order_id)
    )
    order_db = (await db.scalars(order_stmt)).first()
    return order_db


async def add_items_to_order(cart_items: list, user: UserModel, db: AsyncSession):
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User does not have items in cart")

    order = OrderModel(user_id=user.id)
    total_amount = Decimal('0')

    for cart_item in cart_items:
        prod = cart_item.product
        if prod is None or not prod.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product ID{cart_item.product_id} is not available"
            )

        if cart_item.quantity > prod.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many items '{prod.name}' (cart: {cart_item.quantity}, stock: {prod.stock})"
            )

        if (unit_price := prod.price) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{prod.name}' has no price set"
            )

        total_price = unit_price * cart_item.quantity
        total_amount += total_price

        order.items.append(
            OrderItemModel(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                total_price=total_price
            )
        )
        prod.stock -= cart_item.quantity
    order.total_amount = total_amount
    db.add(order)
    await db.execute(
        delete(CartItemModel)
        .where(CartItemModel.user_id == user.id)
    )
    await db.commit()

    created_order = await load_order_with_items(order.id, db)

    if created_order is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to load created order")
    return created_order


async def create_and_get_order_list(
        page: int,
        page_size: int,
        current_user: UserModel,
        db: AsyncSession
) -> OrderList:
    total = await db.scalar(
        select(func.count(OrderModel.id))
        .where(OrderModel.user_id == current_user.id)
    )

    orders_stmt = (
        select(OrderModel)
        .options(selectinload(OrderModel.items).selectinload(OrderItemModel.product))
        .where(OrderModel.user_id == current_user.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    orders = (await db.scalars(orders_stmt)).all()
    return OrderList(items=orders, total=total or 0, page=page, page_size=page_size)


async def get_order_by_id(
        order_id: int,
        current_user: UserModel,
        db: AsyncSession
):
    order = await load_order_with_items(order_id, db)
    if order is None or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Order not found')
    return order