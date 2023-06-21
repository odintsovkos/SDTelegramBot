import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import dp
from utils.db_services import db_service
from utils.notify_admins import admin_notify
from utils.sd_api import api_service
from utils.sd_api.api_service import get_request_sd_api


async def set_params(tg_id: int, last_prompt):
    db_result = await db_service.db_get_sd_settings(tg_id)
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
    response = api_service.post_request_sd_api("txt2img", params)
    return response


async def change_sd_model(tg_id: int):
    sd_model = api_service.get_request_sd_api("options").json()['sd_model_checkpoint']
    db_model = await db_service.db_get_sd_setting(tg_id, "sd_model")
    if db_model != sd_model:
        params = {
            "sd_model_checkpoint": db_model
        }
        api_service.post_request_sd_api("options", params)
        return db_model
    else:
        return db_model


def is_sd_launched():
    response = get_request_sd_api("options")
    if response is None:
        return False
    else:
        return True


async def change_style_db(tg_id: int, entered_style):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
    if db_styles_list == "":
        await db_service.db_set_sd_settings(tg_id, 'sd_style', entered_style)
        return True
    else:
        result = db_styles_list.split('&')
        if entered_style not in result:
            result = db_styles_list + '&' + entered_style
            await db_service.db_set_sd_settings(tg_id, 'sd_style', result)
            return True
        else:
            result.remove(entered_style)
            await db_service.db_set_sd_settings(tg_id, 'sd_style', '&'.join(result))
            return False


async def user_samplers(api_samplers, hide_user_samplers):
    return [x for x in api_samplers if x['name'] not in hide_user_samplers]


async def create_samplers_keyboard():
    api_result = api_service.get_request_sd_api('samplers').json()
    hide_sampler = api_service.get_request_sd_api('options').json()['hide_samplers']

    inline_kb_full = ReplyKeyboardMarkup()
    inline_kb_full.add(KeyboardButton(text="~Назад~"))
    for i in await user_samplers(api_result, hide_sampler):
        inline_kb_full.add(KeyboardButton(text=i['name']))
    return inline_kb_full


def create_keyboard(endpoint, txt):
    result_models = api_service.get_request_sd_api(endpoint).json()
    inline_kb_full = ReplyKeyboardMarkup()
    inline_kb_full.add(KeyboardButton(text="~Назад~"))
    for i in result_models:
        inline_kb_full.add(KeyboardButton(text=i[txt]))
    return inline_kb_full


async def create_style_keyboard(tg_id: int):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
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
