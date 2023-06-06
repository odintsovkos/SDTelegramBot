Stable Diffusion Local Telegram Bot

Бот предназначен для управления локальной версией Stable Diffusion от AUTOMATIC1111,
через Telegram.\
Бот использует API от AUTOMATIC для взаимодействия с SD и асинхронную библиотеку Aiogram,\
для взаимодействия с Telegram.

Установка:
1. Создать папку в любом месте на диске
2. В этой папке в адресной строке написать cmd и нажать Enter
3. Клонировать репозиторий коммандой
    git clone https://github.com/odintsovkos/SDTelegramBot.git
4. Если не установлен Git, скачать Zip архив и распаковать
5. Следовать инструкции по запуску

Инструкция по запуску:
1. В файле "webui-user.bat", в строке set COMMANDLINE_ARGS добавить --api (set COMMANDLINE_ARGS=--args)
2. Запустить SD
3. В Телеграм найти BotFather, создать бота и скопировать Bot Token
4. В папке с ботом создать файл .env и заполнить поля как в примере .env.dist
5. Запустить файл "start_bot.bat"
6. Если всё сделано правильно, то в Телеграм придет сообщение "Бот Запущен", тем ID которые были указаны

![zX4mjBk65k4](https://github.com/odintsovkos/SDTelegramBot/assets/16336122/61fdb963-8557-4451-ac06-8f52add31a4f)
