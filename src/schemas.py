from datetime import date
from pydantic import BaseModel


class UserSummary(BaseModel):
    id: int
    mention: str

    points: int

    latest_entry_date: date | None
    current_streak: int
