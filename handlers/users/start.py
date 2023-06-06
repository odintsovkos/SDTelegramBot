from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default import keyboards
from loader import dp
from states.all_states import SDStates
from utils.db_services import db_get_service
from utils.db_services.db_set_service import db_create_new_user_settings


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")
    await message.answer(f"Я генерирую фото по любому тексту...", reply_markup=keyboards.main_menu)
    if db_get_service.db_get_sd_settings(message.from_user.id) is None:
        db_create_new_user_settings(message.from_user.id)
    else:
        print(f"User {message.from_user.id} added to DB")
    await SDStates.enter_prompt.set()
