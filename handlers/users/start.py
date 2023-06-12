from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default import keyboards
from loader import dp
from states.all_states import SDStates
from utils.db_services import db_service


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    db_users_response = await db_service.db_get_sd_setting(message.from_user.id, 'tg_id')
    if message.from_user.id == db_users_response:
        await message.answer(f"Привет, {message.from_user.full_name}!")
        await message.answer(f"Я генерирую фото по любому тексту...", reply_markup=keyboards.main_menu)
        await SDStates.enter_prompt.set()
    else:
        await message.answer(f"Привет, {message.from_user.full_name}!")
        await message.answer("Бот тебя не знает, хочешь отправить заявку на доступ к функциям бота?",
                             reply_markup=keyboards.auth_menu)
        await SDStates.waiting_for_authorization.set()
