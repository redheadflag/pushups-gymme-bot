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
    users_summary = await get_all_users_summary(session=session)
    report_text = get_daily_report(
        users_summary=users_summary,
        dt=datetime.now().astimezone(settings.tzinfo).date()
    )
    await message.answer(text=report_text)
