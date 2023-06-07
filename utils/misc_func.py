import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from utils.db_services.db_get_service import db_get_sd_settings, db_get_sd_setting
from utils.db_services.db_set_service import db_set_sd_settings
from utils.sd_api import api_service
from utils.sd_api.api_service import get_request_sd_api


def set_params(tg_id: int, last_prompt):
    db_result = db_get_sd_settings(tg_id)
    params = {
        "prompt": last_prompt,
        "negative_prompt": db_result[3],
        "styles": db_result[2].split('&'),
        "cfg_scale": db_result[7],
        "steps": db_result[5],
        "width": int(db_result[6].split('x')[0]),
        "height": int(db_result[6].split('x')[1]),
        "sampler_name": db_result[4],
        "restore_faces": 'true' if db_result[8] else 'false',
        "batch_size": db_result[9]
    }
    try:
        response = api_service.post_request_sd_api("txt2img", params)
        return response
    except requests.exceptions.ConnectionError:
        print("Ошибка изменения настроек, проверь SD")


def change_sd_model(tg_id: int):
    sd_model = api_service.get_request_sd_api("options").json()['sd_model_checkpoint']
    db_model = db_get_sd_setting(tg_id, "sd_model")
    if db_model != sd_model:
        params = {
            "sd_model_checkpoint": db_model
        }
        try:
            api_service.post_request_sd_api("options", params)
            return db_model
        except requests.exceptions.ConnectionError:
            print("Ошибка загрузки модели, проверь SD")
    else:
        return db_model


def is_sd_launched():
    try:
        response = get_request_sd_api("options")
        return True
    except requests.exceptions.ConnectionError:
        return False


def create_style_keyboard(tg_id: int):
    db_styles_list = db_get_sd_setting(tg_id, 'sd_style')
    sd_styles = api_service.get_request_sd_api('prompt-styles').json()
    styles_keyboard = ReplyKeyboardMarkup()
    styles_keyboard.add(KeyboardButton(text="~Назад~"))
    styles_keyboard.add(KeyboardButton(text="~Подтвердить~"))
    styles_keyboard.add(KeyboardButton(text="~Отключить все стили~"))
    for i in sd_styles:
        if i['name'] in db_styles_list.split('&'):
            styles_keyboard.add(KeyboardButton(text='>> ' + i['name']))

        else:
            styles_keyboard.add(KeyboardButton(text=i['name']))
    return styles_keyboard


def change_style_db(tg_id: int, entered_style):
    db_styles_list = db_get_sd_setting(tg_id, 'sd_style')
    if db_styles_list == "":
        db_set_sd_settings(tg_id, 'sd_style', entered_style)
        return True
    else:
        result = db_styles_list.find(entered_style)
        if result == -1:
            result = db_styles_list + '&' + entered_style
            db_set_sd_settings(tg_id, 'sd_style', result)
            return True
        else:
            result = db_styles_list.split('&')
            result.remove(entered_style)
            db_set_sd_settings(tg_id, 'sd_style', '&'.join(result))
            return False
