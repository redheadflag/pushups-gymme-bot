import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import menu_markup
from core.config import settings


logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message, session: AsyncSession):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"  # type: ignore
        f"Это официальный бот для сообщества {hlink("В погоне за пампом", settings.RULES_URL)}!\n",
        reply_markup=menu_markup
    )
