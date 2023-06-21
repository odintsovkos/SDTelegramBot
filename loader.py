import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

from data import config
from utils.db_services import db_service


async def user_verification(admins, users):
    db_users = list(x['tg_id'] for x in await db_service.db_get_all_tg_id())
    for db_user in db_users:
        if str(db_user) not in admins and str(db_user) not in users:
            print("Delete user:", db_user)
            await db_service.db_delete_user(db_user)


async def admins_and_users_initialization_in_db():
    from data.config import ADMINS
    from data.config import USERS
    await user_verification(ADMINS, USERS)
    for admin in ADMINS:
        try:
            await db_service.db_create_new_user_settings(admin)
            print("Create new admin:", admin)
        except sqlite3.IntegrityError:
            continue

    for user in USERS:
        try:
            await db_service.db_create_new_user_settings(user)
            print("Create new user:", user)
        except sqlite3.IntegrityError:
            continue


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
loop.run_until_complete(db_service.db_create_table())
loop.run_until_complete(admins_and_users_initialization_in_db())

logging.basicConfig(level=logging.DEBUG)



