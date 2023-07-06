from aiogram import executor
import time

from data.config import is_wait_sd_launch, time_the_next_check_s, launch_sd_at_bot_started
from loader import dp, logger
import middlewares, handlers
from utils.misc_func import is_sd_launched, check_sd_path, launch_sd_process
from utils.notify_admins import admin_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await admin_notify(dispatcher, msg="Бот запущен")


if __name__ == '__main__':
    start_time = time.time()

    if is_sd_launched():
        executor.start_polling(dp, on_startup=on_startup)

    elif launch_sd_at_bot_started and check_sd_path():
        launch_sd_process()
        logger.info("Начинаю запуск SD...")

        while True:
            if is_sd_launched():
                current_time = time.time()
                logger.info(f"SD запущена - {int(current_time - start_time)}s.")

                executor.start_polling(dp, on_startup=on_startup)
                break
            time.sleep(time_the_next_check_s)

    elif is_wait_sd_launch:
        count = 1

        while True:
            if is_sd_launched():
                current_time = time.time()
                logger.info(f"SD запущена - {int(current_time - start_time)}s.")

                executor.start_polling(dp, on_startup=on_startup)
                break
            logger.warning(f"LAUNCH ATTEMPT {count}, STABLE DIFFUSION NOT LAUNCHED!")
            count += 1
            time.sleep(time_the_next_check_s)

    elif not is_wait_sd_launch:
        logger.warning("SD не запущена!")

