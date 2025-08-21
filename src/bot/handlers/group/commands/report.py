import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.commands import remove_pushup_entry
from bot.filters.admin_command import AdminFilter


logger = logging.getLogger(__name__)

router = Router()
router.message.filter(AdminFilter())

@router.message(Command("report"))
async def report_command_handler(message: Message, session: AsyncSession):
    logger.info("Admin calls command /report")
    if not message.reply_to_message:
        logger.info("Command /report is used without replying message")
        return
    reported_message = message.reply_to_message
    if not reported_message.from_user:
        logger.info("Command /report is used to channel's message")
        return
    msg_date = reported_message.date.astimezone(settings.tzinfo).date()
    await remove_pushup_entry(session=session, user_id=reported_message.from_user.id, entry_date=msg_date)
    await message.reply(f"Видео пользователя {reported_message.from_user.mention_html()} удалено из зачёта.")
