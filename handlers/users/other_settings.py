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
from keyboards.inline.inline_menu import inline_cancel,other_settings, hires_menu, settings_menu
from loader import dp
from states.all_states import SDStates
import settings.string_variables as str_var
from utils.db_services import db_service

callback_data = None

@dp.message_handler(state=SDStates.other_settings, content_types=types.ContentTypes.TEXT)
async def settings_buttons_handler(message: types.Message):
    current_settings = await db_service.db_get_sd_settings(message.from_user.id)
    if message.text == str_var.enable_auto_translate:
        await message.answer(f"Текущее состояние: "
                             f"Автопереводчик - {'Включен' if current_settings['auto_translate'] == 1 else 'Отключен'}\n"
                             f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=keyboards.cancel)
        await SDStates.enable_auto_translate.set()

@dp.callback_query_handler(state=[SDStates.other_settings], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("⚙️ Настройки", reply_markup=settings_menu)
    await SDStates.settings.set()

@dp.callback_query_handler(state=[SDStates.enable_auto_translate,
                                  ], text='cancel')
async def generation_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("Дополнительные настройки", reply_markup=other_settings)
    await SDStates.settings.set()

@dp.message_handler(state=SDStates.enable_auto_translate, content_types=types.ContentTypes.TEXT)
async def enable_auto_translate_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "auto_translate", message.text)
    await callback_data.message.edit_text(f"Автопереводчик - {'Включен' if int(message.text) == 1 else 'Отключен'}", reply_markup=other_settings)
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await SDStates.other_settings.set()


@dp.callback_query_handler(state=SDStates.other_settings, text='enable_auto_translate')
async def current_settings(callback: types.CallbackQuery):
    global callback_data
    callback_data = callback
    current_settings = await db_service.db_get_sd_settings(callback.from_user.id)
    await callback.message.edit_text(f"Текущее состояние: "
                                     f"Автопереводчик - {'Включен' if current_settings['auto_translate'] == 1 else 'Отключен'}\n"
                                     f"✏️ Введи 1 - Вкл. или 0 - Выкл.", reply_markup=inline_cancel)
    await SDStates.enable_auto_translate.set()
