from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import I18nConfig
from starlette_admin.contrib.sqla import Admin

from admin.providers import EnvAuthProvider
from admin.views import PushupEntryView, UserView, PointsTransactionView
from core.config import admin_settings
from db.base import engine
from db.models import *


app = Starlette()

admin = Admin(
    engine=engine,
    title="GYMME SQUAD",
    base_url=admin_settings.ENDPOINT,
    auth_provider=EnvAuthProvider(),
    middlewares=[
        Middleware(
            SessionMiddleware,
            secret_key=admin_settings.SECRET_TOKEN.get_secret_value(),
            max_age=admin_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
    ],
    i18n_config=I18nConfig(default_locale="ru"),
)

admin.mount_to(app)

admin.add_view(
    UserView(
        model=User,
        icon="fa-solid fa-user",
        name="качок",
        label="Качки",
        identity="user"
    )
)

admin.add_view(
    PushupEntryView(
        model=PushupEntry,
        name="запись отжиманий",
        label="Дневник отжиманий",
        identity="pushup-entry"
    )
)

admin.add_view(
    PointsTransactionView(
        model=PointsTransaction,
        name="транзакция",
        label="Начисления баллов",
        identity="points-transaction"
    )
)
