from datetime import datetime
import logging
from typing import AsyncGenerator

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker
import taskiq_aiogram

from core.config import settings, redis_settings
from core.utils import send_daily_report
from db.base import sessionmaker


logger = logging.getLogger(__name__)

broker = ListQueueBroker(redis_settings.taskiq_url)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

taskiq_aiogram.init(
    broker=broker,
    dispatcher="bot.dependencies:dp",
    bot="bot.dependencies:bot"
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


@broker.task(
        schedule=[{"cron": "00 23 * * *", "cron_offset": settings.TIMEZONE}]
)
async def daily_report_task(bot: Bot = TaskiqDepends(), session: AsyncSession = TaskiqDepends(get_session)) -> None:
    logger.info("Starting scheduled task")
    
    await send_daily_report(
        session=session,
        bot=bot,
        chat_id=settings.GROUP_ID,
        topic_id=settings.PUSHUPS_TOPIC_ID,
        dt=datetime.now().astimezone(settings.tzinfo).date()
    )

    logger.info("Daily report was sent")
