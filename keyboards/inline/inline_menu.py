"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import settings.string_variables as str_var
from utils.db_services import db_service
from utils.misc_func import user_samplers
from utils.sd_api import api_service

main_menu = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text=str_var.repeat, callback_data='repeat'),
            InlineKeyboardButton(text=str_var.repeat_with_seed, callback_data='repeat_with_seed'),
        ],
        [
            InlineKeyboardButton(text=str_var.model, callback_data='model'),
            InlineKeyboardButton(text=str_var.styles, callback_data='styles'),
            InlineKeyboardButton(text=str_var.loras, callback_data='loras'),
        ],
        [
            InlineKeyboardButton(text=str_var.settings, callback_data='settings'),
        ]
    ],
)

main_menu_none_repeat = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text=str_var.model, callback_data='model'),
            InlineKeyboardButton(text=str_var.styles, callback_data='styles'),
            InlineKeyboardButton(text=str_var.loras, callback_data='loras'),
        ],
        [
            InlineKeyboardButton(text=str_var.settings, callback_data='settings'),
        ],
    ],
)

settings_menu = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text=str_var.current_settings, callback_data='current_settings'),
        ],
        [
            InlineKeyboardButton(text=str_var.gen_settings, callback_data='gen_settings'),
            InlineKeyboardButton(text=str_var.hr_settings, callback_data='hr_settings'),
        ],
        [
            InlineKeyboardButton(text=str_var.ad_settings, callback_data='ad_settings'),
        ],
        [
            InlineKeyboardButton(text=str_var.reset_settings, callback_data='reset_settings'),
        ],
        [
            InlineKeyboardButton(text=str_var.cancel, callback_data='cancel'),
        ],
    ],
)

gen_settings_menu = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text=str_var.negative_prompt, callback_data='negative_prompt'),
            InlineKeyboardButton(text=str_var.sampler, callback_data='sampler'),
            InlineKeyboardButton(text=str_var.steps, callback_data='steps'),
        ],
        [
            InlineKeyboardButton(text=str_var.width_height, callback_data='width_height'),
            InlineKeyboardButton(text=str_var.cfg_scale, callback_data='cfg_scale'),
            InlineKeyboardButton(text=str_var.batch_count, callback_data='batch_count'),
        ],
        [
            InlineKeyboardButton(text=str_var.cancel, callback_data='cancel'),
        ]
    ],
)

hires_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str_var.hr_on_off, callback_data='hr_on_off'),
        ],
        [
            InlineKeyboardButton(text=str_var.hr_upscaler, callback_data='hr_upscaler'),
            InlineKeyboardButton(text=str_var.hr_steps, callback_data='hr_steps'),
            InlineKeyboardButton(text=str_var.hr_denoising_strength, callback_data='hr_den_strength'),
            InlineKeyboardButton(text=str_var.hr_upscale_by, callback_data='hr_upscale_by'),
        ],
        [
            InlineKeyboardButton(text=str_var.cancel, callback_data='cancel'),
        ],
    ],
)

adetailer_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str_var.ad_on_off, callback_data='ad_on_off'),
        ],
        [
            InlineKeyboardButton(text=str_var.ad_model, callback_data='ad_model'),
        ],
        [
            InlineKeyboardButton(text=str_var.ad_prompt, callback_data='ad_prompt'),
            InlineKeyboardButton(text=str_var.ad_neg_prompt, callback_data='ad_neg_prompt'),
        ],
        [
            InlineKeyboardButton(text=str_var.ad_confidence, callback_data='ad_confidence'),
            InlineKeyboardButton(text=str_var.ad_mask_blur, callback_data='ad_mask_blur'),
        ],
        [
            InlineKeyboardButton(text=str_var.ad_denoising_strength, callback_data='ad_denoising_strength'),
            InlineKeyboardButton(text=str_var.ad_wh, callback_data='ad_wh'),
        ],
        [
            InlineKeyboardButton(text=str_var.ad_steps, callback_data='ad_steps'),
            InlineKeyboardButton(text=str_var.cancel, callback_data='cancel'),
        ],
    ],
)

inline_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str_var.cancel, callback_data='cancel'),
        ]
    ]
)


