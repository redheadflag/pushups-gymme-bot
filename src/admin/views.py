from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import ActionFailed

from db.commands import sync_user_streak, user_repository, pushup_entry_repository
from db.models import PushupEntry


class UserView(ModelView):
    pass


class PushupEntryView(ModelView):
    async def after_change(self, request: Request, obj: PushupEntry) -> None:
        session: AsyncSession = request.state.session
        user = await user_repository.get(session=session, pk=obj.user_id)
        await sync_user_streak(session=session, user=user)
    
    async def after_create(self, request: Request, obj: PushupEntry) -> None:
        session: AsyncSession = request.state.session
        user = await user_repository.get(session=session, pk=obj.user_id)
        duplicates = await pushup_entry_repository.filter(session, PushupEntry.user == user, PushupEntry.date == obj.date)
        if len(duplicates) != 0:
            await session.delete(obj)
            await session.commit()
            raise ActionFailed(f"У пользователя {str(user)} уже есть запись отжиманий на этот день")
        await self.after_change(request, obj)
    
    async def after_edit(self, request: Request, obj: PushupEntry) -> None:
        await self.after_change(request, obj)

    async def after_delete(self, request: Request, obj: PushupEntry) -> None:
        await self.after_change(request, obj)
