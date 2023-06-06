import requests

from utils.db_services.db_get_service import db_get_sd_settings, db_get_sd_setting
from utils.sd_api import api_service
from utils.sd_api.api_service import get_request_sd_api


def set_params(tg_id: int, last_prompt):
    db_result = db_get_sd_settings(tg_id)

    params = {
        "prompt": last_prompt,
        "negative_prompt": db_result[3],
        "styles": [db_result[2]],
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
    db_model = db_get_sd_setting(tg_id, "sd_model")[0]
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
