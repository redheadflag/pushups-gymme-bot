import datetime
from sqlalchemy import BigInteger, Date, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from db.mixins import TimeStampedMixin


class User(TimeStampedMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(length=32), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(length=128), nullable=False)

    streak: Mapped[int] = mapped_column(SmallInteger, default=0)
    last_completed: Mapped[datetime.date] = mapped_column(nullable=True)
    
    pushup_entries: Mapped[list["PushupEntry"]] = relationship(back_populates="user")


class PushupEntry(Base):
    __tablename__ = "pushup_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user: Mapped["User"] = relationship(back_populates="pushup_entries")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    quantity: Mapped[int] = mapped_column(nullable=True)
    date: Mapped[datetime.date] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.time] = mapped_column(nullable=True)
