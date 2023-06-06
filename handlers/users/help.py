from aiogram import types
from aiogram.dispatcher.filters import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp(), state='*')
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать генерировать",
            "/settings - Настройки генерации",
            "/help - Справка")

    await message.answer("\n".join(text))
