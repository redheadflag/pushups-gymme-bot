from datetime import datetime

from core.config import settings


def get_current_datetime() -> datetime:
    return datetime.now(settings.tzinfo)
