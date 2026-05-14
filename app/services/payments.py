import ipaddress
import json
from datetime import datetime, timezone

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from yookassa.domain.notification import WebhookNotification
from yookassa.domain.response import PaymentResponse

from app.models import Order as OrderModel

YANDEX_IP_LIST = [
    '185.71.76.0/27',
    '185.71.77.0/27',
    '77.75.153.0/25',
    '77.75.156.11',
    '77.75.156.35',
    '77.75.154.128/25',
    '2a02:5180::/32'
]


def is_ip_allowed(ip: str | None) -> bool:
    if ip is None:
        return False
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False

    for mask in YANDEX_IP_LIST:
        if '/' in mask:
            if address in ipaddress.ip_network(mask, strict=False):
                return True
        elif address == ipaddress.ip_address(mask):
            return True
    return False


def _extract_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for is not None:
        return forwarded_for.split(',')[0].strip()
    return request.client.host if request.client else None


def ip_validation(request: Request):
    client_ip = _extract_client_ip(request)
    if not is_ip_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='IP is not allowed'
        )


async def get_payload(request: Request):
    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid JSON: {exc}'
        )
    return payload


def get_payment(payload):
    try:
        notification = WebhookNotification(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid notification: {exc}'
        )
    return notification.object


async def get_order_db(
        payment: PaymentResponse,
        db: AsyncSession) -> OrderModel | None:
    order_id = payment.metadata.get('order_id') if payment.metadata else None
    if order_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Order id is missing'
        )

    order_stmt = (
        select(OrderModel)
        .where(OrderModel.id == int(order_id))
    )
    order_db = (await db.scalars(order_stmt)).first()
    return order_db


async def get_response_update_order(
        payment: PaymentResponse,
        order_db: OrderModel | None,
        db: AsyncSession
) -> dict:
    if order_db is None:
        return {'status': 'ignored'}
    if payment.status == 'succeeded':
        if not order_db.paid_at:
            order_db.status = 'paid'
            order_db.paid_at = datetime.now(timezone.utc)
            order_db.payment_id = payment.id
    elif payment.status == 'canceled':
        order_db.status = 'canceled'
    await db.commit()
    return {'status': 'ok'}