def wh_create_keyboards():
    inline_kb_full = InlineKeyboardMarkup()
    for i in range(0, len(str_var.wh_buttons), 2):
        if i + 1 < len(str_var.wh_buttons):
            inline_kb_full.add(
                InlineKeyboardButton(text=str_var.wh_buttons[i], callback_data="wh_" + str_var.wh_buttons[i]),
                InlineKeyboardButton(text=str_var.wh_buttons[i + 1],
                                     callback_data="wh_" + str_var.wh_buttons[i + 1])
            )
        else:
            inline_kb_full.add(
                InlineKeyboardButton(text=str_var.wh_buttons[i], callback_data="wh_" + str_var.wh_buttons[i]))
    inline_kb_full.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return inline_kb_full


async def create_samplers_inline_keyboard():
    api_result = api_service.get_request_sd_api('samplers').json()
    hide_sampler = api_service.get_request_sd_api('options').json()['hide_samplers']
    user_samplers_list = await user_samplers(api_result, hide_sampler)
    inline_kb_full = InlineKeyboardMarkup()

    for i in range(0, len(user_samplers_list), 2):
        if i + 1 < len(user_samplers_list):
            inline_kb_full.add(
                InlineKeyboardButton(text=user_samplers_list[i]['name'],
                                     callback_data="sampler_" + user_samplers_list[i]['name']),
                InlineKeyboardButton(text=user_samplers_list[i + 1]['name'],
                                     callback_data="sampler_" + user_samplers_list[i + 1]['name'])
            )
        else:
            inline_kb_full.add(
                InlineKeyboardButton(text=user_samplers_list[i]['name'],
                                     callback_data="sampler_" + user_samplers_list[i]['name']))
    inline_kb_full.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return inline_kb_full


async def create_hr_upscalers_keyboard():
    api_result = api_service.get_request_sd_api('upscalers').json()
    inline_kb_full = InlineKeyboardMarkup()

    for i in range(1, len(api_result), 2):
        if i + 1 < len(api_result):
            inline_kb_full.add(
                InlineKeyboardButton(text=api_result[i]['name'], callback_data="upscaler_" + api_result[i]['name']),
                InlineKeyboardButton(text=api_result[i + 1]['name'],
                                     callback_data="upscaler_" + api_result[i + 1]['name'])
            )
        else:
            inline_kb_full.add(
                InlineKeyboardButton(text=api_result[i]['name'], callback_data="upscaler_" + api_result[i]['name']))
    inline_kb_full.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return inline_kb_full

async def create_ad_model_keyboard():
    model_list = [
        "face_yolov8n.pt",
        "face_yolov8s.pt",
        "hand_yolov8n.pt",
        "person_yolov8n-seg.pt",
        "person_yolov8s-seg.pt",
        "mediapipe_face_full",
        "mediapipe_face_short",
        "mediapipe_face_mesh",
        "mediapipe_face_mesh_eyes_only"
    ]

    inline_kb_full = InlineKeyboardMarkup()

    for i in range(0, len(model_list), 2):
        if i + 1 < len(model_list):
            inline_kb_full.add(
                InlineKeyboardButton(text=model_list[i], callback_data="ad_model_" + model_list[i]),
                InlineKeyboardButton(text=model_list[i + 1], callback_data="ad_model_" + model_list[i + 1])
            )
        else:
            inline_kb_full.add(
                InlineKeyboardButton(text=model_list[i], callback_data="ad_model_" + model_list[i])
            )

    inline_kb_full.add(InlineKeyboardButton(text="Cancel", callback_data="cancel"))

    return inline_kb_full


def create_model_keyboard(endpoint, txt):
    result_models = api_service.get_request_sd_api(endpoint).json()
    result_models = [x[txt] for x in result_models]
    result_models.sort()
    inline_kb_full = InlineKeyboardMarkup()
    for i in range(0, len(result_models), 2):
        if i + 1 < len(result_models):

            inline_kb_full.add(
                InlineKeyboardButton(text=result_models[i], callback_data="model_" + result_models[i]),
                InlineKeyboardButton(text=result_models[i + 1],
                                     callback_data="model_" + result_models[i + 1])
            )
        else:
            inline_kb_full.add(
                InlineKeyboardButton(text=result_models[i], callback_data="model_" + result_models[i]))
    inline_kb_full.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return inline_kb_full


