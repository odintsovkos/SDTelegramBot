from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("settings", "Настройки генерации"),
            types.BotCommand("help", "Вывести справку"),
        ]
    )
