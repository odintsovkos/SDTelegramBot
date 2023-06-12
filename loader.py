import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

from data import config
from utils.db_services import db_service

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
loop.run_until_complete(db_service.db_create_table())


logging.basicConfig(level=logging.DEBUG)
