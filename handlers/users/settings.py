from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from loader import dp
from states.all_states import SDStates
from keyboards.default import keyboards
from utils.db_services.db_get_service import db_get_sd_settings
from utils.db_services.db_set_service import db_set_sd_settings, db_update_default_settings
from utils.sd_api import api_service


@dp.message_handler(Text(equals="Назад"), state=SDStates.settings)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=keyboards.main_menu)
    await SDStates.enter_prompt.set()


@dp.message_handler(commands=["settings"], state=SDStates.enter_prompt)
async def settings_command_handler(message: Message, state: FSMContext):
    await message.answer("Настройки генерации", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings, content_types=types.ContentTypes.TEXT)
async def answer_from_location(message: types.Message, state: FSMContext):
    if message.text == "Negative Prompt":
        await message.answer(f"Напиши Negative prompt", reply_markup=keyboards.cancel)
        await SDStates.settings_set_n_prompt.set()
    elif message.text == "Sampler":
        sampler_keyb = create_keyboard('samplers', 'name')
        await message.answer(f"Выбери Sampler", reply_markup=sampler_keyb)
        await SDStates.settings_set_sampler.set()
    elif message.text == "Steps":
        await message.answer(f"Введи количество шагов генерации", reply_markup=keyboards.cancel)
        await SDStates.settings_set_steps.set()
    elif message.text == "Width & Height":
        await message.answer(f"Введи ширину и высоту, через 'x'", reply_markup=keyboards.cancel)
        await SDStates.settings_set_wh.set()
    elif message.text == "CFG Scale":
        await message.answer(f"Введи CFG Scale (дробное число, через точку)", reply_markup=keyboards.cancel)
        await SDStates.settings_set_cfg_scale.set()
    elif message.text == "Restore face":
        await message.answer(f"Включить Restore face? Y/N", reply_markup=keyboards.cancel)
        await SDStates.settings_set_restore_face.set()
    elif message.text == "Batch count":
        await message.answer(f"Укажи Batch count (MAX 8)", reply_markup=keyboards.cancel)
        await SDStates.settings_set_batch_count.set()
    elif message.text == "Текущие настройки":
        db_result = db_get_sd_settings(message.from_user.id)
        await message.answer(f"Model:\n"
                             f"{db_result[1]}\n"
                             f"Style:\n"
                             f"{db_result[2]}\n"
                             f"Negative Prompt:\n"
                             f"{db_result[3]}\n"
                             f"Sampler:\n"
                             f"{db_result[4]}\n"
                             f"Steps: {db_result[5]}\n"
                             f"Width x Height: {db_result[6]}\n"
                             f"CFG Scale: {db_result[7]}\n"
                             f"Restore face: {'On' if db_result[8] == 1 else 'Off'}\n"
                             f"Batch count: {db_result[9]}", reply_markup=keyboards.settings)
    elif message.text == "Сброс настроек":
        db_update_default_settings(message.from_user.id)
        await message.answer('Настройки сброшены', reply_markup=keyboards.settings)


@dp.message_handler(state=SDStates.settings_set_n_prompt, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_n_prompt", message.text)
    await message.answer("Negative prompt установлен", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_sampler, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_sampler", message.text)
    await message.answer("Sampler установлен", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_steps, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_steps", int(message.text))
    await message.answer("Количество шагов задано", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_wh, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_width_height", message.text)
    await message.answer("Высота и ширина заданы", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_cfg_scale, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_cfg_scale", int(message.text))
    await message.answer("CFG Scale задан", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_restore_face, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_restore_face", int(message.text))
    if message.text == 1:
        await message.answer("Restore face включен", reply_markup=keyboards.settings)
    elif message.text == 0:
        await message.answer("Restore face выключен", reply_markup=keyboards.settings)
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_batch_count, content_types=types.ContentTypes.TEXT)
async def cancel_menu(message: Message, state: FSMContext):
    await state.finish()
    db_set_sd_settings(message.from_user.id, "sd_batch_count", int(message.text))
    await message.answer("Batch count задан", reply_markup=keyboards.settings)
    await SDStates.settings.set()


def create_keyboard(endpoint, txt):
    result_models = api_service.get_request_sd_api(endpoint).json()
    inline_kb_full = ReplyKeyboardMarkup()
    inline_kb_full.add(KeyboardButton(text="Отмена"))
    for i in result_models:
        inline_kb_full.add(KeyboardButton(text=i[txt]))
    return inline_kb_full
