import requests

from app import config
from app.config import NAVIGATION
from app.log import LOG
from app.util.datetime_util import datetime_now

__googleUrl = NAVIGATION['url']
__queryParam = NAVIGATION['query_param']
__apiKey = NAVIGATION['api_key']


def fetch_navigation_for_user(query_param):
    query_param_url = config.NAVIGATION['query_param']\
        .replace("[origin.latitude]", query_param.origin.latitude)\
        .replace("[origin.longitude]", query_param.origin.longitude)\
        .replace("[destination.latitude]", query_param.destination.latitude)\
        .replace("[destination.longitude]", query_param.destination.longitude)\
        .replace("[key]", __apiKey)

    api_endpoint = __googleUrl + query_param_url

    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(api_endpoint, headers=headers)

    return response.json()


class NavigationService:

    __googleUrl = NAVIGATION['url']
    __queryParam = NAVIGATION['query_param']
    __apiKey = NAVIGATION['api_key']

    def fetch_navigation_for_user(self, query_params):
        return fetch_navigation_for_user(query_param=query_params)
