from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from core.config import settings

bot = Bot(settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML"))
