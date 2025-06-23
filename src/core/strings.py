from datetime import date, datetime, timedelta
from functools import reduce
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
        
        users_strings.append(f"{sign} {hlink(user.mention, f"tg://user?id={user.id}")}")
    
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


def get_user_stats(user: User) -> str:
    if "pushup_entries" not in user.__dict__ or "points_transactions" not in user.__dict__:
        raise ValueError("You should provide both pushup_entries and points_transactions to call this function")
    
    text_parts = list()
    text_parts.append(
        "\n".join([
            f"📈 Статистика {user.as_hlink}",
            f"Дата регистрации: {user.created_at.strftime("%d.%m.%Y")}",
            # f"Опыт: {user.points_transactions[0].balance_after}"
        ])
    )

    max_streak = sorted(user.pushup_entries, key=lambda entry: entry.streak, reverse=True)[0].streak

    user.pushup_entries.sort(key=lambda entry: entry.date, reverse=True)
    user.points_transactions.sort(key=lambda t: t.created_at, reverse=True)

    text_parts.append(
        "\n".join([
            f"🔥 Текущая серия: {pluralize_days(user.pushup_entries[0].streak)}",
            f"Максимальная серия: {pluralize_days(max_streak)}",
        ])
    )

    total_quantity = reduce(lambda x, y: x + (y.quantity if y.quantity is not None else 0), user.pushup_entries, 0)
    max_quantity = max((entry.quantity for entry in user.pushup_entries if entry.quantity is not None), default=0)

    text_parts.append(
        "\n\n".join([
            f"За все время выполнено {pluralize_pushups(total_quantity)}",
            f"🚀 Рекорд за один раз: {pluralize_pushups(max_quantity)}"
        ])
    )

    today = datetime.now(settings.tzinfo)
    last_5_days = [(today - timedelta(days=i)).date() for i in reversed(range(5))]
    entries_by_date = {entry.date: entry.quantity or "✅" for entry in user.pushup_entries[:5]}
    last_5_days_strings = [
        entries_by_date.get(day, "⚠️" if day == today.date() else "✖")
        for day in last_5_days
    ]

    text_parts.append(
        "\n".join([
            "Последние 5 дней",
            " • ".join(map(str, last_5_days_strings))
        ])
    )

    return "\n\n".join(text_parts)


def pluralize_days(n: int) -> str:
    """
    Возвращает строку с числом и правильным окончанием для слова 'день'.

    Примеры:
    1 -> "1 день"
    2 -> "2 дня"
    5 -> "5 дней"
    """
    if 11 <= n % 100 <= 14:
        ending = "дней"
    else:
        last_digit = n % 10
        if last_digit == 1:
            ending = "день"
        elif 2 <= last_digit <= 4:
            ending = "дня"
        else:
            ending = "дней"
    return f"{n} {ending}"


def pluralize_pushups(n: int) -> str:
    """
    Возвращает строку с числом и правильным окончанием для слова 'отжимание'.

    Примеры:
    1 -> "1 отжимание"
    2 -> "2 отжимания"
    5 -> "5 отжиманий"
    """
    if 11 <= n % 100 <= 14:
        ending = "отжиманий"
    else:
        last_digit = n % 10
        if last_digit == 1:
            ending = "отжимание"
        elif 2 <= last_digit <= 4:
            ending = "отжимания"
        else:
            ending = "отжиманий"
    return f"{n} {ending}"

