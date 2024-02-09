import requests
import logging
from .const import API_URL
_LOGGER = logging.getLogger(__name__)


class ApiCall:

    @staticmethod
    def update_info(api_key, stop_id, conn_num):
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"ids": stop_id, "total": conn_num, "minutesAfter": 720}

        response = requests.get(API_URL, params=parameters, headers=headers)
        return response.json()

    @staticmethod
    def authenticate(api_key, stop_id, conn_num):
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"ids": stop_id, "total": conn_num, "minutesAfter": 720}
        response = requests.get(API_URL, params=parameters, headers=headers)
        reply = response.json()
        title = reply["stops"][0]["stop_name"]
        if response.status_code == 200:
            return True, title
        else:
            return False, None



