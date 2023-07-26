"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""
from aiogram.dispatcher import FSMContext
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

inline_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=str_var.cancel, callback_data='cancel'),
        ]
    ]
)


async def text_slicer(list_items):
    for i in range(0, len(list_items)):
        if len(list_items[i]) > 30:
            list_items[i] = list_items[i][:30]
    return list_items


async def checked_selected_items(db_items_list, api_items_list):
    for i in range(0, len(api_items_list)):
        if api_items_list[i] in db_items_list:
            api_items_list[i] = '✅ ' + api_items_list[i]
        else:
            api_items_list[i] = api_items_list[i]
    return api_items_list


async def create_hr_upscalers_keyboard(state: FSMContext = None):
    api_result = api_service.get_request_sd_api('upscalers').json()
    api_result = [x['name'] for x in api_result]
    api_result.sort()
    hr_upscalers_name_button = await text_slicer(api_result)
    hr_upscalers_keyboard = await create_keyboard(hr_upscalers_name_button, api_result, prefix="upscaler_", state=state)
    return hr_upscalers_keyboard


async def create_samplers_keyboard(state: FSMContext = None):
    api_result = api_service.get_request_sd_api('samplers').json()
    api_result = [x['name'] for x in api_result]
    api_result.sort()
    hide_sampler = api_service.get_request_sd_api('options').json()['hide_samplers']
    user_samplers_list = await user_samplers(api_result, hide_sampler)
    sampler_keyboard = await create_keyboard(user_samplers_list, user_samplers_list, prefix="sampler_", state=state)
    return sampler_keyboard


async def create_wh_keyboard(state: FSMContext = None):
    wh_keyboard = await create_keyboard(str_var.wh_buttons, str_var.wh_buttons, prefix="wh_", state=state)
    return wh_keyboard


async def create_models_keyboard(state: FSMContext = None):
    result_models = api_service.get_request_sd_api('sd-models').json()
    result_models = [x['model_name'] for x in result_models]
    result_models.sort()
    models_name_button = await text_slicer(result_models)
    models_keyboard = await create_keyboard(models_name_button, result_models, prefix="model_", state=state)
    return models_keyboard


async def create_styles_keyboard(tg_id, state: FSMContext = None):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
    sd_styles = api_service.get_request_sd_api('prompt-styles').json()
    sd_styles = [x['name'] for x in sd_styles]

    if len(db_styles_list) != 0:
        db_styles_list = db_styles_list.split('&')
        user_styles = await checked_selected_items(db_styles_list, sd_styles)
        list_name_button = await text_slicer(user_styles)
    else:
        list_name_button = await text_slicer(sd_styles)
    style_keyboard = await create_keyboard(list_name_button, sd_styles, prefix="style_", state=state, isConfirmed=True)
    return style_keyboard


async def create_loras_keyboard(tg_id, state: FSMContext = None):
    db_lora_list = await db_service.db_get_sd_setting(tg_id, 'sd_lora')
    sd_lora = api_service.get_request_sd_api('loras').json()
    if len(sd_lora) == 0:
        return None
    sd_lora = [x['name'] for x in sd_lora]

    if len(db_lora_list) != 0:
        db_lora_list = db_lora_list.split('&')
        user_loras = await checked_selected_items(db_lora_list, sd_lora)
        list_name_button = await text_slicer(user_loras)
    else:
        list_name_button = await text_slicer(sd_lora)
    lora_keyboard = await create_keyboard(list_name_button, sd_lora, prefix="lora_", state=state, isConfirmed=True)
    return lora_keyboard


async def create_keyboard(list_name_items, list_callback_items, num_columns=2, num_rows=7, prefix='',
                          state: FSMContext = None, isConfirmed=False):
    state_data = await state.get_data()
    current_page = state_data.get('current_page')

    num_pages = len(list_name_items) // (num_columns * num_rows)
    if len(list_name_items) % (num_columns * num_rows) != 0:
        num_pages += 1

    if num_pages > 4:
        num_columns = 3
        num_pages -= 1

    await state.update_data(num_pages=num_pages)
    keyboard = InlineKeyboardMarkup()
    list_button = []
    for i in range(current_page * num_columns * num_rows,
                   (current_page * num_columns * num_rows) + (num_columns * num_rows), num_columns):
        if num_columns > 1:
            for j in range(0, num_columns):
                if i + j < len(list_name_items):
                    list_button.append(InlineKeyboardButton(text=list_name_items[i + j],
                                                            callback_data=prefix + list_callback_items[i + j]))
        keyboard.add(*list_button)
        list_button.clear()
    if num_pages > 1:
        if current_page == 0:
            keyboard.add(InlineKeyboardButton(text="➡️ Page", callback_data=prefix + "next_page"))
        elif 0 < current_page < num_pages - 1:
            keyboard.add(InlineKeyboardButton(text="⬅️ Page", callback_data=prefix + "prev_page"),
                         InlineKeyboardButton(text="➡️ Page", callback_data=prefix + "next_page"))
        elif current_page == num_pages - 1:
            keyboard.add(InlineKeyboardButton(text="⬅️ Page", callback_data=prefix + "prev_page"))
    if isConfirmed:
        keyboard.add(InlineKeyboardButton(text=str_var.confirm, callback_data=prefix + "confirm"),
                     InlineKeyboardButton(text=str_var.disable_all, callback_data=prefix + "disable_all"))
    keyboard.add(InlineKeyboardButton(text=str_var.cancel, callback_data="cancel"))
    return keyboard
