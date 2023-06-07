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
from utils.misc_func import set_params, change_sd_model, create_style_keyboard, change_style_db
from utils.sd_api import api_service

last_prompt = ""


@dp.message_handler(Text(equals="Ещё раз"), state="*")
async def re_generation_button_handler(message: Message, state: FSMContext):
    if last_prompt == "":
        await message.answer("Введи Prompt")
    else:
        await send_photo(message, last_prompt)


@dp.message_handler(Text(equals="Модель"), state=SDStates.enter_prompt)
async def model_button_handler(message: Message):
    sd_model = api_service.get_request_sd_api("options").json()['sd_model_checkpoint']
    models_keyboard = create_keyboard('sd-models', 'title')
    await message.answer(f"Текущая модель:\n{sd_model}", reply_markup=models_keyboard)
    await SDStates.settings_set_model.set()


@dp.message_handler(state=SDStates.settings_set_model, content_types=types.ContentTypes.TEXT)
async def change_model_handler(message: Message):
    db_set_sd_settings(message.from_user.id, 'sd_model', message.text)
    change_sd_model(message.from_user.id)
    await message.answer("Модель загружена", reply_markup=keyboards.main_menu)
    await SDStates.enter_prompt.set()


@dp.message_handler(Text(equals="Стиль"), state=SDStates.enter_prompt)
async def style_button_handler(message: Message):
    styles_keyboard = create_style_keyboard(message.from_user.id)
    await message.answer(f"Выбери стили", reply_markup=styles_keyboard)
    await SDStates.settings_set_style.set()


@dp.message_handler(state=SDStates.settings_set_style, content_types=types.ContentTypes.TEXT)
async def change_style_handler(message: Message):
    if message.text == "~Назад~":
        await message.answer("Действие отменено", reply_markup=keyboards.main_menu)
        await SDStates.enter_prompt.set()
    elif message.text == "~Подтвердить~":
        await message.answer("Стили установлены", reply_markup=keyboards.main_menu)
        await SDStates.enter_prompt.set()
    elif message.text == "~Отключить все стили~":
        await message.answer("Стили отключены", reply_markup=keyboards.main_menu)
        db_set_sd_settings(message.from_user.id, "sd_style", "")
        await SDStates.enter_prompt.set()
    else:
        text_style = message.text
        if message.text[0] == '>':
            text_style = message.text[3:]
        is_changed = change_style_db(message.from_user.id, text_style)
        styles_keyboard = create_style_keyboard(message.from_user.id)
        await message.answer(f"Стиль {text_style} {'установлен' if is_changed else 'отключен'}", reply_markup=styles_keyboard)


@dp.message_handler(state=SDStates.enter_prompt, content_types=types.ContentTypes.TEXT)
async def entered_prompt_handler(message: types.Message):
    global last_prompt
    last_prompt = message['text']
    await send_photo(message, last_prompt)


async def send_photo(message, prompt):
    sd_model = change_sd_model(message.from_user.id)
    response = set_params(message.from_user.id, prompt)
    style = db_get_sd_setting(message.from_user.id, 'sd_style')
    caption = f"Prompt:\n{prompt}\nModel:\n{sd_model}\nStyle: {'Не задан' if style == '' else style.replace('&', ', ')}"

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
