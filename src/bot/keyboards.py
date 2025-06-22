from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


STATS_BUTTON_TEXT = "Моя статистика"
TODAY_REPORT_BUTTON_TEXT = "Отчёт за сегодня"

menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=STATS_BUTTON_TEXT),
            KeyboardButton(text=TODAY_REPORT_BUTTON_TEXT)
        ]
    ],
    is_persistent=True,
    resize_keyboard=True
)
