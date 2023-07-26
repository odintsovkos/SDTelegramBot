"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import settings.string_variables as str_var
from keyboards.default import keyboards
from keyboards.inline.inline_menu import inline_cancel, create_hr_upscalers_keyboard, hires_menu, settings_menu
from loader import dp
from states.all_states import SDStates
from utils.db_services import db_service

callback_data = None


@dp.message_handler(state=SDStates.hr_settings, content_types=types.ContentTypes.TEXT)
async def settings_buttons_handler(message: types.Message):
    current_settings = await db_service.db_get_sd_settings(message.from_user.id)
    if message.text == str_var.hr_on_off:
        await message.answer(f"Текущее состояние: "
                             f"Hires - {'Включен' if current_settings['sd_hr_on_off'] == 1 else 'Отключен'}\n"
                             f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=keyboards.cancel)
        await SDStates.hr_set_on_off.set()


@dp.callback_query_handler(state=[SDStates.hr_settings], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Настройки", reply_markup=settings_menu)
    await SDStates.settings.set()


@dp.callback_query_handler(state=[SDStates.hr_set_on_off,
                                  SDStates.hr_change_upscaler,
                                  SDStates.settings_set_wh,
                                  SDStates.hr_set_upscale_by,
                                  SDStates.hr_set_steps,
                                  SDStates.hr_set_denoising_strength], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Настройки Hires Fix", reply_markup=hires_menu)
    await SDStates.hr_settings.set()


@dp.message_handler(state=SDStates.hr_set_on_off, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_on_off", message.text)
    await callback_data.message.edit_text(f"Hires - {'Включен' if int(message.text) == 1 else 'Отключен'}", reply_markup=hires_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.hr_settings.set()


@dp.message_handler(state=SDStates.hr_set_steps, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_steps", message.text)
        await callback_data.message.edit_text("Steps установлен", reply_markup=hires_menu)
        await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await SDStates.hr_settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.hr_set_denoising_strength, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    try:
        await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_denoising_strength", float(message.text))
        await callback_data.message.edit_text("Denoising strength установлен", reply_markup=hires_menu)
        await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await SDStates.hr_settings.set()
    except ValueError:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.hr_set_upscale_by, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_upscale_by", message.text)
        await callback_data.message.edit_text("Upscale by установлен", reply_markup=hires_menu)
        await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await SDStates.hr_settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.callback_query_handler(state=SDStates.hr_settings, text='hr_on_off')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее состояние: "
                                     f"Hires - {'Включен' if current_settings['sd_hr_on_off'] == 1 else 'Отключен'}\n"
                                     f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=inline_cancel)
    await SDStates.hr_set_on_off.set()


@dp.callback_query_handler(state=SDStates.hr_settings, text='hr_upscaler')
async def current_settings(callback: types.CallbackQuery, state: FSMContext):
    global callback_data
    callback_data = callback
    await state.update_data(current_page=0)
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    upscaler_keyboard = await create_hr_upscalers_keyboard(state)
    await callback.message.edit_text(f"Текущий Upscaler: "
                                     f"{current_settings['sd_hr_upscaler']}\n"
                                     f"✏️ Выбери Upscaler", reply_markup=upscaler_keyboard)
    await SDStates.hr_change_upscaler.set()


@dp.callback_query_handler(state=SDStates.hr_settings, text='hr_steps')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Steps: "
                                     f"{current_settings['sd_hr_steps']}\n"
                                     f"✏️ Введи значение Steps", reply_markup=inline_cancel)
    await SDStates.hr_set_steps.set()


@dp.callback_query_handler(state=SDStates.hr_settings, text='hr_den_strength')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Denoising strength: "
                                     f"{current_settings['sd_hr_denoising_strength']}\n"
                                     f"✏️ Введи значение Denoising strength", reply_markup=inline_cancel)
    await SDStates.hr_set_denoising_strength.set()


@dp.callback_query_handler(state=SDStates.hr_settings, text='hr_upscale_by')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Upscale by: "
                                     f"{current_settings['sd_hr_upscale_by']}\n"
                                     f"✏️ Введи значение Upscale by", reply_markup=inline_cancel)
    await SDStates.hr_set_upscale_by.set()


@dp.callback_query_handler(Text(startswith="upscaler_"), state=SDStates.hr_change_upscaler)
async def current_settings(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    current_model_page = state_data.get('current_page')
    num_pages = state_data.get('num_pages')
    action = callback.data[9:]

    if action == "prev_page":
        if current_model_page > 0:
            current_model_page -= 1
            await state.update_data(current_page=current_model_page)
            styles_keyboard = await create_hr_upscalers_keyboard(state=state)
            await callback.message.edit_text(f"Страница {current_model_page + 1} из {num_pages}",
                                             reply_markup=styles_keyboard)
        else:
            await callback.answer()

    elif action == "next_page":
        if current_model_page < num_pages - 1:
            current_model_page += 1
            await state.update_data(current_page=current_model_page)
            styles_keyboard = await create_hr_upscalers_keyboard(state=state)
            await callback.message.edit_text(f"Страница {current_model_page + 1} из {num_pages}",
                                             reply_markup=styles_keyboard)
        else:
            await callback.answer()

    else:
        await db_service.db_set_sd_settings(callback.from_user.id, "sd_hr_upscaler", action)
        await callback.message.edit_text(f"<b>Upscaler \"{action}\" задан</b>", reply_markup=hires_menu)
        await SDStates.hr_settings.set()
