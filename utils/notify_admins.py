from aiogram import Dispatcher

from data.config import ADMINS
from loader import logger


async def admin_notify(dp: Dispatcher, msg: str):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, msg)

        except Exception as err:
            logger.exception(err)
