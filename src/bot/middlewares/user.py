from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

from db.commands import add_or_update_user, user_repository
from db.models import User


class UserMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any:
        data["user"] = None
        data["is_new"] = None
        if not message.from_user:
            return await handler(message, data)
        session = data["session"]
        user_id = message.from_user.id
        user = await user_repository.get(session, pk=user_id)

        is_existing = isinstance(user, User)
        data["is_new"] = not(is_existing)

        user = await add_or_update_user(
            session=session,
            data={
                "id": message.from_user.id,
                "username": message.from_user.username,
                "full_name": message.from_user.full_name
            }
        )
        data["user"] = user
        return await handler(message, data)
