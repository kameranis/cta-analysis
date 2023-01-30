import requests
import logging
from typing import Union, List

import pandas as pd

from cta_secrets import BUS_API_KEY

BASE_URL = 'http://www.ctabustracker.com/bustime/api/v2/'
VEHICLES_ENDPOINT = 'getvehicles'

logging.basicConfig(filename='logs/bus.log', format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.WARN)


class APIError(Exception):
    pass


def call_api(route: str, **params) -> dict:
    try:
        response = requests.get(BASE_URL + route, params={
            'key': BUS_API_KEY,
            'format': 'json',
            **params
        })
        response.raise_for_status()
        body = response.json()['bustime-response']
        if 'error' in body:
            for e in body['error']:
                logging.warning(e)

    except Exception as e:
        logging.warning(f'Unable to complete request to /{route} with params {params}.\n{e}')
    else:
        return body
    return dict()


def get_routes(routes: Union[str, List[str]], tmres: str = 's') -> list:
    route_param = routes if isinstance(routes, str) else ','.join(routes)
    if tmres not in ['m', 's']:
        raise ValueError('Parameter `tmres` can only be one of [\'m\', \'s\']')
    js = call_api(VEHICLES_ENDPOINT, rt=route_param, tmres=tmres)
    return js.get("vehicle", list())
