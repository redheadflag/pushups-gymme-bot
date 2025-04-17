from datetime import date, timedelta
import random

from aiogram.utils.markdown import hlink

from core.config import settings
from db.models import User


STREAK_FIRST_DAY = "Добро пожаловать в клуб! 💪"

GREETING_MESSAGE_FIRST_PART = "\n\n".join([
    "Привет, {}!",
    "Здесь мы делаем прокачиваемся каждый день, делая отжимания."
])

GREETING_MESSAGE_SENT_VIDEO = "\n\n".join([
    GREETING_MESSAGE_FIRST_PART,
    f"Как я вижу, ты сразу врываешься в бой. Достойно уважения! Но на всякий случай, ознакомься с {hlink("правилами", settings.RULES_URL)}"
])

GREETING_MESSAGE_FIRST_MESSAGE = "\n\n".join([
    GREETING_MESSAGE_FIRST_PART,
    f"Присоединяйся к нам! Но для начала, ознакомься с {hlink("правилами", settings.RULES_URL)}"
])


ATHLETE_REFERENCES = [
    "Хорош, качок!",
    "Хорош, машина.",
    "Молодчина!",
    "Молорик, зверюга.",
    "А я уже и не верил в тебя..",
    "Горилла, красава."
]

def last_chance_msg() -> str:
    return random.choice(ATHLETE_REFERENCES) + "\n\n" + "Ты успел сделать отжимания в последний вагон 🚃"


def get_daily_report(users: list[User], dt: date) -> str:
    text_parts = list()
    text_parts.append(f"Отчёт за {dt.strftime("%d.%m.%Y")}")
    
    users_progress = list()
    for user in users:
        if user.last_completed == dt:
            sign = "✅"
        elif user.last_completed == dt - timedelta(days=1):
            sign = "⚠️"
        else:
            sign = "❌"
        
        users_progress.append(f"{sign} ({user.streak}) {hlink(user.mention, f"tg://user?id={user.id}")}")
    
    text_parts.append("\n".join(users_progress))

    text = "\n\n".join(text_parts)
    return text
