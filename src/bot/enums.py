from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class EventDetails:
    points: int
    reason: str


class PointEvent(Enum):
    DAILY_ENTRY_SUBMISSION = EventDetails(10, "Daily entry bonus")
    PUSHUP_AMOUNT_SUBMISSION = EventDetails(2, "The number of push-ups is written in")
    FIRST_PUSHUPS = EventDetails(20, "First step is the hardest")
    WINNING_NOMINATION = EventDetails(50, "Winning the nomination")
    STREAK_30_DAYS = EventDetails(30, "30 days streak")
    STREAK_100_DAYS = EventDetails(100, "100 days streak")


def get_bonus_points_for_quantity(quantity: int) -> EventDetails:
    return EventDetails(quantity//10, f"Bonus points for {quantity} pushups")
