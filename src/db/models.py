import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from sqlalchemy import BigInteger, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import TimeStampedMixin


class User(TimeStampedMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(length=32), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(length=128), nullable=False)

    streak: Mapped[int] = mapped_column(SmallInteger, default=0)
    last_completed: Mapped[datetime.date | None] = mapped_column(nullable=True)
    
    pushup_entries: Mapped[list["PushupEntry"]] = relationship(back_populates="user")

    is_admin: Mapped[bool] = mapped_column(default=False)

    @property
    def mention(self) -> str:
        if self.username:
            return f"@{self.username}"
        else:
            return self.full_name
    
    def __str__(self) -> str:
        s = f"{self.full_name}"
        if self.username is not None:
            s += f" @{self.username}"
        return s
    
    async def __admin_repr__(self, request: Request) -> str:
        return self.__str__()


class PushupEntry(Base):
    __tablename__ = "pushup_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user: Mapped["User"] = relationship(back_populates="pushup_entries")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    quantity: Mapped[int] = mapped_column(nullable=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.time] = mapped_column(nullable=True)

    def __str__(self) -> str:
        return f"Entry id={self.date.strftime("%d.%m.%Y")} user_id={self.user_id}"

    async def __admin_repr__(self, request: Request) -> str: 
        session: AsyncSession = request.state.session
        await session.refresh(self, attribute_names=["user"])
        return f"{str(self.user)}: {self.date.strftime("%d.%m.%Y")}"
