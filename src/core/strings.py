from datetime import date, timedelta
import random

from aiogram.utils.markdown import hlink

from core.config import settings
from db.models import User
from schemas import UserSummary


STREAK_FIRST_DAY = "Добро пожаловать в клуб! 💪"
USER_WELCOME_BACK = "{user}, с возвращением!"

STREAK_30_DAYS = """{user}, уважение!

30 дней отжиманий - это мощно!

Теперь твоё имя будет на доске почета нашего сообщества. 

Не сбавляй обороты! Дальше будет только интереснее! 🦍"""

STREAK_100_DAYS = """{user}, это уже легенда! 🔥

100 дней отжиманий без пропусков — ты переписал правила игры!

Твоё упорство вдохновляет всех в сообществе.  
Ты — живое доказательство силы дисциплины и характера.

Продолжай, впереди новые вершины! 🚀"""

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


def get_daily_report(
    users_summary: list[UserSummary],
    dt: date,
    early_bird_user: User | None = None,
    last_wagon_user: User | None = None,
    strongest_user: User | None = None
) -> str:
    text_parts = list()
    text_parts.append(
        f"Отчёт за {dt.strftime("%d.%m.%Y")}\n" +
        f"Спортсменов: {sum(1 for u in users_summary if u.latest_entry_date in [dt, dt - timedelta(days=1), dt - timedelta(days=2)])}" 
    )

    users_summary.sort(key=lambda u: u.current_streak, reverse=True)
    users_strings = list()

    for user in users_summary:
        if user.current_streak == 0:
            continue
        if user.latest_entry_date == dt:
            sign = "✅"
        elif user.latest_entry_date == dt - timedelta(days=1):
            sign = "⚠️"
        elif user.latest_entry_date == dt - timedelta(days=2):
            sign = "❄️"
        elif user.latest_entry_date == dt - timedelta(days=3):
            sign = "❌"
        else:
            continue
        
        users_strings.append(f"{sign} {hlink(user.mention, f"tg://user?id={user.id}")} ({user.points})")
    
    text_parts.append("\n".join(users_strings))

    if any([early_bird_user, last_wagon_user, strongest_user]):
        yesterday_nominations = list()
        yesterday_nominations.append(f"Номинации за вчера ({(dt - timedelta(days=1)).strftime("%d.%m.%Y")})\n")

        if early_bird_user:
            yesterday_nominations.append(f"🐦 Ранняя пташка: {early_bird_user.as_hlink}")
        
        if last_wagon_user:
            yesterday_nominations.append(f"🚂 Последний вагон: {last_wagon_user.as_hlink}")

        if strongest_user:
            yesterday_nominations.append(f"💪 Самое большое количество отжиманий: {strongest_user.as_hlink}")

        text_parts.append("\n".join(yesterday_nominations))

    text = "\n\n".join(text_parts)
    return text
