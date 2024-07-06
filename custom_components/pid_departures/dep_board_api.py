import requests
import logging
from .const import API_URL
_LOGGER = logging.getLogger(__name__)


class PIDDepartureBoardAPI:

    @staticmethod
    def update_info(api_key, stop_id, conn_num):
        """ Gets new data from API. """
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"aswIds": stop_id, "total": conn_num, "minutesAfter": 4320}
        response = requests.get(API_URL, params=parameters, headers=headers)
        return response.json()

    @staticmethod
    def authenticate(api_key, stop_id, conn_num):
        """ Checks the authentication. """
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"aswIds": stop_id, "total": conn_num, "minutesAfter": 4320}
        response = requests.get(API_URL, params=parameters, headers=headers)
        reply = response.json()
        return response.status_code, reply
