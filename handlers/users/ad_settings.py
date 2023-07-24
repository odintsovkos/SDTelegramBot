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

from keyboards.default import keyboards
from keyboards.inline.inline_menu import inline_cancel, create_hr_upscalers_keyboard, adetailer_menu, settings_menu
from loader import dp
from states.all_states import SDStates
import settings.string_variables as str_var
from utils.db_services import db_service

callback_data = None

@dp.message_handler(state=SDStates.ad_settings, content_types=types.ContentTypes.TEXT)
async def settings_buttons_handler(message: types.Message):
    current_settings = await db_service.db_get_sd_settings(message.from_user.id)
    print("test")
    if message.text == str_var.ad_on_of:
        await message.answer(f"Текущее состояние: "
                             f"Adetailer - {'Включен' if current_settings['ad_on_off'] == 1 else 'Отключен'}\n"
                             f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=keyboards.cancel)
        await SDStates.ad_on_off.set()


@dp.callback_query_handler(state=[SDStates.ad_settings], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    print("test1")
    await callback.message.edit_text("⚙️ Настройки", reply_markup=settings_menu)
    await SDStates.settings.set()


@dp.callback_query_handler(state=[SDStates.ad_on_off,
                                  SDStates.ad_set_prompt,
                                  SDStates.ad_set_neg_prompt,
                                  SDStates.ad_set_confidence,
                                  SDStates.ad_set_mask_blur,
                                  SDStates.ad_set_denoising_strength,
                                  SDStates.ad_set_wh,
                                  SDStates.ad_set_steps,
                                  SDStates.ad_change_model,], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    print("test12")
    await callback.message.edit_text("👩 Настройки Adetailer", reply_markup=adetailer_menu)
    await SDStates.ad_settings.set()


@dp.message_handler(state=SDStates.ad_on_off, content_types=types.ContentTypes.TEXT)
async def ad_on_off_button_handler(message: Message):
    print("test3")
    await db_service.db_set_sd_settings(message.from_user.id, "ad_on_off", message.text)
    await callback_data.message.edit_text(f"Adetailer - {'Включен' if int(message.text) == 1 else 'Отключен'}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()


@dp.message_handler(state=SDStates.ad_set_steps, content_types=types.ContentTypes.TEXT)
async def ad_on_off_button_handler(message: Message):
    print("test4")
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "ad_steps", message.text)
        await callback_data.message.edit_text("Steps установлен", reply_markup=adetailer_menu)
        await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await SDStates.ad_settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


# @dp.message_handler(state=SDStates.hr_set_denoising_strength, content_types=types.ContentTypes.TEXT)
# async def hr_on_off_button_handler(message: Message):
#     try:
#         await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_denoising_strength", float(message.text))
#         await callback_data.message.edit_text("Denoising strength установлен", reply_markup=adetailer_menu)
#         await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
#         await SDStates.hr_settings.set()
#     except ValueError:
#         await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


# @dp.message_handler(state=SDStates.hr_set_upscale_by, content_types=types.ContentTypes.TEXT)
# async def hr_on_off_button_handler(message: Message):
#     if message.text.isdigit():
#         await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_upscale_by", message.text)
#         await callback_data.message.edit_text("Upscale by установлен", reply_markup=adetailer_menu)
#         await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
#         await SDStates.hr_settings.set()
#     else:
#         await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_on_off')
async def current_settings(callback: types.CallbackQuery):
    print("test5")
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее состояние: "
                                     f"Adetailer - {'Включен' if current_settings['ad_on_off'] == 1 else 'Отключен'}\n"
                                     f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=inline_cancel)
    await SDStates.ad_on_off.set()


# @dp.callback_query_handler(state=SDStates.hr_settings, text='hr_upscaler')
# async def current_settings(callback: types.CallbackQuery):
#     global callback_data
#     callback_data = callback
#     current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
#     upscaler_keyboard = await create_hr_upscalers_keyboard()
#     await callback.message.edit_text(f"Текущий Upscaler: "
#                                      f"{current_settings['sd_hr_upscaler']}\n"
#                                      f"✏️ Выбери Upscaler", reply_markup=upscaler_keyboard)
#     await SDStates.hr_change_upscaler.set()


@dp.callback_query_handler(state=SDStates.ad_on_off, text='ad_steps')
async def current_settings(callback: types.CallbackQuery):
    print("test6")
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Steps: "
                                     f"{current_settings['ad_steps']}\n"
                                     f"✏️ Введи значение Steps", reply_markup=inline_cancel)
    await SDStates.ad_set_steps.set()


# @dp.callback_query_handler(state=SDStates.hr_settings, text='hr_den_strength')
# async def current_settings(callback: types.CallbackQuery):
#     global callback_data
#     callback_data = callback
#     current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
#     await callback.message.edit_text(f"Текущее значение Denoising strength: "
#                                      f"{current_settings['sd_hr_denoising_strength']}\n"
#                                      f"✏️ Введи значение Denoising strength", reply_markup=inline_cancel)
#     await SDStates.hr_set_denoising_strength.set()


# @dp.callback_query_handler(state=SDStates.hr_settings, text='hr_upscale_by')
# async def current_settings(callback: types.CallbackQuery):
#     global callback_data
#     callback_data = callback
#     current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
#     await callback.message.edit_text(f"Текущее значение Upscale by: "
#                                      f"{current_settings['sd_hr_upscale_by']}\n"
#                                      f"✏️ Введи значение Upscale by", reply_markup=inline_cancel)
#     await SDStates.hr_set_upscale_by.set()


# @dp.callback_query_handler(Text(startswith="upscaler_"), state=SDStates.hr_change_upscaler)
# async def current_settings(callback: types.CallbackQuery):
#     action = callback.data[9:]
#     await db_service.db_set_sd_settings(callback.from_user.id, "sd_hr_upscaler", action)
#     await callback.message.edit_text(f"<b>Upscaler \"{action}\" задан</b>", reply_markup=adetailer_menu)
#     await SDStates.hr_settings.set()
