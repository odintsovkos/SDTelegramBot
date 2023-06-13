from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

auth_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Запрос авторизации"),
        ]
    ],
    resize_keyboard=True
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Ещё раз"),
        ],
        [
            KeyboardButton(text="Модель"),
            KeyboardButton(text="Стиль"),
        ],
    ],
    resize_keyboard=True
)

settings = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Текущие настройки"),
        ],
        [
            KeyboardButton(text="Negative Prompt"),
            KeyboardButton(text="Sampler"),
            KeyboardButton(text="Steps"),
        ],
        [

            KeyboardButton(text="Width & Height"),
            KeyboardButton(text="CFG Scale"),
            KeyboardButton(text="Restore face"),
        ],
        [

            KeyboardButton(text="Batch count"),
        ],
        [
            KeyboardButton(text="Сброс настроек"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ],
    resize_keyboard=True
)

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена"),
        ],
    ],
    resize_keyboard=True
)
