import logging
import re
from datetime import time

from aiogram import F, Bot, Router
from aiogram.enums import ContentType
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.user_context import UserContext
from core import strings
from core.config import settings
from core.utils import bot_set_reaction
from db.commands import add_pushup_entry, add_pushup_quantity_points


logger = logging.getLogger(__name__)


router = Router()


@router.message(
    F.content_type.in_(settings.ALLOWED_CONTENT_TYPES)
)
async def user_sends_video_handler(message: Message, session: AsyncSession, user_context: UserContext, bot: Bot):
    user = await user_context.get_user(session)
    entry = await add_pushup_entry(session=session, user=user)
    if not entry:
        return
    
    if message.content_type == ContentType.VIDEO \
            and message.caption \
            and re.fullmatch(r"^\d*\.?\d+$", message.caption):
        quantity = int(message.caption)
        entry.quantity = quantity
        await session.commit()
        # await add_pushup_quantity_points(session=session, quantity = quantity, user=user)

    if entry.timestamp > time(hour=23, minute=55):
        await message.reply(strings.last_chance_msg())
    
    await bot_set_reaction(
        message=message,
        guaranteed=True
    )
    
    # streak = await user.get_streak(session)
    # 
    # if streak == 1:
    #     if user.created_at.astimezone(settings.tzinfo) == get_current_datetime().date:
    #         await message.reply(strings.STREAK_FIRST_DAY)
    #         await add_points_transaction(session, PointEvent.FIRST_PUSHUPS.value, user=user)
    #         await bot_set_reaction(
    #             message=message,
    #             reaction=SPECIAL_REACTION,
    #             guaranteed=True
    #         )
    #     else:
    #         await bot_set_reaction(
    #             message=message,
    #             guaranteed=True
    #         )
    #         await message.reply(strings.USER_WELCOME_BACK.format(user=str(user)))
    # else:
    #     admins = await get_admins(session=session)
    #     additional_message = str()
    #     if streak == 30:
    #         await add_points_transaction(session, PointEvent.STREAK_30_DAYS.value, user=user)
    #         additional_message = strings.STREAK_30_DAYS.format(user=str(user))
    #         for admin in admins:
    #             await bot.send_message(admin.id, f"Добавьте {user.as_hlink} в доску почета (30 дней)")
    #     elif streak == 100:
    #         await add_points_transaction(session, PointEvent.STREAK_100_DAYS.value, user=user)
    #         additional_message = strings.STREAK_100_DAYS.format(user=str(user))
    #         for admin in admins:
    #             await bot.send_message(admin.id, f"Добавьте {user.as_hlink} в доску почета (100 дней)")
    #     elif streak == 182:
    #         # TODO: add a message for group
    #         for admin in admins:
    #             await bot.send_message(admin.id, f"Добавьте {user.as_hlink} в доску почета (Полгода)")
    #     if additional_message:
    #         await message.reply(additional_message)
        
    #     await bot_set_reaction(
    #         message=message,
    #         guaranteed=True
    #     )
