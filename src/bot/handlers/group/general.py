from aiogram import Router
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from core import strings
from db.commands import add_or_update_user


router = Router()


@router.chat_member()
async def new_chat_member(session: AsyncSession, chat_member: ChatMemberUpdated):
    user = await add_or_update_user(
        session=session,
        data={
            "id": chat_member.from_user.id,
            "username": chat_member.from_user.username,
            "full_name": chat_member.from_user.full_name
        }
    )

    await chat_member.answer(strings.NEW_CHAT_MEMBER.format(user_as_hlink=user.as_hlink))
