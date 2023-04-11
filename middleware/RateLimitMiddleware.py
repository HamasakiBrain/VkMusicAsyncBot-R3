import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from datetime import datetime

def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different functions.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator

class RateLimitMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=3):
        self.rate_limit = limit
        super(RateLimitMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = f"ratelimit_{getattr(handler, 'throttling_key', f'ratelimit_{handler.__name__}')}"
        else:
            limit = self.rate_limit
            key = f"ratelimit_message"

        data = await dispatcher.storage.get_data(user=message.from_user.id)
        if not data or key not in data:
            await dispatcher.storage.set_data(user=message.from_user.id, data={ key: datetime.utcnow().timestamp() })
        else:
            if (datetime.utcnow().timestamp() - data[key]) > getattr(handler, "throttling_rate_limit", self.rate_limit):
                await dispatcher.storage.update_data(user=message.from_user.id, data={ key: datetime.utcnow().timestamp() })
            else: raise CancelHandler()