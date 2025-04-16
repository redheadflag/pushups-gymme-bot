from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


class IsNewUser(Filter):
    def __init__(self, is_new: bool = True) -> None:
        self.is_new = is_new
    
    async def __call__(self, message: Message, session: AsyncSession, is_new: bool) -> bool:
        if not message.from_user:
            return False
        
        return self.is_new == is_new
