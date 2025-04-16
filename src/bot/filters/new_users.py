from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from db.commands import add_or_update_user, user_repository
from db.models import User


class IsNewUser(Filter):
    def __init__(self, is_new: bool = True) -> None:
        self.is_new = is_new
    
    async def __call__(self, message: Message, session: AsyncSession) -> bool | dict[str, User]:
        if not message.from_user:
            return False
        
        user_id = message.from_user.id
        user = await user_repository.get(session, pk=user_id)

        is_existing = isinstance(user, User)
        if self.is_new == is_existing:
            return False
  
        user = await add_or_update_user(
            session=session,
            data={
                "id": message.from_user.id,
                "username": message.from_user.username,
                "full_name": message.from_user.full_name
            }
        )

        return {"user": user}
