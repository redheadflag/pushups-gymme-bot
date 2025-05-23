from datetime import datetime, timedelta
import logging
from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.throttling import rate_limit
from core.config import settings
from core.utils import send_daily_report


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
    await send_daily_report(
        session=session,
        bot=bot,
        chat_id=message.chat.id,
        dt=datetime.now().astimezone(settings.tzinfo).date()
    )
