import base64
import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, KeyboardButton

from handlers.users.settings import create_keyboard
from loader import dp
from states.all_states import SDStates
from keyboards.default import keyboards
from utils.db_services.db_get_service import db_get_sd_setting
from utils.db_services.db_set_service import db_set_sd_settings
from utils.misc_func import set_params, change_sd_model
from utils.sd_api import api_service

last_prompt = ""


@dp.message_handler(Text(equals="Ещё раз"), state="*")
async def cancel_menu(message: Message, state: FSMContext):
    if last_prompt == "":
        await message.answer("Введи Prompt")
    else:
        await send_photo(message, last_prompt)


@dp.message_handler(Text(equals="Модель"), state=SDStates.enter_prompt)
async def cancel_menu(message: Message, state: FSMContext):
    sd_model = api_service.get_request_sd_api("options").json()['sd_model_checkpoint']
    model_keyb = create_keyboard('sd-models', 'title')
    await message.answer(f"Текущая модель:\n{sd_model}", reply_markup=model_keyb)
    await SDStates.settings_set_model.set()


@dp.message_handler(state=SDStates.settings_set_model, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, 'sd_model', message.text)
    change_sd_model(message.from_user.id)
    await message.answer("Модель загружена", reply_markup=keyboards.main_menu)
    await SDStates.enter_prompt.set()


@dp.message_handler(Text(equals="Стиль"), state=SDStates.enter_prompt)
async def cancel_menu(message: Message, state: FSMContext):
    style_keyb = create_keyboard('prompt-styles', 'name')
    style_keyb.add(KeyboardButton(text="Убрать стиль"))
    await message.answer(f"Выбери стиль", reply_markup=style_keyb)
    await SDStates.settings_set_style.set()


@dp.message_handler(state=SDStates.settings_set_style, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    if message.text == "Убрать стиль":
        db_set_sd_settings(message.from_user.id, "sd_style", "")
        await message.answer("Стиль убран", reply_markup=keyboards.main_menu)
    else:
        db_set_sd_settings(message.from_user.id, "sd_style", message.text)
        await message.answer("Новый стиль установлен", reply_markup=keyboards.main_menu)
    await SDStates.enter_prompt.set()


@dp.message_handler(state=SDStates.enter_prompt, content_types=types.ContentTypes.TEXT)
async def answer_from_location(message: types.Message, state: FSMContext):
    global last_prompt
    last_prompt = message['text']
    await send_photo(message, last_prompt)


async def send_photo(message, prompt):
    sd_model = change_sd_model(message.from_user.id)
    response = set_params(message.from_user.id, prompt)
    style = db_get_sd_setting(message.from_user.id, 'sd_style')
    caption = f"Prompt:\n{prompt}\nModel:\n{sd_model}\nStyle: {'Не задан' if style[0] == '' else style[0]}"

    r = response.json()

    media = types.MediaGroup()
    if len(r['images']) > 1:
        try:
            for i in r['images']:
                image = types.InputFile(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                media.attach_photo(image)
            await message.answer_media_group(media=media)
            await message.answer(caption, reply_markup=keyboards.main_menu)
        except Exception:
            await message.answer("Ошибка генерации, проверь SD!")
    else:
        for i in r['images']:
            image = types.InputFile(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            await message.answer_photo(photo=image)
            await message.answer(caption, reply_markup=keyboards.main_menu)
