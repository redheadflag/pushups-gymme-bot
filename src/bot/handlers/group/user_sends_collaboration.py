import datetime
from re import Match
from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.user_context import UserContext
from core.config import settings
from db.commands import add_pushup_entry, get_user_by_id, pushup_entry_repository
from db.models import PushupEntry


router = Router()


@router.message(
    F.reply_to_message,
    F.reply_to_message.content_type.in_(settings.ALLOWED_CONTENT_TYPES),
    F.text.regexp(r"^@[A-Za-z0-9_]+$").as_("collab_user")
)
async def user_sends_collab(message: Message, session: AsyncSession,
                            collab_user: Match[str], user_context: UserContext):
    collab_user_username = collab_user.group()
    collab_user_username_without_at_sign = collab_user_username[1:]
    collab_user_db = await get_user_by_id(session, collab_user_username_without_at_sign)
    
    replied_message = message.reply_to_message
    entry_date = replied_message.date.astimezone(settings.tzinfo).date()
    user_id = replied_message.from_user.id
    entry = await pushup_entry_repository.filter(
        session,
        PushupEntry.user_id == user_id,
        PushupEntry.date == entry_date
    )

    if len(entry) != 1:
        await message.reply("Запись не найдена :(")
        return
    
    entry = entry[0]

    await add_pushup_entry(
        session,
        user=collab_user_db,
        dt=datetime.datetime(
            year=entry.date.year,
            month=entry.date.month,
            day=entry.date.day,
            hour=entry.timestamp.hour,
            minute=entry.timestamp.minute,
            second=entry.timestamp.second
        ),
        entry_data={
            'quantity': entry.quantity,
        }
    )

    await message.reply(f"Записал для {collab_user_username}")
