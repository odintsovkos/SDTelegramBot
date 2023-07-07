import asyncio
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, KeyboardButton

from settings.bot_config import ADMINS
from keyboards.default import keyboards
from loader import dp
from states.all_states import SDStates
from utils.db_services import db_service
from utils.misc_func import create_samplers_keyboard, is_sd_launched, restart_sd, check_sd_path
from utils.sd_api import api_service


@dp.message_handler(Text(equals="~Назад~"), state=[SDStates.settings, SDStates.settings_set_n_prompt,
                                                   SDStates.settings_set_sampler, SDStates.settings_set_steps,
                                                   SDStates.settings_set_wh, SDStates.settings_set_cfg_scale,
                                                   SDStates.settings_set_restore_face,
                                                   SDStates.settings_set_batch_count])
async def cancel_button_handler(message: Message, state: FSMContext):

    if await state.get_state() == SDStates.settings.state:
        await message.answer("Действие отменено", reply_markup=keyboards.main_menu)
        await SDStates.enter_prompt.set()
    else:
        await message.answer("Действие отменено", reply_markup=keyboards.settings)
        await SDStates.settings.set()


@dp.message_handler(commands=["settings"], state=SDStates.enter_prompt)
async def settings_command_handler(message: Message):
    if str(message.from_user.id) in ADMINS and keyboards.settings.keyboard[-1][0].text != "Перезапуск SD":
        keyboards.settings.add(KeyboardButton(text="Перезапуск SD"))
    await message.answer("Настройки генерации", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings, content_types=types.ContentTypes.TEXT)
async def settings_buttons_handler(message: types.Message, state: FSMContext):
    if message.text == "Negative Prompt":
        await message.answer(f"Напиши Negative prompt", reply_markup=keyboards.cancel)
        await SDStates.settings_set_n_prompt.set()
    elif message.text == "Sampler":
        await message.answer(f"Выбери Sampler", reply_markup=await create_samplers_keyboard())
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
        await message.answer(f"Включить Restore face? 1/0", reply_markup=keyboards.cancel)
        await SDStates.settings_set_restore_face.set()
    elif message.text == "Batch count":
        await message.answer(f"Укажи Batch count (MAX 8)", reply_markup=keyboards.cancel)
        await SDStates.settings_set_batch_count.set()
    elif message.text == "Текущие настройки":
        db_result = await db_service.db_get_sd_settings(message.from_user.id)
        await message.answer(f"Model:\n"
                             f"{db_result[1]}\n"
                             f"------------------------------------\n"
                             f"Style:\n"
                             f"{db_result[2].replace('&', ', ')}\n"
                             f"------------------------------------\n"
                             f"Lora:\n"
                             f"{db_result[3].replace('&', ', ')}\n"
                             f"------------------------------------\n"
                             f"Negative Prompt:\n"
                             f"{db_result[4]}\n"
                             f"------------------------------------\n"
                             f"Sampler:\n"
                             f"{db_result[5]}\n"
                             f"------------------------------------\n"
                             f"Steps: {db_result[6]}\n"
                             f"------------------------------------\n"
                             f"Width x Height: {db_result[7]}\n"
                             f"------------------------------------\n"
                             f"CFG Scale: {db_result[8]}\n"
                             f"------------------------------------\n"
                             f"Restore face: {'On' if db_result[9] == 1 else 'Off'}\n"
                             f"------------------------------------\n"
                             f"Batch count: {db_result[10]}", reply_markup=keyboards.settings)
    elif message.text == "Сброс настроек":
        await db_service.db_update_default_settings(message.from_user.id)
        await message.answer('Настройки сброшены', reply_markup=keyboards.settings)
    elif message.text == "Перезапуск SD":
        if check_sd_path():
            start_time = time.time()
            await message.answer("Перезапуск SD начат...")
            await restart_sd()
            while True:
                if is_sd_launched():
                    current_time = time.time()
                    await message.answer(f"Перезапуск SD завершен\nВремя ожидания: {round(current_time - start_time)}s.", reply_markup=keyboards.main_menu)
                    await SDStates.enter_prompt.set()
                    break
                else:
                    await asyncio.sleep(1)
        else:
            await message.answer("Перезапуск SD невозможен, ошибка в пути к папке SD", reply_markup=keyboards.main_menu)


@dp.message_handler(state=SDStates.settings_set_n_prompt, content_types=types.ContentTypes.TEXT)
async def nprompt_button_handler(message: Message, state: FSMContext):
    await state.finish()
    await db_service.db_set_sd_settings(message.from_user.id, "sd_n_prompt", message.text)
    await message.answer("Negative prompt установлен", reply_markup=keyboards.settings)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_sampler, content_types=types.ContentTypes.TEXT)
async def sampler_button_handler(message: Message):
    api_result = api_service.get_request_sd_api('samplers').json()
    sampler_in_list = False
    for sampler in api_result:
        if message.text == sampler['name']:
            sampler_in_list = True
    if sampler_in_list:
        await db_service.db_set_sd_settings(message.from_user.id, "sd_sampler", message.text)
        await message.answer("Sampler установлен", reply_markup=keyboards.settings)
        await SDStates.settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.settings)


@dp.message_handler(state=SDStates.settings_set_steps, content_types=types.ContentTypes.TEXT)
async def steps_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_steps", int(message.text))
        await message.answer("Количество шагов задано", reply_markup=keyboards.settings)
        await SDStates.settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.settings_set_wh, content_types=types.ContentTypes.TEXT)
async def wh_button_handler(message: Message):
    if message.text.find('x'):
        message_list = message.text.split('x')
        if len(message_list) == 2 and message_list[0].isdigit() and message_list[1].isdigit():
            await db_service.db_set_sd_settings(message.from_user.id, "sd_width_height", message.text)
            await message.answer("Высота и ширина заданы", reply_markup=keyboards.settings)
            await SDStates.settings.set()
        else:
            await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.settings_set_cfg_scale, content_types=types.ContentTypes.TEXT)
async def cfg_scale_button_handler(message: Message):
    try:
        await db_service.db_set_sd_settings(message.from_user.id, "sd_cfg_scale", float(message.text))
        await message.answer("CFG Scale задан", reply_markup=keyboards.settings)
        await SDStates.settings.set()
    except ValueError:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.settings_set_restore_face, content_types=types.ContentTypes.TEXT)
async def restore_face_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_restore_face", int(message.text))
        if message.text == '1':
            await message.answer("Restore face включен", reply_markup=keyboards.settings)
        elif message.text == '0':
            await message.answer("Restore face выключен", reply_markup=keyboards.settings)
        else:
            await message.answer("Ошибка ввода", reply_markup=keyboards.settings)
        await SDStates.settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.settings_set_batch_count, content_types=types.ContentTypes.TEXT)
async def batch_count_button_handler(message: Message):
    if message.text.isdigit():
        if 1 <= int(message.text) <= 8:
            await db_service.db_set_sd_settings(message.from_user.id, "sd_batch_count", int(message.text))
            await message.answer("Batch count задан", reply_markup=keyboards.settings)
            await SDStates.settings.set()
        else:
            await message.answer("Batch count должен быть от 1 до 8", reply_markup=keyboards.cancel)
    else:
        await message.answer("Введите число", reply_markup=keyboards.cancel)
