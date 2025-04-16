from datetime import datetime, timedelta
import logging
from typing import Generic, TypeVar

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.base import Base
from db.models import User, PushupEntry


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

    async def filter(
        self,
        session: AsyncSession,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await session.scalars(query))


user_repository = DatabaseRepository(User)
pushup_entry_repository = DatabaseRepository(PushupEntry)


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


async def add_pushup_entry(session: AsyncSession, user: User) -> PushupEntry | None:
    dt_now = datetime.now(settings.tzinfo)
    today_date = dt_now.date()
    today_time = dt_now.time()
    if user.last_completed == today_date:
        logger.warning(
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
    yesterday_date = today_date - timedelta(days=1)
    
    if user.last_completed == yesterday_date:
        user.streak = user.streak + 1
    else:
        user.streak = 1
    
    logger.info(
        "Created pushup entry id=%i, user.id=%i, user.streak=%i",
        pushup_entry.id, user.id, user.streak
    )

    user.last_completed = today_date
    await session.commit()
    await session.refresh(user)
    return pushup_entry
