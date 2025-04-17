from datetime import datetime
import logging
from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.throttling import rate_limit
from core.config import settings
from core.strings import get_daily_report
from db.commands import get_all_users


logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message, session: AsyncSession):
    pass
    # await message.answer(f"Hi, {message.from_user.first_name}!")  # type: ignore
    # await user_repository.create(
    #     session=session,
    #     data={
    #         "id": message.from_user.id,
    #         "username": message.from_user.username,
    #         "full_name": message.from_user.full_name
    #     }
    # )


@router.message()
@rate_limit(limit=5)
async def echo(message: Message, session: AsyncSession, bot: Bot):
    users = await get_all_users(session=session)
    text = get_daily_report(users=users, dt=datetime.now().astimezone(settings.tzinfo).date())
    await message.answer(text=text)
