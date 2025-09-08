import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.commands import add_or_update_user, is_user_newbie, user_repository
from db.models import PushupEntry, User


logger = logging.getLogger(__name__)

class UserContextMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not event.from_user or event.from_user.is_bot:
            return
        session = data["session"]
        user_id = event.from_user.id
        
        user_context = UserContext(user_id=user_id)

        is_newbie = await is_user_newbie(session=session, user_id=user_id)
        user_context.is_new = not(is_newbie)

        if event.chat.id != settings.GROUP_ID or event.message_thread_id != settings.PUSHUPS_TOPIC_ID:
            return await handler(event, data)

        user = await add_or_update_user(
            session=session,
            data={
                "id": event.from_user.id,
                "username": event.from_user.username,
                "full_name": event.from_user.full_name
            }
        )

        user_context.load_user(user=user)
        data["user_context"] = user_context
        return await handler(event, data)


class UserContext:
    def __init__(self, *, user_id: int, user: User | None = None, is_new: bool | None = None, latest_pushup_entry: PushupEntry | None = None):
        self._user = user
        self._user_id = user_id
        if not any([self._user, self._user_id]):
            raise ValueError("You should provide either user instance or user_id")
        
        self._is_new = is_new
        self._latest_pushup_entry = latest_pushup_entry
    
    def load_user(self, user: User) -> None:
        if not self._user:
            self._user = user

    async def get_user(self, session: AsyncSession) -> User:
        if not self._user:
            if not self._user_id:
                raise ValueError("You should provide either user instance or user_id")
            self._user = await user_repository.get_or_raise(session, self._user_id)
        return self._user
    
    @property
    def is_new(self) -> bool | None:
        return self._is_new
    
    @is_new.setter
    def is_new(self, value: bool) -> None:
        self._is_new = value
    
    @property
    def user_id(self) -> int:
        return self._user_id

    async def get_latest_pushup_entry(self, session: AsyncSession) -> PushupEntry:
        if not self._latest_pushup_entry:
            user = await self.get_user(session)
            self._latest_pushup_entry = await user.get_latest_entry(session)
        return self._latest_pushup_entry
