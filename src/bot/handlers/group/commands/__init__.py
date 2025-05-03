from aiogram import Router

from bot.handlers.group.commands import report, today


command_router = Router()
command_router.include_routers(
    report.router,
    today.router
)
