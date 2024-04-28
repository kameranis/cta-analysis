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
    """Base function to perform requests to the CTA train API and handle errors.

    This function sends a GET request to the CTA train API with the specified route and query parameters, and returns the
    response body as a dictionary. It also handles any errors that occur during the request, logging any warnings and
    printing any error messages.

    :param route: The API endpoint to request, appended to the base URL.
    :type route: str

    :param params: Query parameters to include in the request.
    :type params: Any

    :return: The response body as a dictionary.
    :rtype: dict
    :raises: APIError: If the response body indicates an error occurred during the request.

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
    """Retrieve the arrival times for a specific CTA train stop using its station ID (stpid)
    or the map ID (mapid).

    :param mapid: The map ID for the stop (e.g., 40900). Either `mapid` or `stpid` must be provided.
    :type mapid: int, optional

    :param stpid: The station ID for the stop (e.g., 30283). Either `mapid` or `stpid` must be provided.
    :type stpid: int, optional

    :param max: The maximum number of arrivals to return.
    :type max: int, optional

    :param rt: The train route code (e.g., 'red', 'blue', etc.) to filter by.
    :type rt: str, optional

    :return: A list of arrival times for the specified stop.
    :rtype: List[Dict]
    """
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


def get_locations(rt: Union[str, Iterable[str]] = TRAIN_ROUTES[::]) -> List[Dict]:
    """Returns the current locations of trains on the specified route(s).

    :param rt: A string or iterable of strings indicating the train route(s) to query. The default value is the list of all
               train routes defined in the module-level constant TRAIN_ROUTES.
    :type rt: str or Iterable[str]

    :return: A list of dictionaries containing information about the locations of trains on the specified route(s).
    :rtype: List[Dict]
    """
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
    """Retrieves estimated arrival times for a train given its `runnumber`.

    :param runnumber: The unique identifier for the train's run.
    :type runnumber: str

    :return: A list of dictionaries, each containing estimated arrival time data for a train.
    :rtype: List[Dict]
    """
    js = call_api(FOLLOW_ENDPOINT, runnumber=runnumber)
    return js.get('eta', list())


def get_predictions(runnumbers: Union[Iterable[str], None]) -> List[Dict]:
    """
    Retrieves the prediction information for the specified train `runnumbers`.

    :param runnumbers: An optional iterable of train run numbers for which predictions are to be retrieved.
                       If not specified, then all currently running trains are fetched and their corresponding
                       predictions are retrieved.
    :type runnumbers: Optional[Iterable[str]]

    :return: A list of dictionaries, where each dictionary represents the prediction information for a particular train.
    :rtype: List[Dict]
    """
    if runnumbers is None:
        runnumbers = [t['rn'] for t in get_locations()]
    predictions = []
    for rn in runnumbers:
        predictions.extend(follow(rn))
    return predictions
