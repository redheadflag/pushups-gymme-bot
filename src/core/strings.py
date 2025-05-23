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


def get_daily_report(
    users: list[User],
    dt: date,
    early_bird_user: User | None = None,
    last_wagon_user: User | None = None,
    strongest_user: User | None = None
) -> str:
    text_parts = list()
    text_parts.append(
        f"Отчёт за {dt.strftime("%d.%m.%Y")}\n" +
        f"Спортсменов: {sum(1 for u in users if u.last_completed in [dt, dt - timedelta(days=1), dt - timedelta(days=2)])}" 
    )
    
    users_progress = list()
    for user in users:
        if user.streak == 0:
            continue
        if user.last_completed == dt:
            sign = "✅"
        elif user.last_completed == dt - timedelta(days=1):
            sign = "⚠️"
        elif user.last_completed == dt - timedelta(days=2):
            sign = "❄️"
        else:
            sign = "❌"
        
        users_progress.append(f"{sign} {hlink(user.mention, f"tg://user?id={user.id}")}")
    
    text_parts.append("\n".join(users_progress))

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
