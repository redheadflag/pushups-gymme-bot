from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import db_settings

Base = declarative_base()

engine = create_async_engine(db_settings.url, echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
