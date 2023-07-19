"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""
import asyncio
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils import markdown

import settings.string_variables as str_var
from keyboards.inline.inline_menu import settings_menu, gen_settings_menu, create_samplers_inline_keyboard, \
    inline_cancel, wh_create_keyboards, hires_menu, main_menu
from loader import dp
from settings.bot_config import ADMINS
from states.all_states import SDStates
from utils.db_services import db_service
from utils.misc_func import check_sd_path, restart_sd, is_sd_launched

callback_data = None


@dp.message_handler(commands=["settings"], state=SDStates.enter_prompt)
async def settings_command_handler(message: Message):
    await message.bot.delete_message(message.chat.id, message.message_id)
    if str(message.from_user.id) in ADMINS and settings_menu.inline_keyboard[-1][0].text != str_var.restart_sd:
        settings_menu.add(InlineKeyboardButton(text=str_var.restart_sd, callback_data="restart_sd"))
    await message.answer("⚙️ Настройки", reply_markup=settings_menu)
    await SDStates.settings.set()


@dp.message_handler(state=SDStates.settings_set_n_prompt, content_types=types.ContentTypes.TEXT)
async def nprompt_button_handler(message: Message, state: FSMContext):
    await state.finish()
    await db_service.db_set_sd_settings(message.from_user.id, "sd_n_prompt", message.text)
    await callback_data.message.edit_text("Negative Prompt установлен", reply_markup=gen_settings_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.gen_settings.set()


@dp.message_handler(state=SDStates.settings_set_steps, content_types=types.ContentTypes.TEXT)
async def steps_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_steps", int(message.text))
        await callback_data.message.edit_text("Количество шагов задано", reply_markup=gen_settings_menu)
        await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await SDStates.gen_settings.set()
    else:
        await callback_data.message.edit_text("Ошибка ввода", reply_markup=inline_cancel)


@dp.message_handler(state=SDStates.settings_set_cfg_scale, content_types=types.ContentTypes.TEXT)
async def cfg_scale_button_handler(message: Message):
    try:
        await db_service.db_set_sd_settings(message.from_user.id, "sd_cfg_scale", float(message.text))
        await callback_data.message.edit_text("CFG Scale задан", reply_markup=gen_settings_menu)
        await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await SDStates.gen_settings.set()
    except ValueError:
        await callback_data.message.edit_text("Ошибка ввода", reply_markup=inline_cancel)


@dp.message_handler(state=SDStates.settings_set_batch_count, content_types=types.ContentTypes.TEXT)
async def batch_count_button_handler(message: Message):
    if message.text.isdigit():
        if 1 <= int(message.text) <= 8:
            await db_service.db_set_sd_settings(message.from_user.id, "sd_batch_count", int(message.text))
            await callback_data.message.edit_text("Batch count задан", reply_markup=gen_settings_menu)
            await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            await SDStates.gen_settings.set()
        else:
            await callback_data.message.edit_text("Batch count должен быть от 1 до 8", reply_markup=inline_cancel)
    else:
        await callback_data.message.edit_text("Введите число", reply_markup=inline_cancel)


@dp.callback_query_handler(state=SDStates.settings, text='current_settings')
async def current_settings(callback: types.CallbackQuery):
    db_result = await db_service.db_get_sd_settings(callback.from_user.id)
    current_model = markdown.hbold("Model: ") + markdown.hitalic(db_result[1])
    current_style = markdown.hbold("\nStyle:\n") + markdown.hitalic(db_result[2].replace('&', ', ')) if db_result[
                                                                                                            2] != '' else ""
    current_lora = markdown.hbold("\nLoRa:\n") + markdown.hitalic(db_result[3].replace('&', ', ')) if db_result[
                                                                                                          3] != '' else ""
    current_n_prompt = markdown.hbold("\nNegative Prompt:\n") + markdown.hitalic(db_result[4])
    current_sampler = markdown.hbold("\nSampler: ") + markdown.hitalic(db_result[5])
    current_steps = markdown.hbold("\nSteps: ") + markdown.hitalic(db_result[6])
    current_wh = markdown.hbold("\nWidth x Height: ") + markdown.hitalic(db_result[7])
    current_cfg_scale = markdown.hbold("\nCFG Scale: ") + markdown.hitalic(db_result[8])
    current_batch_count = markdown.hbold("\nBatch count: ") + markdown.hitalic(db_result[9])
    current_settings = current_model + current_style + current_lora + current_n_prompt + current_sampler + \
                       current_steps + current_wh + current_cfg_scale + current_batch_count
    hires_settings = markdown.hbold("\nHires: ") + markdown.hitalic("Включен" if db_result[10] == 1 else "Отключен") + \
                     markdown.hbold("\nHires Upscaler: ") + markdown.hitalic(db_result[11]) + \
                     markdown.hbold("\nHires Steps: ") + markdown.hitalic(db_result[12]) + \
                     markdown.hbold("\nHires Denoising Strength: ") + markdown.hitalic(db_result[13]) + \
                     markdown.hbold("\nHires Upscale by: ") + markdown.hitalic(db_result[14])

    await callback.message.edit_text(current_settings + hires_settings if db_result[10] == 1 else current_settings,
                                     reply_markup=settings_menu)


@dp.callback_query_handler(state=[SDStates.settings, SDStates.gen_settings], text='cancel')
async def generation_settings(callback: types.CallbackQuery, state: FSMContext):
    if await state.get_state() == SDStates.gen_settings.state:
        await callback.message.edit_text("⚙️ Настройки", reply_markup=settings_menu)
        await SDStates.settings.set()
    elif await state.get_state() == SDStates.settings.state:
        await callback.message.edit_text("📖 Меню генерации", reply_markup=main_menu)
        await SDStates.enter_prompt.set()


@dp.callback_query_handler(state=[SDStates.settings_set_steps,
                                  SDStates.settings_set_n_prompt,
                                  SDStates.settings_set_wh,
                                  SDStates.settings_set_cfg_scale,
                                  SDStates.settings_set_batch_count,
                                  SDStates.settings_set_sampler], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Настройки генерации", reply_markup=gen_settings_menu)
    await SDStates.gen_settings.set()


@dp.callback_query_handler(state=SDStates.settings, text='gen_settings')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Настройки генерации", reply_markup=gen_settings_menu)
    await SDStates.gen_settings.set()


@dp.callback_query_handler(state=SDStates.settings, text='hr_settings')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Настройки Hires Fix", reply_markup=hires_menu)
    await SDStates.hr_settings.set()


@dp.callback_query_handler(state=SDStates.gen_settings, text='negative_prompt')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(
        f"<b>Текущий Negative Prompt:</b>\n<code>{current_settings['sd_n_prompt']}</code>\n"
        f"✏️ Напиши Negative prompt", reply_markup=inline_cancel)
    await SDStates.settings_set_n_prompt.set()


@dp.callback_query_handler(state=SDStates.gen_settings, text='sampler')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    sample_keyboard = await create_samplers_inline_keyboard()
    await callback.message.edit_text(f"<b>Текущий Sampler:</b>\n <i>{current_settings['sd_sampler']}</i>\n"
                                     f"✏️ Выбери Sampler", reply_markup=sample_keyboard)
    await SDStates.settings_set_sampler.set()


@dp.callback_query_handler(state=SDStates.gen_settings, text='steps')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"<b>Текущий Steps:</b>\n <i>{current_settings['sd_steps']}</i>\n"
                                     f"✏️ Введи количество шагов генерации", reply_markup=inline_cancel)
    await SDStates.settings_set_steps.set()


@dp.callback_query_handler(state=SDStates.gen_settings, text='width_height')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    width_height_keyboard = wh_create_keyboards()
    await callback.message.edit_text(f"<b>Текущие Width x Height:</b>\n <i>{current_settings['sd_width_height']}</i>\n"
                                     f"✏️ Введи ширину и высоту, через 'x'", reply_markup=width_height_keyboard)
    await SDStates.settings_set_wh.set()


@dp.callback_query_handler(state=SDStates.gen_settings, text='cfg_scale')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"<b>Текущий CFG Scale:</b>\n <i>{current_settings['sd_cfg_scale']}</i>\n"
                                     f"✏️ Введи CFG Scale (дробное число, через точку)", reply_markup=inline_cancel)
    await SDStates.settings_set_cfg_scale.set()


