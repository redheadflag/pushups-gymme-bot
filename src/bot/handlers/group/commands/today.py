from datetime import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.strings import get_daily_report
from db.commands import get_all_users_summary


router = Router()


@router.message(Command("today"))
async def today_report_handler(message: Message, session: AsyncSession):
    await message.reply(
        "Команда отключена. " \
        "Чтобы посмотреть отчёт за сегодня, а также вашу статистику за все время, " \
        "перейдите в личные сообщения со мной"
    )
    return
