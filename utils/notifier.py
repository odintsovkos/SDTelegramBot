import logging

from aiogram import Dispatcher

from settings.bot_config import ADMINS, USERS


async def admin_notify(dp: Dispatcher, msg: str):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, msg)

        except Exception as err:
            logging.exception(err)


async def user_notify(dp: Dispatcher, msg: str):
    for user in USERS:
        try:
            await dp.bot.send_message(user, msg)

        except Exception as err:
            logging.exception(err)


async def users_and_admins_notify(dp: Dispatcher, msg: str):
    await user_notify(dp, msg)
    await admin_notify(dp, msg)
