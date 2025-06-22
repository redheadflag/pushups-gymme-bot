from datetime import datetime

from aiogram import F, Bot, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import TODAY_REPORT_BUTTON_TEXT
from bot.middlewares.throttling import rate_limit
from core.config import settings
from core.utils import send_daily_report


router = Router()


@router.message(F.text == TODAY_REPORT_BUTTON_TEXT)
@rate_limit(limit=1)
async def echo(message: Message, session: AsyncSession, bot: Bot):
    await send_daily_report(
        session=session,
        bot=bot,
        chat_id=message.chat.id,
        dt=datetime.now().astimezone(settings.tzinfo).date()
    )