@dp.callback_query_handler(state=SDStates.gen_settings, text='batch_count')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"<b>Текущий Batch count:</b>\n <i>{current_settings['sd_batch_count']}</i>\n"
                                     f"✏️ Введи Batch count (MAX 8)", reply_markup=inline_cancel)
    await SDStates.settings_set_batch_count.set()


@dp.callback_query_handler(Text(startswith="wh_"), state=SDStates.settings_set_wh)
async def current_settings(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    await db_service.db_set_sd_settings(callback.from_user.id, "sd_width_height", action)
    await callback.message.edit_text(f"<b>Width x Height задан</b>", reply_markup=gen_settings_menu)
    await SDStates.gen_settings.set()


@dp.callback_query_handler(Text(startswith="sampler_"), state=SDStates.settings_set_sampler)
async def current_settings(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    await db_service.db_set_sd_settings(callback.from_user.id, "sd_sampler", action)
    await callback.message.edit_text(f"<b>Sampler \"{action}\" задан</b>", reply_markup=gen_settings_menu)
    await SDStates.gen_settings.set()


@dp.callback_query_handler(state=SDStates.settings, text='reset_settings')
async def current_settings(callback: types.CallbackQuery):
    await db_service.db_update_default_settings(callback.from_user.id)
    await callback.message.edit_text('🛠 Настройки сброшены', reply_markup=settings_menu)


@dp.callback_query_handler(state=SDStates.settings, text='restart_sd')
async def current_settings(callback: types.CallbackQuery):
    if check_sd_path():
        start_time = time.time()
        await callback.message.edit_text("Перезапуск SD начат...")
        await restart_sd()
        while True:
            if is_sd_launched():
                current_time = time.time()
                await callback.message.answer(
                    f"❕ Перезапуск SD завершен\nВремя ожидания: {round(current_time - start_time)}s.",
                    reply_markup=main_menu)
                await SDStates.enter_prompt.set()
                break
            else:
                await asyncio.sleep(1)
    else:
        await callback.message.edit_text("⛔️ Перезапуск SD невозможен, ошибка в пути к папке SD",
                                         reply_markup=main_menu)
        await SDStates.enter_prompt.set()
