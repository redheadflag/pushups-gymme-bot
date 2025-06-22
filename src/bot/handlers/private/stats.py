from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.throttling import rate_limit
from core.strings import get_user_stats
from db.commands import user_repository
from exceptions import NotFoundError
from keyboards import STATS_BUTTON_TEXT


router = Router()


@router.message(F.text == STATS_BUTTON_TEXT)
@rate_limit(limit=1)
async def user_stats_handler(message: Message, session: AsyncSession) -> None:
    user = await user_repository.get(session, message.from_user.id)  # type: ignore
    if not user:
        raise NotFoundError("User with id %i not found" % message.from_user.id)
    
    await session.refresh(user, attribute_names=["pushup_entries", "points_transactions"])
    text = get_user_stats(user=user)
    await message.answer(text)
