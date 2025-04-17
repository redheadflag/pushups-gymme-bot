import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import LinkPreviewOptions

from core.config import settings
from core.redis import redis


logger = logging.getLogger(__name__)

bot = Bot(
    settings.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode="HTML",
        link_preview=LinkPreviewOptions(
            is_disabled=True
        ),
    )
)

dp = Dispatcher(storage=RedisStorage(redis))
