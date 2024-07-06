import voluptuous as vol

import logging
from typing import Any, Tuple, Dict
from .dep_board_api import PIDDepartureBoardAPI

from .const import DOMAIN, CONF_DEP_NUM, CONF_STOP_SEL
from homeassistant.const import CONF_API_KEY, CONF_ID
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import selector
from .stop_list import STOP_LIST, ASW_IDS

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> tuple[dict[str, str], dict]:
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    try:
        data[CONF_ID] = ASW_IDS[STOP_LIST.index(data[CONF_STOP_SEL])]
    except Exception:
        raise StopNotInList
    status, reply = await hass.async_add_executor_job(PIDDepartureBoardAPI.authenticate, data[CONF_API_KEY], data[CONF_ID], data[CONF_DEP_NUM])
    if status == 200:
        title: str = reply["stops"][0]["stop_name"] + " " + (reply["stops"][0]["platform_code"] or "")
        if data[CONF_DEP_NUM] == 0:
            raise NoDeparturesSelected()
        else:
            return {"title": title}, data
    elif status == 401:
        raise WrongApiKey
    elif status == 404:
        raise StopNotFound
    else:
        raise CannotConnect


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    VERSION = 0.1

    async def async_step_user(self, user_input=None):

        # Check for any previous instance of the integration
        if DOMAIN in list(self.hass.data.keys()):
            # If previous instance exists, set the API key as suggestion to new config
            data_schema = {vol.Required(CONF_API_KEY, default=self.hass.data[DOMAIN][list(self.hass.data[DOMAIN].keys())[0]].api_key): str,
                vol.Required(CONF_DEP_NUM, default=1): int}
        else:
            # if no previous instance, show blank form
            data_schema = {vol.Required(CONF_API_KEY): str,
                 vol.Required(CONF_DEP_NUM, default=1): int}

        data_schema[CONF_STOP_SEL] = selector({
                "select": {
                    "options": STOP_LIST,
                    "mode": "dropdown",
                    "sort": True,
                    "custom_value": True
                }
            })

        # Set dict for errors
        errors: dict = {}

        # Steps to take if user input is received
        if user_input is not None:
            try:
                info, data = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=data)

            except CannotConnect:
                _LOGGER.exception("Cannot connect to API, check your internet connection.")
                errors["base"] = "cannot_connect"

            except WrongApiKey:
                _LOGGER.exception("Wrong or no API key provided, cannot authorize connection to API.")
                errors[CONF_API_KEY] = "wrong_api_key"

            except StopNotFound:
                _LOGGER.exception("Stop was not found by the API.")
                errors[CONF_STOP_SEL] = "stop_not_found"

            except StopNotInList:
                errors[CONF_STOP_SEL] = "stop_not_in_list"

            except NoDeparturesSelected:
                errors[CONF_DEP_NUM] = "no_departures_selected"

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception")
                errors["base"] = "Unknown exception"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect for unknown reason."""


class WrongApiKey(exceptions.HomeAssistantError):
    """Error to indicate wrong API key was provided."""


class StopNotFound(exceptions.HomeAssistantError):
    """Error to indicate wrong stop was provided."""


class NoDeparturesSelected(exceptions.HomeAssistantError):
    """Error to indicate wrong stop was provided."""


class StopNotInList(exceptions.HomeAssistantError):
    """Error to indicate stop not on the list was provided."""
