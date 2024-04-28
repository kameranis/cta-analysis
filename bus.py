"""
Module for accessing the CTA bus tracker API.

This module provides functions to access various endpoints of the CTA bus tracker API,
including getting data on routes, vehicles, stops, patterns, and predictions.
"""

import os
import sys
import logging
from typing import Union, List, Dict
import requests

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

if SCRIPT_DIRECTORY not in sys.path:
    sys.path.append(SCRIPT_DIRECTORY)

LOG_FILE = os.path.join(SCRIPT_DIRECTORY, 'logs', 'bus.log')
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE), mode=0o766, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s\t%(levelname)s\t%(message)s', level=logging.WARN)

from cta_secrets import BUS_API_KEY

BASE_URL = 'http://www.ctabustracker.com/bustime/api/v2/'
VEHICLES_ENDPOINT = 'getvehicles'
ROUTES_ENDPOINT = 'getroutes'
DIRECTIONS_ENDPOINT = 'getdirections'
STOPS_ENDPOINT = 'getstops'
PATTERNS_ENDPOINT = 'getpatterns'
PREDICTIONS_ENDPOINT = 'getpredictions'


MAX_ROUTES_PER_CALL = 10
MAX_PATTERNS_PER_CALL = 10
MAX_STOPS_PER_CALL = 10
MAX_VEHICLES_PER_CALL = 10


class APIError(Exception):
    """Generic error class to indicate that an error is induced by the API"""
    pass


