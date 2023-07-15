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
import logging
from aiogram import executor
import time
from settings.bot_config import is_wait_sd_launch, time_the_next_check_s, launch_sd_at_bot_started
from loader import dp
import middlewares, handlers
from utils.db_services import db_service
from utils.db_services.db_service import admins_and_users_initialization_in_db
from utils.misc_func import is_sd_launched, check_sd_path, start_sd_process
from utils.notifier import users_and_admins_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await db_service.db_create_table()
    await asyncio.sleep(2)
    await admins_and_users_initialization_in_db()
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await users_and_admins_notify(dispatcher, msg="📢 Бот запущен, введите команду /start для начала генерации...")


if __name__ == '__main__':
    start_time = time.time()

    if is_sd_launched():
        executor.start_polling(dp, on_startup=on_startup)

    elif launch_sd_at_bot_started and check_sd_path():
        start_sd_process()
        logging.info("Начинаю запуск SD...")

        while True:
            if is_sd_launched():
                current_time = time.time()
                logging.info(f"SD запущена - {int(current_time - start_time)}s.")

                executor.start_polling(dp, on_startup=on_startup)
                break
            time.sleep(time_the_next_check_s)

    elif is_wait_sd_launch:
        count = 1

        while True:
            if is_sd_launched():
                current_time = time.time()
                logging.info(f"SD запущена - {int(current_time - start_time)}s.")

                executor.start_polling(dp, on_startup=on_startup)
                break
            logging.warning(f"LAUNCH ATTEMPT {count}, STABLE DIFFUSION NOT LAUNCHED!")
            count += 1
            time.sleep(time_the_next_check_s)

    elif not is_wait_sd_launch:
        logging.warning("SD не запущена!")
