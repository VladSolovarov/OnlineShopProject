from decimal import Decimal
from typing import Any
from uuid import uuid4

from anyio import to_thread
from yookassa import Configuration, Payment

from app.config import yookassa_cfg, get_yookassa_key


async def get_yookassa_payment(
        *,
        order_id: int,
        amount: Decimal,
        user_email: str,
        description: str,
) -> dict[str, Any]:
    Configuration.account_id = yookassa_cfg.SHOP_ID
    Configuration.secret_key = get_yookassa_key()

    payload = {
        'amount': {
            'value': f'{amount:.2f}', # str(Decimal) - обязательно строка ('100.00')
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': yookassa_cfg.RETURN_URL
        },
        'capture': True, # Авто-списаниеи денег после авторизации
        'description': description,
        'metadata': {
            'order_id': order_id # связь с заказом из БД
        },
        'receipt': { # ФИСКальный ЧЕК (обязателен по 54-ФЗ для РФ!)
            'customer': {
                'user_email': user_email
            },
            'items': [ # здесь 1 item - весь заказ
                {
                    'description': description[:128], #max length 128
                    'quantity': '1.00',
                    'amount': {
                        'value': f'{amount:.2f}',
                        'currency': 'RUB'
                    },
                    'vat_code': 1, # НДС: 1=без НДС (0%), 2=0%, 3=10%, 4=20%, 5=расчетный, 6=спецрежим
                    'payment_mode': 'full_prepayment',
                    'payment_subject': 'commodity' #Тип: "service"=услуга, "commodity"=товар или заказ
                }
            ]
        }
    }

    def _request() -> Payment:
        return Payment.create(payload, str(uuid4())) # POST запрос к API YOOKASSA

    # Вызов в thread (библиотека YooKassa синхронная, а FastAPI ассинхронный)
    payment: Payment = await to_thread.run_sync(_request)
    # URL для оплаты
    confirmation_url = getattr(payment.confirmation, 'confirmation_url', None)
    return {
        'id': payment.id, # ID платежа, полученного от YooKassa
        'status': payment.status,
        'confirmation_url': confirmation_url # сюда перенаправит пользователя для оплаты
    }