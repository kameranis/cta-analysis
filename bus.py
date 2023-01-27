import requests
from secrets import BUS_API_KEY

BASE_URL = "http://www.ctabustracker.com/bustime/api/v2/"


class APIError(Exception):
    pass


def call_api(route: str, **params) -> dict:
    response = requests.get(BASE_URL + route, params={
        'key': BUS_API_KEY,
        'format': 'json',
        **params
    })
    body = response.json()["bustime-response"]

    if "error" in body:
        raise APIError(body["error"][0]["msg"])

    return body

