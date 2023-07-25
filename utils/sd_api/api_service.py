"""
Автор: Константин Одинцов
e-mail: kos5172@yandex.ru
Github: https://github.com/odintsovkos
Этот файл — часть SDTelegramBot.

SDTelegramBot — свободная программа: вы можете перераспространять ее и/или изменять ее на условиях Стандартной общественной лицензии GNU в том виде, в каком она была опубликована Фондом свободного программного обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.

SDTelegramBot распространяется в надежде, что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной общественной лицензии GNU.

Вы должны были получить копию Стандартной общественной лицензии GNU вместе с этой программой. Если это не так, см. <https://www.gnu.org/licenses/>.
"""


import requests
import logging


def post_request_sd_api(endpoint, params, is_logging=True):
    url = f"http://127.0.0.1:7860/sdapi/v1/{endpoint}"

    try:
        response = requests.post(url, json=params)
        return response.json()
    except requests.exceptions.ConnectionError:
        if is_logging:
            logging.critical("Ошибка запроса к SD API. Проверь SD")
        return None


def get_request_sd_api(endpoint, is_logging=True):
    url = f"http://127.0.0.1:7860/sdapi/v1/{endpoint}"
    try:
        response = requests.get(url)
        return response
    except requests.exceptions.ConnectionError:
        if is_logging:
            logging.critical("Ошибка запроса к SD API. Проверь SD")
        return None
    

def get_models_sd_api():
    return get_request_sd_api("sd-models").json()


def get_hr_upscaler_sd_api():
    return get_request_sd_api("upscalers").json()


def get_image_seed(image):
    png_payload = {
        "image": "data:image/png;base64," + image
    }
    image_info = post_request_sd_api("png-info", png_payload).get('info')
    image_info = image_info.split(', ')
    for j in range(len(image_info) - 1, 0, -1):
        if image_info[j].find("Seed:") != -1:
            return image_info[j][6:]

def get_model_name_by_hash(hash):
    models = get_models_sd_api()
    for model in models:
        if model['sha256'] == hash:
            return model['model_name']
    return None