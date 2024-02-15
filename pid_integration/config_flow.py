import voluptuous as vol

import logging
from typing import Any
from .api_call import ApiCall

from .const import DOMAIN, CONF_DEP_NUM
from homeassistant.const import CONF_API_KEY, CONF_ID
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    status, reply = await hass.async_add_executor_job(ApiCall.authenticate, data[CONF_API_KEY], data[CONF_ID], data[CONF_DEP_NUM])
    if status == 200:
        title: str = reply["stops"][0]["stop_name"] + " " + ApiCall.check_not_null(reply["stops"][0]["platform_code"])
        return {"title": title}
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
            data_schema = vol.Schema(
                {vol.Required(CONF_ID): str, vol.Required(CONF_API_KEY, default=self.hass.data[DOMAIN][list(self.hass.data[DOMAIN].keys())[0]].api_key): str,
                vol.Required(CONF_DEP_NUM): int}
                )
        else:
            # if no previous instance, show blank form
            data_schema = vol.Schema(
                {vol.Required(CONF_ID): str, vol.Required(CONF_API_KEY): str,
                 vol.Required(CONF_DEP_NUM): int}
            )

        # Set dict for errors
        errors: dict = {}

        # Steps to take if user input is received
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)

            except CannotConnect:
                _LOGGER.exception("Unknown API connection error")
                errors["base"] = "Unknown API connection error"

            except WrongApiKey:
                _LOGGER.exception("The API key provided in configuration is not correct.")
                errors["base"] = "Connection was not authorized. Wrong or no API key provided"

            except StopNotFound:
                _LOGGER.exception("Stop with provided awsIDs was not found.")
                errors["base"] = "Non existent awsIds provided, stop not found."

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception - cannot connect to API")
                errors["base"] = "Unknown exception - cannot connect to API"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect for unknown reason."""


class WrongApiKey(exceptions.HomeAssistantError):
    """Error to indicate wrong API key was provided."""


class StopNotFound(exceptions.HomeAssistantError):
    """Error to indicate wrong stop was provided."""
