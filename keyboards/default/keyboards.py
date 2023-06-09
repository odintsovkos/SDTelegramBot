from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import settings.string_variables as str_var
from utils.db_services import db_service
from utils.misc_func import user_samplers
from utils.sd_api import api_service

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=str_var.repeat),
        ],
        [
            KeyboardButton(text=str_var.model),
            KeyboardButton(text=str_var.styles),
            KeyboardButton(text=str_var.loras),
        ],
    ],
    resize_keyboard=True
)

settings = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=str_var.current_settings),
        ],
        [
            KeyboardButton(text=str_var.negative_prompt),
            KeyboardButton(text=str_var.sampler),
            KeyboardButton(text=str_var.steps),
        ],
        [

            KeyboardButton(text=str_var.width_height),
            KeyboardButton(text=str_var.cfg_scale),
            KeyboardButton(text=str_var.restore_face),
        ],
        [

            KeyboardButton(text=str_var.batch_count),
        ],
        [
            KeyboardButton(text=str_var.reset_settings),
        ],
        [
            KeyboardButton(text=str_var.cancel),
        ],
    ],
    resize_keyboard=True
)

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=str_var.cancel),
        ],
    ],
    resize_keyboard=True
)


async def create_samplers_keyboard():
    api_result = api_service.get_request_sd_api('samplers').json()
    hide_sampler = api_service.get_request_sd_api('options').json()['hide_samplers']
    inline_kb_full = ReplyKeyboardMarkup()
    inline_kb_full.add(KeyboardButton(text=str_var.cancel))
    for i in await user_samplers(api_result, hide_sampler):
        inline_kb_full.add(KeyboardButton(text=i['name']))
    return inline_kb_full


def create_model_keyboard(endpoint, txt):
    result_models = api_service.get_request_sd_api(endpoint).json()
    result_models = [x[txt] for x in result_models]
    result_models.sort()
    inline_kb_full = ReplyKeyboardMarkup()
    inline_kb_full.add(KeyboardButton(text=str_var.cancel))
    for i in result_models:
        inline_kb_full.add(KeyboardButton(text=i))
    return inline_kb_full


async def create_style_keyboard(tg_id: int):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
    sd_styles = api_service.get_request_sd_api('prompt-styles').json()
    styles_keyboard = ReplyKeyboardMarkup()
    styles_keyboard.add(KeyboardButton(text=str_var.cancel))
    styles_keyboard.add(KeyboardButton(text=str_var.confirm))
    styles_keyboard.add(KeyboardButton(text=str_var.disable_all_styles))
    for i in sd_styles:
        if i['name'] in db_styles_list.split('&'):
            styles_keyboard.add(KeyboardButton(text='>> ' + i['name']))

        else:
            styles_keyboard.add(KeyboardButton(text=i['name']))
    return styles_keyboard


async def create_lora_keyboard(tg_id: int):
    db_lora_list = await db_service.db_get_sd_setting(tg_id, 'sd_lora')
    sd_lora = api_service.get_request_sd_api('loras').json()
    lora_keyboard = ReplyKeyboardMarkup()
    lora_keyboard.add(KeyboardButton(text=str_var.cancel))
    lora_keyboard.add(KeyboardButton(text=str_var.confirm))
    lora_keyboard.add(KeyboardButton(text=str_var.disable_all_loras))
    for i in sd_lora:
        if i['alias'] in db_lora_list.split('&'):
            lora_keyboard.add(KeyboardButton(text='>> ' + i['alias']))
        else:
            lora_keyboard.add(KeyboardButton(text=i['alias']))
    return lora_keyboard
