from aiogram import executor
import time

from data.config import is_wait_sd_launch, num_of_checks, time_the_next_check_s, launch_sd_at_bot_started
from loader import dp
import middlewares, handlers
from utils.misc_func import is_sd_launched, check_sd_path, launch_sd_process
from utils.notify_admins import admin_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await admin_notify(dispatcher, msg="Бот запущен")


def print_error(num):
    print(f"\033[93m!!!        LAUNCH ATTEMPT {num}       !!!")
    print("\033[93m!!! STABLE DIFFUSION NOT LAUNCHED !!!")
    print("*********************************")
    time.sleep(time_the_next_check_s)


if __name__ == '__main__':
    if is_sd_launched():
        executor.start_polling(dp, on_startup=on_startup)
    elif launch_sd_at_bot_started and check_sd_path():
        launch_sd_process()
        print()
        print("Начинаю запуск SD...")
        while True:
            if is_sd_launched():
                executor.start_polling(dp, on_startup=on_startup)
                print("SD запущена!!!")
                break
            time.sleep(time_the_next_check_s)
    elif is_wait_sd_launch:
        if num_of_checks == 0:
            count = 1
            while True:
                if is_sd_launched():
                    executor.start_polling(dp, on_startup=on_startup)
                    print("SD запущена!!!")
                    break
                print_error(count)
                count += 1
                time.sleep(time_the_next_check_s)

        for i in range(1, num_of_checks + 1):
            if is_sd_launched():
                executor.start_polling(dp, on_startup=on_startup)
                break
            else:
                print_error(i)

    elif not is_wait_sd_launch:
        error_text = "*********************************\n" \
                     "* STABLE DIFFUSION NOT LAUNCHED *\n" \
                     "*********************************"
        print(f"\033[93m{error_text}")

