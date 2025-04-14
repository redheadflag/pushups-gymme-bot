from typing import Generic, TypeVar

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import Base
from db.models import User

Model = TypeVar("Model", bound=Base)


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
