from typing import Any, Awaitable, Callable, Dict
import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.events import detect_events


logger = logging.getLogger(__name__)


class EventMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        result = await handler(event, data)

        bot = data["bot"]
        session = data["session"]
        user_context = data["user_context"]

        detected_events = await detect_events(session, user_context=user_context)

        for _event in detected_events:
            await _event.handle(bot=bot, message=event, session=session, user_context=user_context)

        return result
