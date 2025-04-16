from aiogram import Router

from bot.handlers.group.commands import report


command_router = Router()
command_router.include_routers(
    report.router
)
