"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.

Эта часть кода была написанна пользвателем daswer123
"""



from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from keyboards.default import keyboards
from keyboards.inline.inline_menu import inline_cancel, create_ad_model_keyboard, adetailer_menu, settings_menu
from loader import dp
from states.all_states import SDStates
import settings.string_variables as str_var
from utils.db_services import db_service

callback_data = None

@dp.message_handler(state=SDStates.ad_settings, content_types=types.ContentTypes.TEXT)
async def settings_buttons_handler(message: types.Message):
    current_settings = await db_service.db_get_sd_settings(message.from_user.id)
    if message.text == str_var.ad_on_off:
        await message.answer(f"Текущее состояние: "
                             f"Adetailer - {'Включен' if current_settings['ad_on_off'] == 1 else 'Отключен'}\n"
                             f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=keyboards.cancel)
        await SDStates.ad_on_off.set()


@dp.callback_query_handler(state=[SDStates.ad_settings], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
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
    await callback.message.edit_text("👩 Настройки Adetailer", reply_markup=adetailer_menu)
    await SDStates.ad_settings.set()


@dp.message_handler(state=SDStates.ad_on_off, content_types=types.ContentTypes.TEXT)
async def ad_on_off_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_on_off", message.text)
    await callback_data.message.edit_text(f"Adetailer - {'Включен' if int(message.text) == 1 else 'Отключен'}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()


@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_on_off')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее состояние: "
                                     f"Adetailer - {'Включен' if current_settings['ad_on_off'] == 1 else 'Отключен'}\n"
                                     f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=inline_cancel)
    await SDStates.ad_on_off.set()

# Обработчик для кнопки ad_model
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_model')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    ad_model_keyboard = await create_ad_model_keyboard()
    await callback.message.edit_text(f"Текущая модель Adetailer: "
                                     f"{current_settings['ad_model']}\n"
                                     f"✏️ Выбери Модель", reply_markup=ad_model_keyboard)
    await SDStates.ad_change_model.set()

@dp.message_handler(state=SDStates.ad_change_model, content_types=types.ContentTypes.TEXT)
async def ad_model_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_model", message.text)
    await callback_data.message.edit_text(f"Модель изменена на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

@dp.callback_query_handler(Text(startswith="ad_model_"), state=SDStates.ad_change_model)
async def current_settings(callback: types.CallbackQuery):
    action = callback.data[9:]
    await db_service.db_set_sd_settings(callback.from_user.id, "ad_model", action)
    await callback.message.edit_text(f"<b>Model \"{action}\" задан</b>", reply_markup=adetailer_menu)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_prompt
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_prompt')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущий Prompt: {current_settings['ad_prompt']}\n"
                                     f"✏️ Введите prompt для Adetailer", reply_markup=inline_cancel)
    await SDStates.ad_set_prompt.set()

@dp.message_handler(state=SDStates.ad_set_prompt, content_types=types.ContentTypes.TEXT)
async def ad_prompt_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_prompt", message.text)
    await callback_data.message.edit_text(f"Prompt изменен на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_neg_prompt
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_neg_prompt')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущий negative prompt: {current_settings['ad_negative_prompt']}\n"
                                     f"✏️ Введите negative prompt", reply_markup=inline_cancel)
    await SDStates.ad_set_neg_prompt.set()

@dp.message_handler(state=SDStates.ad_set_neg_prompt, content_types=types.ContentTypes.TEXT)
async def ad_neg_prompt_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_negative_prompt", message.text)
    await callback_data.message.edit_text(f"Negative prompt изменен на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_confidence
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_confidence')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущая сила определения лица: {current_settings['ad_confidence']}\n"
                                     f"✏️ Введите новую силу определения лица", reply_markup=inline_cancel)
    await SDStates.ad_set_confidence.set()

@dp.message_handler(state=SDStates.ad_set_confidence, content_types=types.ContentTypes.TEXT)
async def ad_confidence_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_confidence", message.text)
    await callback_data.message.edit_text(f"Сила определения лица изменена на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_mask_blur
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_mask_blur')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Mask Blur: {current_settings['ad_mask_blur']}\n"
                                     f"✏️ Введите новое значение для Mask Blur", reply_markup=inline_cancel)
    await SDStates.ad_set_mask_blur.set()

@dp.message_handler(state=SDStates.ad_set_mask_blur, content_types=types.ContentTypes.TEXT)
async def ad_mask_blur_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_mask_blur", message.text)
    await callback_data.message.edit_text(f"Mask Blur изменен на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_denoising_strength
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_denoising_strength')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Denoising Strength: {current_settings['ad_denoising_strength']}\n"
                                     f"✏️ Введите новое значение для Denoising Strength", reply_markup=inline_cancel)
    await SDStates.ad_set_denoising_strength.set()

@dp.message_handler(state=SDStates.ad_set_denoising_strength, content_types=types.ContentTypes.TEXT)
async def ad_denoising_strength_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_denoising_strength", message.text)
    await callback_data.message.edit_text(f"Denoising Strength изменено на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_wh
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_wh')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Width x Height: {current_settings['ad_inpaint_width_height']}\n"
                                     f"✏️ Введите новое значение для Width x Height, в формате 'ширинаxвысота'", reply_markup=inline_cancel)
    await SDStates.ad_set_wh.set()

@dp.message_handler(state=SDStates.ad_set_wh, content_types=types.ContentTypes.TEXT)
async def ad_wh_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_inpaint_width_height", message.text)
    await callback_data.message.edit_text(f"Width x Height изменено на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()

# Обработчик для кнопки ad_steps
@dp.callback_query_handler(state=SDStates.ad_settings, text='ad_steps')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее значение Steps: {current_settings['ad_steps']}\n"
                                     f"✏️ Введите новое значение для Steps", reply_markup=inline_cancel)
    await SDStates.ad_set_steps.set()

@dp.message_handler(state=SDStates.ad_set_steps, content_types=types.ContentTypes.TEXT)
async def ad_steps_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "ad_steps", message.text)
    await callback_data.message.edit_text(f"Steps изменено на {message.text}", reply_markup=adetailer_menu)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.ad_settings.set()
