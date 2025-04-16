from aiogram.utils.markdown import hlink

from core.config import settings


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
