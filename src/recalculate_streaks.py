import asyncio
from datetime import date
import logging

from sqlalchemy import select

from db.base import sessionmaker
from db.commands import get_all_users
from db.models import PushupEntry


logger = logging.getLogger(__name__)

async def recalculate_streaks_from(session, from_date: date):
    users = await get_all_users(session)
    for user in users:
        logger.info("Recalculating user %s", repr(user))
        stmt = (
            select(PushupEntry)
            .where(PushupEntry.user_id == user.id)
            .where(PushupEntry.date >= from_date)
            .order_by(PushupEntry.date)
        )
        entries = list(await session.scalars(stmt))
        streak = 0
        prev_date = None
        for entry in entries:
            if prev_date is None:
                streak = 1
            else:
                days_diff = (entry.date - prev_date).days
                if days_diff in (1, 2):
                    streak += 1
                else:
                    streak = 1
            entry.streak = streak
            prev_date = entry.date
            session.add(entry)
        await session.commit()
    logger.info("Streaks recalculated.")

async def main():
    from_date = date(2024, 1, 1)  # <-- CHANGE THIS DATE as needed
    async with sessionmaker() as session:
        await recalculate_streaks_from(session, from_date)

if __name__ == "__main__":
    asyncio.run(main())


# Script usage: docker compose run --rm bot python recalculate_streaks.py
