from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.user_context import UserContext
from db.models import User


class NewUserFilter(Filter):
    def __init__(self, is_new: bool = True) -> None:
        self.is_new = is_new
    
    async def __call__(self, message: Message, session: AsyncSession, user_context: UserContext) -> bool:
        if not message.from_user:
            return False

        return user_context.is_new == self.is_new
