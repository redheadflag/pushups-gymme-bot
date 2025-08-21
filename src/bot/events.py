from abc import ABC, abstractmethod
import logging
from typing import Sequence

from aiogram import Bot
from aiogram.types import Message, TelegramObject, Update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.user_context import UserContext
from core import strings
from core.utils import send_message_to_admins
from db.models import PushupEntry


logger = logging.getLogger(__name__)


class Event(ABC):
    text: str
    admin_message_text: str | None

    def __init__(self, text: str, admin_message_text: str | None) -> None:
        self.text = text
        self.admin_message_text = admin_message_text

    @abstractmethod
    def is_happened(self, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    async def handle(self, bot: Bot, message: Message, session: AsyncSession, user_context: UserContext) -> None:
        pass


class DaysMilestoneEvent(Event):
    _base_text = """{days} дней отжиманий!"""

    def __init__(self, days: int, text: str | None = None, admin_message_text: str | None = None) -> None:
        text = text or self._base_text.format(days=days)
        super().__init__(
            text=text,
            admin_message_text=admin_message_text
        )

        self.days = days
    
    def is_happened(self, pushup_entry: PushupEntry | None, *args, **kwargs) -> bool:
        if not pushup_entry:
            return False
        if self.days == pushup_entry.streak:
            return True
        return False

    async def handle(self, bot: Bot, message: Message, session: AsyncSession, user_context: UserContext):
        logging.info("Handling event %s", repr(self))

        user = await user_context.get_user(session)
        
        if self.days == 1:
            if user_context.is_new:
                await message.reply(self.text.format(user_as_hlink=user.as_hlink))
            else:
                await message.reply(strings.USER_WELCOME_BACK.format(user_as_hlink=user.as_hlink))
        else:
            await message.reply(self.text.format(user_as_hlink=user.as_hlink))
        
        if self.admin_message_text:
            await send_message_to_admins(bot=bot, session=session, text=self.admin_message_text.format(user_as_hlink=user.as_hlink))
    
    def __repr__(self) -> str:
        return f"<Event {type(self)}, days={self.days}>"


DAYS_MILESTONE_EVENTS = [
    DaysMilestoneEvent(1, "{user_as_hlink}, добро пожаловать в клуб!", admin_message_text="Пользователь {user_as_hlink} сделал отжимания впервые"),
    DaysMilestoneEvent(30, strings.STREAK_30_DAYS, admin_message_text="Добавьте {user_as_hlink} в доску почета (30 дней)"),
    DaysMilestoneEvent(100, strings.STREAK_100_DAYS, admin_message_text="Добавьте {user_as_hlink} в доску почета (100 дней)"),
    DaysMilestoneEvent(182, "Полгода отжиманий!", admin_message_text="Добавьте {user_as_hlink} в доску почета (Полгода)"),
    DaysMilestoneEvent(365, "Год отжиманий!", admin_message_text="Добавьте {user_as_hlink} в доску почета (Год)"),
    DaysMilestoneEvent(730, "2 года отжиманий!", admin_message_text="Добавьте {user_as_hlink} в доску почета (2 года)"),
]

EVENTS = [
    *DAYS_MILESTONE_EVENTS,
]


async def detect_events(session: AsyncSession, user_context: UserContext) -> Sequence[Event]:
    detected_events = list()
    pushup_entry = await user_context.get_latest_pushup_entry(session)
    for event in EVENTS:
        if event.is_happened(pushup_entry):
            detected_events.append(event)
    
    return detected_events
