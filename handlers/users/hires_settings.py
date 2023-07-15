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
from keyboards.default.keyboards import create_hr_upscalers_keyboard
from loader import dp
from states.all_states import SDStates
import settings.string_variables as str_var
from utils.db_services import db_service


@dp.message_handler(Text(equals=str_var.cancel), state=[SDStates.hr_settings, SDStates.hr_set_on_off,
                                                        SDStates.hr_change_upscaler, SDStates.hr_set_steps,
                                                        SDStates.hr_set_denoising_strength, SDStates.hr_set_upscale_by])
async def cancel_button_handler(message: Message, state: FSMContext):
    if await state.get_state() == SDStates.hr_settings.state:
        await message.answer("⚙️ Настройки генерации", reply_markup=keyboards.settings)
        await SDStates.settings.set()
    else:
        await message.answer("⚙️ Настройки Hires", reply_markup=keyboards.hires_menu)
        await SDStates.hr_settings.set()


@dp.message_handler(state=SDStates.hr_settings, content_types=types.ContentTypes.TEXT)
async def settings_buttons_handler(message: types.Message):
    current_settings = await db_service.db_get_sd_settings(message.from_user.id)
    if message.text == str_var.hr_on_off:
        await message.answer(f"Текущее состояние: "
                             f"Hires - {'Включен' if current_settings['sd_hr_on_off'] == 1 else 'Отключен'}\n"
                             f"✏️ Введи 1 - Вкл. или 0 - Выкл.")
        await SDStates.hr_set_on_off.set()

    elif message.text == str_var.hr_upscaler:
        hr_upscalers_keyboard = await create_hr_upscalers_keyboard()
        await message.answer(f"Текущий Upscaler: "
                             f"{current_settings['sd_hr_upscaler']}\n"
                             f"✏️ Выбери Upscaler", reply_markup=hr_upscalers_keyboard)
        await SDStates.hr_change_upscaler.set()

    elif message.text == str_var.hr_steps:
        await message.answer(f"Текущее значение Steps: "
                             f"{current_settings['sd_hr_steps']}\n"
                             f"✏️ Введи значение Steps", reply_markup=keyboards.cancel)
        await SDStates.hr_set_steps.set()

    elif message.text == str_var.hr_denoising_strength:
        await message.answer(f"Текущее значение Denoising strength: "
                             f"{current_settings['sd_hr_denoising_strength']}\n"
                             f"✏️ Введи значение Denoising strength", reply_markup=keyboards.cancel)
        await SDStates.hr_set_denoising_strength.set()

    elif message.text == str_var.hr_upscale_by:
        await message.answer(f"Текущее значение Upscale by: "
                             f"{current_settings['sd_hr_upscale_by']}\n"
                             f"✏️ Введи значение Upscale by", reply_markup=keyboards.cancel)
        await SDStates.hr_set_upscale_by.set()


@dp.message_handler(state=SDStates.hr_set_on_off, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_on_off", message.text)
    await message.answer(f"Hires - {'Включен' if int(message.text) == 1 else 'Отключен'}",
                         reply_markup=keyboards.hires_menu)
    await SDStates.hr_settings.set()


@dp.message_handler(state=SDStates.hr_change_upscaler, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_upscaler", message.text)
    await message.answer(f"Upscaler {message.text} выбран",
                         reply_markup=keyboards.hires_menu)
    await SDStates.hr_settings.set()


@dp.message_handler(state=SDStates.hr_set_steps, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_steps", message.text)
        await message.answer(f"Steps установлен",
                             reply_markup=keyboards.hires_menu)
        await SDStates.hr_settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.hr_set_denoising_strength, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_denoising_strength", message.text)
        await message.answer(f"Denoising strength установлен",
                             reply_markup=keyboards.hires_menu)
        await SDStates.hr_settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)


@dp.message_handler(state=SDStates.hr_set_upscale_by, content_types=types.ContentTypes.TEXT)
async def hr_on_off_button_handler(message: Message):
    if message.text.isdigit():
        await db_service.db_set_sd_settings(message.from_user.id, "sd_hr_upscale_by", message.text)
        await message.answer(f"Upscale by установлен",
                             reply_markup=keyboards.hires_menu)
        await SDStates.hr_settings.set()
    else:
        await message.answer("Ошибка ввода", reply_markup=keyboards.cancel)
