from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.user_context import UserContext


class AdminFilter(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, user_context: UserContext, session: AsyncSession, **kwargs) -> bool:
        user = await user_context.get_user(session)
        return user.is_admin
