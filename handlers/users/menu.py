import asyncio
import threading

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import settings.string_variables as str_var
from keyboards.default import keyboards
from keyboards.default.keyboards import create_model_keyboard, create_lora_keyboard, create_style_keyboard
from loader import dp
from states.all_states import SDStates
from utils.db_services import db_service
from utils.misc_func import change_style_db, change_lora_db, send_photo, change_model_callback, restart_sd, \
    restarting_sd, is_sd_launched, message_parse
from utils.waiting_bar import waiting_bar

last_prompt = ""
response_list = []


@dp.message_handler(Text(equals=str_var.cancel), state=[SDStates.settings_set_model, SDStates.settings_set_style,
                                                        SDStates.settings_set_lora])
async def cancel_button_handler(message: Message):
    await message.answer("🖥 Главное меню", reply_markup=keyboards.main_menu)
    await SDStates.enter_prompt.set()


@dp.message_handler(Text(equals=str_var.repeat), state=[SDStates.enter_prompt])
async def re_generation_button_handler(message: Message):
    if last_prompt == "":
        await message.answer("✏️ Введи Prompt")
    else:
        if is_sd_launched():
            await send_photo(message, last_prompt, response_list)
        else:
            await restarting_sd(message)
            await asyncio.sleep(2)
            await send_photo(message, last_prompt, response_list)


@dp.message_handler(Text(equals=str_var.model), state=SDStates.enter_prompt)
async def model_button_handler(message: Message):
    sd_model = await db_service.db_get_sd_setting(message.from_user.id, "sd_model")
    models_keyboard = create_model_keyboard('sd-models', 'model_name')
    await message.answer(f"<b>Текущая модель:</b>\n<i>{sd_model}</i>\n"
                         f"👇🏻 Выбери новую модель...", reply_markup=models_keyboard)
    await SDStates.settings_set_model.set()


@dp.message_handler(state=SDStates.settings_set_model, content_types=types.ContentTypes.TEXT)
async def change_model_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, 'sd_model', message.text)
    thread_change_model = threading.Thread(target=change_model_callback, args=(message.from_user.id, response_list))
    thread_change_model.start()
    chat_id, message_id = await waiting_bar(message.chat.id, thread_change_model)
    thread_change_model.join()
    await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
    await message.answer(text=f"✅ Модель загружена", reply_markup=keyboards.main_menu)
    response_list.clear()
    await SDStates.enter_prompt.set()


@dp.message_handler(Text(equals=str_var.loras), state=SDStates.enter_prompt)
async def lora_button_handler(message: Message):
    lora_keyboard = await create_lora_keyboard(message.from_user.id)
    await message.answer(f"Выбери LoRa:", reply_markup=lora_keyboard)
    await SDStates.settings_set_lora.set()


@dp.message_handler(state=SDStates.settings_set_lora, content_types=types.ContentTypes.TEXT)
async def change_lora_handler(message: Message):
    if message.text == str_var.confirm:
        await message.answer("📝 Lora установлены", reply_markup=keyboards.main_menu)
        await SDStates.enter_prompt.set()
    elif message.text == str_var.disable_all_loras:
        await message.answer("📝 Все Lora отключены", reply_markup=keyboards.main_menu)
        await db_service.db_set_sd_settings(message.from_user.id, "sd_lora", "")
        await SDStates.enter_prompt.set()
    else:
        text_lora = message.text
        if message.text[0] == '>':
            text_lora = message.text[3:]
        is_changed = await change_lora_db(message.from_user.id, text_lora)
        lora_keyboard = await create_lora_keyboard(message.from_user.id)
        await message.answer(f"Lora {text_lora} {'установлена' if is_changed else 'отключена'}",
                             reply_markup=lora_keyboard)


@dp.message_handler(Text(equals=str_var.styles), state=SDStates.enter_prompt)
async def style_button_handler(message: Message):
    styles_keyboard = await create_style_keyboard(message.from_user.id)
    await message.answer(f"Выбери стили", reply_markup=styles_keyboard)
    await SDStates.settings_set_style.set()


@dp.message_handler(state=SDStates.settings_set_style, content_types=types.ContentTypes.TEXT)
async def change_style_handler(message: Message):
    if message.text == str_var.confirm:
        await message.answer("📝 Стили установлены", reply_markup=keyboards.main_menu)
        await SDStates.enter_prompt.set()
    elif message.text == str_var.disable_all_styles:
        await message.answer("📝 Стили отключены", reply_markup=keyboards.main_menu)
        await db_service.db_set_sd_settings(message.from_user.id, "sd_style", "")
        await SDStates.enter_prompt.set()
    else:
        text_style = message.text
        if message.text[0] == '>':
            text_style = message.text[3:]
        is_changed = await change_style_db(message.from_user.id, text_style)
        styles_keyboard = await create_style_keyboard(message.from_user.id)
        await message.answer(f"Стиль {text_style} {'установлен' if is_changed else 'отключен'}",
                             reply_markup=styles_keyboard)


@dp.message_handler(state=SDStates.enter_prompt, content_types=types.ContentTypes.TEXT)
async def entered_prompt_handler(message: types.Message):
    global last_prompt
    last_prompt = message['text']
    if is_sd_launched():
        await send_photo(message, last_prompt, response_list)
    else:
        await restarting_sd(message)
        await asyncio.sleep(2)
        await send_photo(message, last_prompt, response_list)
