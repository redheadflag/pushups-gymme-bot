from re import Match
import logging

from aiogram import F, Router
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from bot.enums import PointEvent, get_bonus_points_for_quantity
from bot.filters.new_users import IsNewUser
from core.config import settings
from db.commands import change_points, pushup_entry_repository, user_repository
from db.models import PushupEntry


logger = logging.getLogger(__name__)


router = Router()


@router.message(
    IsNewUser(is_new=False),
    F.reply_to_message,
    F.text.regexp(r"^\d*\.?\d+$").as_("quantity"),
    F.reply_to_message.content_type.in_(settings.ALLOWED_CONTENT_TYPES)
)
async def add_pushups_quantity(message: Message, session: AsyncSession, quantity: Match[str]):
    pushup_count = int(float(quantity.group()))
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
    entry.quantity = pushup_count
    await session.commit()
    user = await user_repository.get_or_raise(session, user_id)
    await change_points(session, point_event=PointEvent.PUSHUP_AMOUNT_SUBMISSION.value, user=user)
    event_details = get_bonus_points_for_quantity(pushup_count)
    await change_points(session, point_event=event_details, user=user)
    await message.react(reaction=[ReactionTypeEmoji(emoji="👍")])
