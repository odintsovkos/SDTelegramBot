import logging

from aiogram import Dispatcher

from data.config import ADMINS


async def admin_notify(dp: Dispatcher, msg: str):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, msg)

        except Exception as err:
            logging.exception(err)
