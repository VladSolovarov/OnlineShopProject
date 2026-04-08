from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db
from app.services import (
    ip_validation,
    get_payload,
    get_payment,
    get_order_db,
    get_response_update_order
)

router = APIRouter(prefix='/payments',
                   tags=['payments'])


@router.post('/yookassa/webhook', status_code=status.HTTP_200_OK)
async def yookassa_webhook(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
):
    ip_validation(request)
    payload = await get_payload(request)
    payment = get_payment(payload)
    order_db = await get_order_db(payment, db)
    response = await get_response_update_order(payment, order_db, db)
    return response
