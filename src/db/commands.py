from datetime import date, datetime, time, timedelta
from enum import Enum
import logging
from typing import Generic, TypeVar

from sqlalchemy import BinaryExpression, Time, cast, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.enums import EventDetails, PointEvent
from core.utils import get_current_datetime
from core.config import settings
from db.base import Base
from db.exceptions import NotFoundError
from db.models import PointsTransaction, User, PushupEntry


logger = logging.getLogger(__name__)

Model = TypeVar("Model", bound=Base)  # type: ignore


class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model]) -> None:
        self.model = model

    async def create(self, session: AsyncSession, data: dict) -> Model:
        instance = self.model(**data)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def get(self, session: AsyncSession, pk: int) -> Model | None:
        return await session.get(self.model, pk)
    
    async def get_or_raise(self, session: AsyncSession, pk: int) -> Model:
        instance = await self.get(session, pk)
        if not instance:
            raise NotFoundError("Instance not found")
        return instance
    
    async def get_all(
        self,
        session: AsyncSession
    ) -> list[Model]:
        return await self.filter(session=session)

    async def filter(
        self,
        session: AsyncSession,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        stmt = select(self.model)
        if expressions:
            stmt = stmt.where(*expressions)
        return list(await session.scalars(stmt))


user_repository = DatabaseRepository(User)
pushup_entry_repository = DatabaseRepository(PushupEntry)
points_transaction_repository = DatabaseRepository(PointsTransaction)


async def add_or_update_user(session: AsyncSession, data: dict) -> User:
    pk = data.get("id", None)
    if pk is None:
        raise ValueError("Pass telegram id of the user")
    user = await user_repository.get(session, pk=pk)
    if user:
        logger.info("Update user id=%i", user.id)
        for key, value in data.items():
            setattr(user, key, value)
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        logger.info("Create user id=%i", pk)
        user = await user_repository.create(session=session, data=data)
    return user


async def get_all_users(session: AsyncSession) -> list[User]:
    stmt = (
        select(User).
        options(selectinload(User.pushup_entries)).
        order_by(User.streak.desc())
    )

    return list(await session.scalars(stmt))


async def get_early_bird_user(session: AsyncSession, dt: date) -> User | None:
    stmt = (
        select(User).
        join(PushupEntry).
        where(PushupEntry.date == dt).
        where(cast(PushupEntry.timestamp, Time) > time(4, 0)).
        order_by(PushupEntry.timestamp).
        limit(1)
    )

    return await session.scalar(stmt)


async def get_strongest_user(session: AsyncSession, dt: date) -> User | None:
    stmt = (
        select(User).
        join(PushupEntry).
        where(PushupEntry.date == dt).
        where(PushupEntry.quantity.isnot(None)).
        order_by(PushupEntry.quantity.desc()).
        limit(1)
    )

    return await session.scalar(stmt)


async def get_last_wagon_user(session: AsyncSession, dt: date) -> User | None:
    stmt = (
        select(User).
        join(PushupEntry).
        where(PushupEntry.date == dt).
        order_by(PushupEntry.timestamp.desc()).
        limit(1)
    )

    return await session.scalar(stmt)


async def add_pushup_entry(session: AsyncSession, user: User) -> PushupEntry | None:
    dt_now = get_current_datetime()
    today_date = dt_now.date()
    today_time = dt_now.time()
    if user.last_completed == today_date:
        logger.info(
            "User id=%i has sent not the first video for today. Adding an entry is skipped",
            user.id 
        )
        return
    
    data = {
        "user": user,
        "date": today_date,
        "timestamp": today_time,
    }

    pushup_entry = await pushup_entry_repository.create(session, data)
    
    logger.info(
        "Created pushup entry id=%i, user.id=%i",
        pushup_entry.id, user.id,
    )

    await sync_user_streak(session=session, user=user)
    await change_points(session, point_event=PointEvent.DAILY_ENTRY_SUBMISSION.value, user=user)

    return pushup_entry


async def sync_user_streak(session: AsyncSession, user: User) -> User:
    stmt = (
        select(PushupEntry).
        where(PushupEntry.user_id == user.id).
        order_by(PushupEntry.date.desc())
    )
    entries = list(await session.scalars(stmt))

    if not entries:
        user.streak = 0
        user.last_completed = None
        await session.commit()
        return user

    latest_date = entries[0].date
    user.last_completed = latest_date

    today_date = datetime.now(settings.tzinfo).date()
    if latest_date < today_date - timedelta(days=2):
        user.streak = 0
        await session.commit()
        return user

    streak = 1
    previous_date = latest_date

    for entry in entries[1:]:
        delta_days = (previous_date - entry.date).days
        if delta_days == 1:
            streak += 1
            previous_date = entry.date
        elif delta_days == 2:
            streak += 1
            previous_date = entry.date
        else:
            break

    user.streak = streak
    await session.commit()
    return user


async def sync_user_points(session: AsyncSession, user: User) -> User:
    stmt = (
        select(PointsTransaction).
        where(PointsTransaction.user_id == user.id)
    )

    transactions = await session.scalars(stmt)
    
    if not transactions:
        user.points = 0
        return user
    
    user_points = 0
    
    for transaction in transactions:
        user_points += transaction.points_change

    user.points = user_points
    await session.commit()
    return user


async def remove_pushup_entry(session: AsyncSession, user_id: int, entry_date: date) -> None:
    pushup_entry = await pushup_entry_repository.filter(
        session,
        PushupEntry.user_id == user_id,  # type: ignore
        entry_date == PushupEntry.date  # type: ignore
    )
    
    if len(pushup_entry) != 1:
        raise ValueError(f"There are {len(pushup_entry)} entries for {entry_date} from user id={user_id}")
    
    pushup_entry = pushup_entry[0]
    await session.delete(pushup_entry)
    await session.flush()
    await sync_user_streak(session, await user_repository.get(session, user_id))


async def change_points(
        session: AsyncSession,
        point_event: EventDetails,
        user_id: int | None = None,
        user: User | None = None
) -> PointsTransaction:
    if user is None and user_id is None:
        raise ValueError("You must provide either 'user_id' or 'user'.")
    
    if user is None:
        user = await user_repository.get_or_raise(session, user_id)
    
    user_id = user_id or user.id
    
    user.points += point_event.points

    logger.info("Add %i points to user %i", point_event.points, user.id)

    points_transaction = await points_transaction_repository.create(
        session=session,
        data=dict(
            user_id=user_id,
            points_change=point_event.points,
            reason=point_event.reason
        )
    )

    return points_transaction