async def create_style_keyboard(tg_id: int):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
    sd_styles = api_service.get_request_sd_api('prompt-styles').json()
    styles_keyboard = InlineKeyboardMarkup()

    for i in range(0, len(sd_styles), 3):
        if i + 1 < len(sd_styles) and i + 2 < len(sd_styles):
            styles_keyboard.add(
                InlineKeyboardButton(
                    text=sd_styles[i]['name'] if sd_styles[i]['name'] not in db_styles_list else "✳️" + sd_styles[i][
                        'name'],
                    callback_data="style_" + sd_styles[i]['name']),
                InlineKeyboardButton(
                    text=sd_styles[i + 1]['name'] if sd_styles[i + 1]['name'] not in db_styles_list else "✳️" +
                                                                                                         sd_styles[
                                                                                                             i + 1][
                                                                                                             'name'],
                    callback_data="style_" + sd_styles[i + 1]['name']),
                InlineKeyboardButton(
                    text=sd_styles[i + 2]['name'] if sd_styles[i + 2]['name'] not in db_styles_list else "✳️" +
                                                                                                         sd_styles[
                                                                                                             i + 2][
                                                                                                             'name'],
                    callback_data="style_" + sd_styles[i + 2]['name'])
            )
        elif i + 1 < len(sd_styles):
            styles_keyboard.add(
                InlineKeyboardButton(
                    text=sd_styles[i]['name'] if sd_styles[i]['name'] not in db_styles_list else "✳️" + sd_styles[i][
                        'name'],
                    callback_data="style_" + sd_styles[i]['name']),
                InlineKeyboardButton(
                    text=sd_styles[i + 1]['name'] if sd_styles[i + 1]['name'] not in db_styles_list else "✳️" +
                                                                                                         sd_styles[
                                                                                                             i + 1][
                                                                                                             'name'],
                    callback_data="style_" + sd_styles[i + 1]['name']),
            )
        else:
            styles_keyboard.add(
                InlineKeyboardButton(
                    text=sd_styles[i]['name'] if sd_styles[i]['name'] not in db_styles_list else "✳️" + sd_styles[i][
                        'name'],
                    callback_data="style_" + sd_styles[i]['name']))

    styles_keyboard.add(InlineKeyboardButton(text=str_var.confirm, callback_data="style_confirm"),
                        InlineKeyboardButton(text=str_var.disable_all_styles, callback_data="style_disable_all_styles"))
    styles_keyboard.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return styles_keyboard


async def create_lora_keyboard(tg_id: int):
    db_lora_list = await db_service.db_get_sd_setting(tg_id, 'sd_lora')
    sd_lora = api_service.get_request_sd_api('loras').json()
    lora_keyboard = InlineKeyboardMarkup()
    if len(sd_lora) == 0:
        return None
    for i in range(0, len(sd_lora), 3):
        if i + 1 < len(sd_lora) and i + 2 < len(sd_lora):
            lora_keyboard.add(
                InlineKeyboardButton(
                    text=sd_lora[i]['name'] if sd_lora[i]['name'] not in db_lora_list else "✳️" + sd_lora[i][
                        'name'],
                    callback_data="lora_" + sd_lora[i]['name']),
                InlineKeyboardButton(
                    text=sd_lora[i + 1]['name'] if sd_lora[i + 1]['name'] not in db_lora_list else "✳️" +
                                                                                                   sd_lora[
                                                                                                       i + 1][
                                                                                                       'name'],
                    callback_data="lora_" + sd_lora[i + 1]['name']),
                InlineKeyboardButton(
                    text=sd_lora[i + 2]['name'] if sd_lora[i + 2]['name'] not in db_lora_list else "✳️" +
                                                                                                   sd_lora[
                                                                                                       i + 2][
                                                                                                       'name'],
                    callback_data="lora_" + sd_lora[i + 2]['name'])
            )
        elif i + 1 < len(sd_lora):
            lora_keyboard.add(
                InlineKeyboardButton(
                    text=sd_lora[i]['name'] if sd_lora[i]['name'] not in db_lora_list else "✳️" + sd_lora[i][
                        'name'],
                    callback_data="lora_" + sd_lora[i]['name']),
                InlineKeyboardButton(
                    text=sd_lora[i + 1]['name'] if sd_lora[i + 1]['name'] not in db_lora_list else "✳️" +
                                                                                                   sd_lora[
                                                                                                       i + 1][
                                                                                                       'name'],
                    callback_data="lora_" + sd_lora[i + 1]['name']),
            )
        else:
            lora_keyboard.add(
                InlineKeyboardButton(
                    text=sd_lora[i]['name'] if sd_lora[i]['name'] not in db_lora_list else "✳️" + sd_lora[i][
                        'name'],
                    callback_data="lora_" + sd_lora[i]['name']))

    lora_keyboard.add(InlineKeyboardButton(text=str_var.confirm, callback_data="lora_confirm"),
                      InlineKeyboardButton(text=str_var.disable_all_loras, callback_data="lora_disable_all_loras"))
    lora_keyboard.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return lora_keyboard
