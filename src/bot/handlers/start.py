from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from db.commands import user_repository


router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message, session: AsyncSession):
    await message.answer(f"Hi, {message.from_user.first_name}!")  # type: ignore
    await user_repository.create(
        session=session,
        data={
            "id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name
        }
    )
