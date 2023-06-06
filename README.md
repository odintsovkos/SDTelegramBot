Stable Diffusion Local Telegram Bot

Бот предназначен для управления локальной версией Stable Diffusion от AUTOMATIC1111,
через Telegram.\
Бот использует API от AUTOMATIC для взаимодействия с SD и асинхронную библиотеку Aiogram,\
для взаимодействия с Telegram.

Для использования бота необходимо:
1. В файле "webui-user.bat", в строке set COMMANDLINE_ARGS добавить --api (set COMMANDLINE_ARGS=--args)
2. Запустить SD
3. В Телеграм найти BotFather, создать бота и скопировать Bot Token
4. В папке с ботом создать файл .env и заполнить поля как в примере .env.dist
5. Запустить файл "start_bot.bat"
6. Если всё сделано правильно, то в Телеграм придет сообщение "Бот Запущен", тем ID которые были указаны