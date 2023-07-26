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
import threading

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton

import settings.string_variables as str_var
from keyboards.inline.inline_menu import settings_menu, main_menu, create_styles_keyboard, \
    create_models_keyboard, create_loras_keyboard
from loader import dp
from settings.bot_config import ADMINS
from states.all_states import SDStates
from utils.db_services import db_service
from utils.misc_func import change_style_db, change_lora_db, send_photo, change_model_callback, restarting_sd, \
    is_sd_launched
from utils.waiting_bar import waiting_bar

last_prompt = ""
response_list = []
callback_data = None


@dp.message_handler(state=SDStates.enter_prompt, content_types=types.ContentTypes.TEXT)
async def entered_prompt_handler(message: types.Message):
    global last_prompt
    last_prompt = message['text']
    await message.bot.delete_message(message.chat.id, message.message_id)
    if is_sd_launched():
        await send_photo(message, message.from_user.id, last_prompt, response_list)
    else:
        await restarting_sd(message)
        await asyncio.sleep(2)
        await send_photo(message, message.from_user.id, last_prompt, response_list)


@dp.callback_query_handler(state=SDStates.enter_prompt, text='repeat')
async def current_settings(callback: types.CallbackQuery):
    global last_prompt
    await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if last_prompt.find('&') != -1:
        last_prompt = last_prompt[last_prompt.find('&') + 1:]
    if last_prompt != "":
        if is_sd_launched():
            await send_photo(callback.message, callback.from_user.id, last_prompt, response_list)
        else:
            await restarting_sd(callback)
            await asyncio.sleep(2)
            await send_photo(callback.message, callback.from_user.id, last_prompt, response_list)
    else:
        await callback.message.answer("✏️ Введите Prompt", reply_markup=main_menu)


@dp.callback_query_handler(state=SDStates.enter_prompt, text='repeat_with_seed')
async def current_settings(callback: types.CallbackQuery):
    await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if last_prompt != "":
        if is_sd_launched():
            await send_photo(callback.message, callback.from_user.id, last_prompt, response_list, with_seed=True)
        else:
            await restarting_sd(callback)
            await asyncio.sleep(2)
            await send_photo(callback.message, callback.from_user.id, last_prompt, response_list, with_seed=True)
    else:
        await callback.message.answer("✏️ Введите Prompt", reply_markup=main_menu)


@dp.callback_query_handler(state=SDStates.enter_prompt, text='model')
async def model_button_handler(callback: types.CallbackQuery, state: FSMContext):
    global callback_data
    callback_data = callback
    sd_model = await db_service.db_get_sd_setting(callback.from_user.id, "sd_model")
    await state.update_data(current_page=0)
    models_keyboard = await create_models_keyboard(state=state)
    await callback.message.edit_text(f"<b>Текущая модель:</b>\n<i>{sd_model}</i>\n"
                                     f"👇🏻 Выбери новую модель...", reply_markup=models_keyboard)
    await SDStates.settings_set_model.set()


@dp.callback_query_handler(Text(startswith="model_"), state=SDStates.settings_set_model)
async def change_model_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    state_data = await state.get_data()
    current_model_page = state_data.get('current_page')
    num_pages = state_data.get('num_pages')
    action = callback.data[6:]
    if action == "prev_page":
        if current_model_page > 0:
            current_model_page -= 1
            await state.update_data(current_page=current_model_page)
            styles_keyboard = await create_models_keyboard(state=state)
            await callback.message.edit_text(f"Страница {current_model_page + 1} из {num_pages}",
                                             reply_markup=styles_keyboard)
        else:
            await callback.answer()

    elif action == "next_page":
        if current_model_page < num_pages - 1:
            current_model_page += 1
            await state.update_data(current_page=current_model_page)
            styles_keyboard = await create_models_keyboard(state=state)
            await callback.message.edit_text(f"Страница {current_model_page + 1} из {num_pages}",
                                             reply_markup=styles_keyboard)
        else:
            await callback.answer()

    else:
        await db_service.db_set_sd_settings(callback.from_user.id, 'sd_model', action)
        await callback.message.edit_text("Загружаю модель в SD...")
        thread_change_model = threading.Thread(target=change_model_callback, args=(callback.from_user.id, response_list))
        thread_change_model.start()
        chat_id, message_id = await waiting_bar(callback.message.chat.id, thread_change_model)
        thread_change_model.join()
        await callback.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await callback.message.edit_text(text=f"✅ Модель загружена", reply_markup=main_menu)
        response_list.clear()
        await SDStates.enter_prompt.set()
    print(action)
    print(current_model_page)


@dp.callback_query_handler(state=SDStates.enter_prompt, text='styles')
async def styles_button_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(current_page=0)
    global callback_data
    callback_data = callback
    styles_keyboard = await create_styles_keyboard(callback.from_user.id, state=state)
    await callback.message.edit_text(f"👇🏻 Выбери стили", reply_markup=styles_keyboard)
    await SDStates.settings_set_style.set()


