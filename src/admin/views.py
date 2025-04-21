import logging
from typing import Any, Dict
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import ActionFailed

from db.commands import sync_user_streak, user_repository, pushup_entry_repository
from db.models import PushupEntry


logger = logging.getLogger(__name__)


class UserView(ModelView):
    form_include_pk = True


class PushupEntryView(ModelView):
    async def before_create_or_edit(self, request: Request, data: Dict[str, Any], obj: PushupEntry) -> None:
        session: AsyncSession = request.state.session
        user = await user_repository.get(session=session, pk=obj.user_id)
        duplicates = await pushup_entry_repository.filter(session, and_(PushupEntry.user_id == obj.user_id, PushupEntry.date == obj.date))
        if len(duplicates) != 1:
            raise ActionFailed(f"У пользователя {str(user)} уже есть запись отжиманий на этот день")
        await self.after_change(request, obj)

    async def after_change(self, request: Request, obj: PushupEntry) -> None:
        session: AsyncSession = request.state.session
        user = await user_repository.get(session=session, pk=obj.user_id)
        await sync_user_streak(session=session, user=user)
    
    async def before_create(self, request: Request, data: Dict[str, Any], obj: PushupEntry) -> None:
        await self.before_create_or_edit(request, data, obj)
    
    async def before_edit(self, request: Request, data: Dict[str, Any], obj: PushupEntry) -> None:
        await self.before_create_or_edit(request, data, obj)

    async def after_delete(self, request: Request, obj: PushupEntry) -> None:
        await self.after_change(request, obj)
