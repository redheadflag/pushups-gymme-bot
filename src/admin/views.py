import logging
from typing import Any, Dict
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin import TimeField
from starlette_admin.fields import HasOne, IntegerField, StringField, HasMany, BooleanField, DateField, DateTimeField
from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import ActionFailed

from bot.enums import EventDetails
from db.commands import add_points_transaction, get_current_balance, sync_user_streak, user_repository, pushup_entry_repository
from db.models import PushupEntry, PointsTransaction


logger = logging.getLogger(__name__)


class UserView(ModelView):
    fields = [
        IntegerField("id", label="ID"),
        StringField("username", label="Имя пользователя"),
        StringField("full_name", label="Полное имя"),
        DateField("last_completed", label="Последнее выполнение"),
        BooleanField("is_admin", label="Админ"),
        HasMany("pushup_entries", identity="pushup-entry", label="Записи отжиманий"),
        HasMany("points_transactions", identity="points-transaction", label="Транзакции баллов"),
    ]
    form_include_pk = True


class PushupEntryView(ModelView):
    fields = [
        IntegerField("id", label="ID"),
        HasOne("user", label="Пользователь", identity="user"),
        IntegerField("user_id", label="ID пользователя"),
        IntegerField("quantity", label="Количество"),
        DateField("date", label="Дата"),
        TimeField("timestamp", label="Время"),
        IntegerField("streak", label="Серия"),
    ]
    
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


class PointsTransactionView(ModelView):
    form_include_pk = True

    fields = [
        StringField("id", exclude_from_create=True, exclude_from_edit=True),
        HasOne("user", "Пользователь", identity="user"),
        IntegerField("points_change", "Сколько баллов добавить/убрать"),
        StringField("reason", "Причина"),
        IntegerField("balance_after", exclude_from_create=True, exclude_from_edit=True),
        DateTimeField("created_at", exclude_from_create=True, exclude_from_edit=True),
        DateTimeField("updated_at", exclude_from_create=True, exclude_from_edit=True),
    ]

    def can_create(self, request: Request) -> bool:
        return False

    # async def before_create(self, request: Request, data: Dict[str, Any], obj: PointsTransaction) -> None:
    #     session: AsyncSession = request.state.session
    #     logger.warning(obj)
    #     obj = await add_points_transaction(
    #         session=session,
    #         point_event=EventDetails(points=obj.points_change, reason=obj.reason),
    #         user=obj.user
    #     )
    #     obj.balance_after = obj.points_change + await get_current_balance(session=session, user_id=obj.user.id)
    #     await session.commit()

    def can_delete(self, request: Request) -> bool:
        return False
    
    async def before_edit(self, request: Request, data: Dict[str, Any], obj: Any) -> None:
        pass
