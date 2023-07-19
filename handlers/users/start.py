"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""


from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import Message

from keyboards.inline.inline_menu import main_menu
from loader import dp
from settings.bot_config import ADMINS
from states.all_states import SDStates
from utils.db_services import db_service


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    db_users_response = await db_service.db_get_sd_setting(message.from_user.id, 'tg_id')
    if message.from_user.id == db_users_response or message.from_user.id in ADMINS:
        await message.answer(f"🖐 Привет, {message.from_user.full_name}!")
        await message.answer(f"Я генерирую фото по любому тексту...")
        await message.answer(f"📖 Меню генерации", reply_markup=main_menu)
        await SDStates.enter_prompt.set()
