from typing import Optional

from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed

from core.config import admin_settings


class EnvAuthProvider(AuthProvider):
    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("user", None) is not None:
            """
            Save current `user` object in the request state. Can be used later
            to restrict access to connected user.
            """
            request.state.user = request.session.get("user")
            return True
        return False

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response,
    ) -> Response:
        if username == admin_settings.USERNAME and password == admin_settings.PASSWORD:
            request.session["user"] = {
                "name": "Администратор",
            }
            return response

        raise LoginFailed("Invalid username or password")

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        user = request.state.user
        return AdminUser(username=user["name"])
