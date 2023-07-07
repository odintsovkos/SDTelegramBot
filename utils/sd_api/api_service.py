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

