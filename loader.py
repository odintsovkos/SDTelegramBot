from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from settings import bot_config
from utils.misc.logging import ColoredLogger


bot = Bot(token=bot_config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)
logging.setLoggerClass(ColoredLogger)
