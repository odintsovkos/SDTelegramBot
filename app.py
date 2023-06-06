from aiogram import executor

from loader import dp
import middlewares, handlers
from utils.misc_func import is_sd_launched
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    if is_sd_launched():
        executor.start_polling(dp, on_startup=on_startup)
    else:
        error_text = "*********************************\n" \
                     "* STABLE DIFFUSION NOT LAUNCHED *\n" \
                     "*********************************"
        print(f"\033[31m{error_text}")

