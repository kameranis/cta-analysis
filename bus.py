import logging
from typing import Union, List, Dict
import requests

from cta_secrets import BUS_API_KEY

BASE_URL = 'http://www.ctabustracker.com/bustime/api/v2/'
VEHICLES_ENDPOINT = 'getvehicles'
ROUTES_ENDPOINT = 'getroutes'
DIRECTIONS_ENDPOINT = 'getdirections'
STOPS_ENDPOINT = 'getstops'
PATTERNS_ENDPOINT = 'getpatterns'
PREDICTIONS_ENDPOINT = 'getpredictions'

logging.basicConfig(filename='logs/bus.log', format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.WARN)

MAX_ROUTES_PER_CALL = 10
MAX_PATTERNS_PER_CALL = 10
MAX_STOPS_PER_CALL = 10
MAX_VEHICLES_PER_CALL = 10


class APIError(Exception):
    pass


def call_api(route: str, **params) -> Dict:
    """Base function to perform requests to the CTA bus API and handle errors

    :param route:

    """
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


def get_vehicles(routes: Union[str, List[str]], tmres: str = 's') -> List:
    route_param = routes if isinstance(routes, str) else ','.join(routes)
    if tmres not in ['m', 's']:
        raise ValueError('Parameter `tmres` can only be one of [\'m\', \'s\']')
    js = call_api(VEHICLES_ENDPOINT, rt=route_param, tmres=tmres)
    return js.get('vehicle', list())


def get_routes() -> List:
    js = call_api(ROUTES_ENDPOINT)
    return js.get('routes', list())


def get_all_vehicles() -> List:
    routes = get_routes()
    rts = [rt['rt'] for rt in routes]
    vehicles = []
    for i in range(0, len(rts), MAX_ROUTES_PER_CALL):
        vehicles.extend(get_vehicles(routes=rts[i:i + MAX_ROUTES_PER_CALL]))
    return vehicles


def get_directions(route: str) -> List:
    js = call_api(DIRECTIONS_ENDPOINT, rt=route)
    return js.get('directions', list())


def get_all_directions() -> Dict[str, List]:
    routes = get_routes()
    rts = [rt['rt'] for rt in routes]
    directions = {rt: [direction['dir']
                       for direction in get_directions(rt)
                       if 'dir' in direction]
                  for rt in rts}
    return directions


def get_route_stops(route: str, direction: str) -> List:
    js = call_api(STOPS_ENDPOINT, rt=route, dir=direction)
    return js.get('stops', list())


def get_all_stops(directions: Union[None, Dict[str, List[str]]] = None) -> Dict[str, Dict[str, List]]:
    if directions is None:
        directions = get_all_directions()
    all_stops = {rt: {rt_direction: get_route_stops(rt, rt_direction)
                      for rt_direction in rt_directions}
                 for rt, rt_directions in directions.items()}
    return all_stops


def get_patterns_from_pids(pids: List[Union[str, int]]) -> Dict[int, Dict]:
    patterns = {}
    for i in range(0, len(pids), MAX_PATTERNS_PER_CALL):
        js = call_api(PATTERNS_ENDPOINT, pid=','.join(str(pid) for pid in pids[i:i+MAX_PATTERNS_PER_CALL]))
        for ptr in js['ptr']:
            patterns[ptr['pid']] = ptr
    return patterns


def get_pattern_from_rt(rt: str) -> Dict[int, Dict]:
    js = call_api(PATTERNS_ENDPOINT, rt=rt)
    patterns = {ptr['pid']: ptr for ptr in js['ptr']}
    return patterns


def get_all_patterns() -> Dict[int, Dict]:
    routes = get_routes()
    rts = [rt['rt'] for rt in routes]
    patterns = {}
    for rt in rts:
        rt_patterns = get_pattern_from_rt(rt)
        for pid, _ in rt_patterns.items():
            rt_patterns[pid]['rt'] = rt
        patterns.update(rt_patterns)
    return patterns


def get_predictions_from_stops(stops: Union[str, List[str]], rts: Union[None, str, List[str]] = None) -> List[Dict]:
    predictions = []
    if isinstance(stops, str):
        stops = [stops]
    if isinstance(rts, list):
        rts = ','.join(rts)
    for i in range(0, len(stops), MAX_STOPS_PER_CALL):
        if rts is None:
            predictions.extend(call_api(PREDICTIONS_ENDPOINT, stpid=','.join(stops[i:i + MAX_STOPS_PER_CALL]))['prd'])
        else:
            predictions.extend(call_api(PREDICTIONS_ENDPOINT, stpid=','.join(stops[i:i + MAX_STOPS_PER_CALL]), rt=rts)['prd'])
    return predictions


def get_predictions_from_vehicles(vehicles: Union[str, List[str]]) -> List[Dict]:
    if isinstance(vehicles, str) and ',' in vehicles:
        vehicles = vehicles.split(',')
    if isinstance(vehicles, str):
        return call_api(PREDICTIONS_ENDPOINT, vid=vehicles)['prd']
    predictions = []
    for i in range(0, len(vehicles), MAX_VEHICLES_PER_CALL):
        js = call_api(PREDICTIONS_ENDPOINT, vid=','.join(vehicles[i:i + MAX_VEHICLES_PER_CALL]))
        predictions.extend(js.get('prd', []))
    return predictions


def get_all_predictions() -> List[Dict]:
    vehicles = get_all_vehicles()
    vids = [vehicle['vid'] for vehicle in vehicles]
    predictions = get_predictions_from_vehicles(vids)
    return predictions
