from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base
from db.mixins import TimeStampedMixin


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(length=32), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(length=128), nullable=False)
