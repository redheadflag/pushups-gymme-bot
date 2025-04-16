from aiogram.filters import BaseFilter
from aiogram.types import Message

from db.models import User


class AdminFilter(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, user: User) -> bool:
        return user.is_admin
