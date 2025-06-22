import asyncio
from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.enums import PointEvent, get_bonus_points_for_quantity
from core.utils import get_current_datetime
from db.base import sessionmaker
from db.commands import add_points_transaction, get_all_users, logger
from db.models import PointsTransaction, PushupEntry


async def recalculate_all_points_from(session: AsyncSession, from_date: date) -> None:
    """
    Recalculate all users' points from a given date up to today.
    Removes all points transactions after from_date and recalculates them.
    """
    logger.info("Recalculating all points from %s", from_date)

    # Remove all points transactions after from_date
    await session.execute(
        delete(PointsTransaction).where(PointsTransaction.created_at >= from_date)
    )
    await session.commit()

    users = await get_all_users(session)
    today = get_current_datetime().date()

    for user in users:
        logger.info("Recalculating points for user %s", user.id)
        # Get all pushup entries for this user from from_date to today, ordered by date
        stmt = (
            select(PushupEntry)
            .where(PushupEntry.user_id == user.id)
            .where(PushupEntry.date >= from_date)
            .where(PushupEntry.date <= today)
            .order_by(PushupEntry.date)
        )
        entries = list(await session.scalars(stmt))
        streak = 0

        for entry in entries:
            # Streak calculation
            if streak == 0 or (entry.date - entries[entries.index(entry)-1].date).days in (1, 2):
                streak += 1
            else:
                streak = 1

            # Daily entry bonus
            await add_points_transaction(
                session=session,
                point_event=PointEvent.DAILY_ENTRY_SUBMISSION.value,
                user=user
            )

            # First pushups bonus
            if streak == 1 and entry.date == user.created_at.date():
                await add_points_transaction(
                    session=session,
                    point_event=PointEvent.FIRST_PUSHUPS.value,
                    user=user
                )

            # Streak bonuses
            if streak == 30:
                await add_points_transaction(
                    session=session,
                    point_event=PointEvent.STREAK_30_DAYS.value,
                    user=user
                )
            if streak == 100:
                await add_points_transaction(
                    session=session,
                    point_event=PointEvent.STREAK_100_DAYS.value,
                    user=user
                )

            # Quantity bonus
            if entry.quantity:
                await add_points_transaction(
                    session=session,
                    point_event=PointEvent.PUSHUP_AMOUNT_SUBMISSION.value,
                    user=user
                )
                bonus = get_bonus_points_for_quantity(entry.quantity)
                await add_points_transaction(
                    session=session,
                    point_event=bonus,
                    user=user
                )

        await session.commit()
    logger.info("Recalculation finished.")

async def main():
    from_date = date(2024, 1, 1)  # <-- CHANGE THIS DATE as needed
    async with sessionmaker() as session:
        await recalculate_all_points_from(session, from_date)

if __name__ == "__main__":
    asyncio.run(main())


# Script usage: docker compose run --rm bot python recalculate_points.py
