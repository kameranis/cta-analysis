import logging
from typing import Union, List, Dict, Iterable
import requests

from cta_secrets import TRAIN_API_KEY

TRAIN_ROUTES = ("Red", "Blue", "Brn", "G", "Org", "P", "Pink", "Y")
BASE_URL = 'http://lapi.transitchicago.com/api/1.0/'
ARRIVALS_ENDPOINT = 'ttarrivals.aspx'
FOLLOW_ENDPOINT = 'ttfollow.aspx'
LOCATIONS_ENDPOINT = 'ttpositions.aspx'


class APIError(Exception):
    pass


def call_api(route: str, **params) -> Dict:
    """Base function to perform requests to the CTA bus API and handle errors

    :param route:

    """
    try:
        response = requests.get(BASE_URL + route, params={
            'key': TRAIN_API_KEY,
            'outputType': 'json',
            **params
        })
        response.raise_for_status()
        body = response.json()['ctatt']
        if 'error' in body:
            for e in body['error']:
                logging.warning(e)
                print(e)

    except Exception as e:
        logging.warning(f'Unable to complete request to /{route} with params {params}.\n{e}')
    else:
        return body
    return dict()


def get_stop_arrival(mapid: Union[None, int] = None,
                     stpid: Union[None, int] = None,
                     max: Union[None, int] = None,
                     rt: Union[None, str] = None) -> List[Dict]:
    if mapid is not None and stpid is not None:
        raise ValueError('Cannot include both `mapid` and `stpid` parameters.')
    if mapid is None and stpid is None:
        raise ValueError('Need to include one of `mapid` or `stpid`.')
    params = {}
    if mapid is not None:
        params['mapid'] = mapid
    if stpid is not None:
        params['stpid'] = stpid
    if max is not None:
        params['max'] = max
    if rt is not None:
        params['rt'] = rt
    js = call_api(ARRIVALS_ENDPOINT, **params)
    return js['eta']


def get_locations(rt: Union[int, Iterable[int], str, Iterable[str]] = TRAIN_ROUTES[::]) -> List:
    if isinstance(rt, Iterable):
        rt = ','.join([str(r) for r in rt])
    js = call_api(LOCATIONS_ENDPOINT, rt=rt)
    locations = []
    for rt in js['route']:
        rt_name = rt['@name']
        if 'train' not in rt.keys():
            continue
        if isinstance(rt['train'], dict):
            rt['train']['rt'] = rt_name
            locations.append(rt['train'])
            continue
        for loc in rt['train']:
            loc['rt'] = rt_name
            locations.append(loc)
    return locations


def follow(runnumber: str) -> List[Dict]:
    js = call_api(FOLLOW_ENDPOINT, runnumber=runnumber)
    return js.get('eta', list())


def get_predictions(runnumbers: Union[Iterable[str], None]) -> List[Dict]:
    if runnumbers is None:
        runnumbers = [t['rn'] for t in get_locations()]
    predictions = []
    for rn in runnumbers:
        predictions.extend(follow(rn))
    return predictions
