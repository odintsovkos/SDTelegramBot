import logging

import requests


def post_request_sd_api(endpoint, params):
    url = f"http://127.0.0.1:7860/sdapi/v1/{endpoint}"

    try:
        response = requests.post(url, json=params)
        return response.json()
    except requests.exceptions.ConnectionError:
        logging.critical("Ошибка запроса к SD API. Проверь SD")
        return None


def get_request_sd_api(endpoint):
    url = f"http://127.0.0.1:7860/sdapi/v1/{endpoint}"

    try:
        response = requests.get(url)
        return response
    except requests.exceptions.ConnectionError:
        logging.critical("Ошибка запроса к SD API. Проверь SD")
        return None



