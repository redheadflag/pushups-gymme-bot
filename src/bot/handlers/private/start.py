from datetime import datetime
import logging
from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.throttling import rate_limit
from core.config import settings
from core.utils import send_daily_report


logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message, session: AsyncSession):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"  # type: ignore
        f"Это официальный бот для сообщества {hlink("В погоне за пампом", settings.RULES_URL)}!\n"
        "Напиши любое сообщение, чтобы получить отчет за сегодня"
    )


@router.message()
@rate_limit(limit=5)
async def echo(message: Message, session: AsyncSession, bot: Bot):
    await send_daily_report(
        session=session,
        bot=bot,
        chat_id=message.chat.id,
        dt=datetime.now().astimezone(settings.tzinfo).date()
    )
