import requests


def post_request_sd_api(endpoint, params):
    url = f"http://127.0.0.1:7860/sdapi/v1/{endpoint}"

    response = requests.post(url, json=params)
    return response.json()


def get_request_sd_api(endpoint):
    url = f"http://127.0.0.1:7860/sdapi/v1/{endpoint}"

    response = requests.get(url)
    return response