def call_api(route: str, **params) -> Dict:
    """Base function to perform requests to the CTA bus API and handle errors

    :param route: The endpoint route to call.
    :type route: str
    :param params: Additional parameters to pass to the API.
    :type params: Any
    :return: A dictionary containing the response from the API.
    :rtype: Dict
    :raises APIError: If there is an error while calling the API.
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
    """Get data about all buses on the specified routes.

    :param routes: A list of route IDs to retrieve data for, or a single route ID as a string.
    :type routes: Union[str, List[str]]
    :param tmres: The time resolution of the data. Can be either "m" for minutes or "s" for seconds.
    :type tmres: str
    :return: A list of dictionaries containing data about buses on the specified routes.
    :rtype: List[Dict]
    :raises ValueError: If the `tmres` parameter is not 'm' or 's'.
    """
    route_param = routes if isinstance(routes, str) else ','.join(routes)
    if tmres not in ['m', 's']:
        raise ValueError('Parameter `tmres` can only be one of [\'m\', \'s\']')
    js = call_api(VEHICLES_ENDPOINT, rt=route_param, tmres=tmres)
    return js.get('vehicle', list())


def get_routes() -> List:
    """Retrieve data about all available bus routes.

    :return: A list of dictionaries containing data about available bus routes.
    :rtype: List[Dict]
    """
    js = call_api(ROUTES_ENDPOINT)
    return js.get('routes', list())


def get_all_vehicles() -> List:
    """
    Retrieve data about all buses on all available routes.

    :return: A list of dictionaries containing data about buses on all routes.
    :rtype: List[Dict]
    """
    routes = get_routes()
    rts = [rt['rt'] for rt in routes]
    vehicles = []
    for i in range(0, len(rts), MAX_ROUTES_PER_CALL):
        vehicles.extend(get_vehicles(routes=rts[i:i + MAX_ROUTES_PER_CALL]))
    return vehicles


def get_directions(route: str) -> List[Dict[str, str]]:
    """Retrieve data about the directions that a bus route can take.

    :param route: The route ID for the bus route.
    :type route: str
    :return: A list of strings representing the possible directions for the given route.
    :rtype: List[str]
    """
    js = call_api(DIRECTIONS_ENDPOINT, rt=route)
    return js.get('directions', list())


def get_all_directions() -> Dict[str, List[str]]:
    """Retrieve data about all directions for all available routes.

    :return: A dictionary containing lists of directions for each route.
    :rtype: Dict[str, List[str]]
    """
    routes = get_routes()
    rts = [rt['rt'] for rt in routes]
    directions = {rt: [direction['dir']
                       for direction in get_directions(rt)
                       if 'dir' in direction]
                  for rt in rts}
    return directions


def get_route_stops(route: str, direction: str) -> List:
    """Retrieve data about all stops on a given route and direction.

    :param route: A string representing the route number.
    :type route: str
    :param direction: A string representing the direction of the route (i.e. Northbound or Southbound).
    :type direction: str
    :return: A list of dictionaries containing data about each stop on the given route and direction.
    :rtype: List[Dict]
    """
    js = call_api(STOPS_ENDPOINT, rt=route, dir=direction)
    return js.get('stops', list())


def get_all_stops(directions: Union[None, Dict[str, List[str]]] = None) -> Dict[str, Dict[str, List]]:
    """Retrieve data about all stops for all available routes and directions.

    :param directions: A dictionary of route directions, where each key is a route name and each value is a list of
                       directions for that route. If None, the function will retrieve all available directions using
                       get_all_directions().
    :type directions: Dict[str, List[str]] or None
    :return: A dictionary containing data about stops for all routes and directions. The keys of the outer dictionary
             are the route names, and the values are inner dictionaries. The keys of the inner dictionaries are the
             direction names, and the values are lists of stops for that direction.
    :rtype: Dict[str, Dict[str, List]]
    """
    if directions is None:
        directions = get_all_directions()
    all_stops = {rt: {rt_direction: get_route_stops(rt, rt_direction)
                      for rt_direction in rt_directions}
                 for rt, rt_directions in directions.items()}
    return all_stops


def get_patterns_from_pids(pids: List[Union[str, int]]) -> Dict[int, Dict]:
    """Retrieve data about the patterns (i.e., routes) with the given pattern IDs.

    :param pids: A list of pattern IDs.
    :type pids: List[Union[str, int]]
    :return: A dictionary containing data about the patterns with the given pattern IDs.
    :rtype: Dict[int, Dict]
    """
    patterns = {}
    for i in range(0, len(pids), MAX_PATTERNS_PER_CALL):
        js = call_api(PATTERNS_ENDPOINT, pid=','.join(str(pid) for pid in pids[i:i+MAX_PATTERNS_PER_CALL]))
        for ptr in js['ptr']:
            patterns[ptr['pid']] = ptr
    return patterns


def get_pattern_from_rt(rt: str) -> Dict[int, Dict]:
    """Retrieve data about a pattern for a specific route.

    :param rt: A string representing the route to get pattern data for.
    :type rt: str
    :return: A dictionary containing data about the pattern for the specified route.
    :rtype: Dict[int, Dict]
    """
    js = call_api(PATTERNS_ENDPOINT, rt=rt)
    patterns = {ptr['pid']: ptr for ptr in js['ptr']}
    return patterns


def get_all_patterns() -> Dict[int, Dict]:
    """
    Retrieve data about all available patterns.

    :return: A dictionary containing data about all available patterns.
    :rtype: Dict[int, Dict]
    """
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
    """Retrieve predictions for buses arriving at the given stops.

    :param stops: A list of stop IDs or a single stop ID.
    :type stops: Union[str, List[str]]

    :param rts: A list of route numbers, a single route number, or None. If specified,
                only buses for the given route numbers will be included in the predictions.
    :type rts: Union[None, str, List[str]]

    :return: A list of dictionaries containing prediction data for the specified stops and routes.
    :rtype: List[Dict]
    """
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
    """Retrieve predicted arrival times for all available vehicles with given IDs.

    :param vehicles: A string or list of strings representing vehicle IDs.
    :type vehicles: Union[str, List[str]]

    :return: A list of dictionaries containing predicted arrival times for all available vehicles with given IDs.
    :rtype: List[Dict]
    """
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
    """Retrieve data about all bus predictions for all vehicles.

    :return: A list of dictionaries containing data about all bus predictions for all vehicles.
    :rtype: List[Dict]
    """
    vehicles = get_all_vehicles()
    vids = [vehicle['vid'] for vehicle in vehicles]
    predictions = get_predictions_from_vehicles(vids)
    return predictions