@dp.callback_query_handler(Text(startswith="style_"), state=SDStates.settings_set_style)
async def change_style_handler(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    current_page = state_data.get('current_page')
    num_pages = state_data.get('num_pages')
    action = callback.data[6:]
    if action == "confirm":
        await callback.message.edit_text("📝 Стили установлены", reply_markup=main_menu)
        await SDStates.enter_prompt.set()
    elif action == "disable_all":
        await callback.message.edit_text("📝 Стили отключены", reply_markup=main_menu)
        await db_service.db_set_sd_settings(callback.from_user.id, "sd_style", "")
        await SDStates.enter_prompt.set()
    elif action == "prev_page":
        current_page -= 1
        await state.update_data(current_page=current_page)
        styles_keyboard = await create_styles_keyboard(callback.from_user.id, state=state)
        await callback.message.edit_text(f"Страница {current_page + 1} из {num_pages}",
                                         reply_markup=styles_keyboard)
    elif action == "next_page":
        current_page += 1
        await state.update_data(current_page=current_page)
        styles_keyboard = await create_styles_keyboard(callback.from_user.id, state=state)
        await callback.message.edit_text(f"Страница {current_page + 1} из {num_pages}",
                                         reply_markup=styles_keyboard)
    else:
        if action[0] == "✅":
            action = action[2:]
        is_changed = await change_style_db(callback.from_user.id, action)
        styles_keyboard = await create_styles_keyboard(callback.from_user.id, state=state)
        await callback.message.edit_text(f"Стиль {action} {'установлен' if is_changed else 'отключен'}",
                                         reply_markup=styles_keyboard)


@dp.callback_query_handler(state=SDStates.enter_prompt, text='loras')
async def current_settings(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(current_page=0)
    global callback_data
    callback_data = callback
    lora_keyboard = await create_loras_keyboard(callback.from_user.id, state=state)
    if lora_keyboard is None:
        await callback.message.edit_text("LoRA не найдены", reply_markup=main_menu)
        await SDStates.enter_prompt.set()
        return
    await callback.message.edit_text(f"👇🏻 Выбери LoRa", reply_markup=lora_keyboard)
    await SDStates.settings_set_lora.set()


@dp.callback_query_handler(Text(startswith="lora_"), state=SDStates.settings_set_lora)
async def current_settings(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    current_page = state_data.get('current_page')
    num_pages = state_data.get('num_pages')
    action = callback.data[5:]

    if action == "confirm":
        await callback.message.edit_text("📝 LoRa установлены", reply_markup=main_menu)
        await SDStates.enter_prompt.set()
    elif action == "disable_all":
        await callback.message.edit_text("📝 Lora отключены", reply_markup=main_menu)
        await db_service.db_set_sd_settings(callback.from_user.id, "sd_lora", "")
        await SDStates.enter_prompt.set()
    elif action == "prev_page":
        if current_page > 0:
            current_page -= 1
            await state.update_data(current_page=current_page)
            styles_keyboard = await create_loras_keyboard(callback.from_user.id, state=state)
            await callback.message.edit_text(f"Страница {current_page + 1} из {num_pages}",
                                             reply_markup=styles_keyboard)
        else:
            await callback.answer()
    elif action == "next_page":
        if current_page < num_pages - 1:
            current_page += 1
            await state.update_data(current_page=current_page)
            styles_keyboard = await create_loras_keyboard(callback.from_user.id, state=state)
            await callback.message.edit_text(f"Страница {current_page + 1} из {num_pages}",
                                             reply_markup=styles_keyboard)
        else:
            await callback.answer()
    else:
        if action[0] == "✅":
            action = action[2:]
        is_changed = await change_lora_db(callback.from_user.id, action)
        lora_keyboard = await create_loras_keyboard(callback.from_user.id, state=state)
        await callback.message.edit_text(f"LoRa {action} {'установлен' if is_changed else 'отключен'}",
                                         reply_markup=lora_keyboard)


@dp.callback_query_handler(state=SDStates.enter_prompt, text='settings')
async def current_settings(callback: types.CallbackQuery):
    if str(callback.from_user.id) in ADMINS and settings_menu.inline_keyboard[-1][0].text != str_var.restart_sd:
        settings_menu.add(InlineKeyboardButton(text=str_var.restart_sd, callback_data="restart_sd"))
    await callback.message.edit_text("⚙️ Настройки", reply_markup=settings_menu)
    await SDStates.settings.set()


@dp.callback_query_handler(state=[SDStates.settings_set_style,
                                  SDStates.settings_set_lora,
                                  SDStates.settings_set_model], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("📖 Меню генерации", reply_markup=main_menu)
    await SDStates.enter_prompt.set()
