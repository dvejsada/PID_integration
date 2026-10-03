import logging
from typing import Any, Mapping
from datetime import timedelta

from homeassistant.const import CONF_API_KEY, CONF_ID
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector
import voluptuous as vol

from .const import CONF_CAL_EVENTS_NUM, CONF_DEP_NUM, CONF_STOP_SEL, CONF_WALKING_OFFSET, DOMAIN
from .coordinator import PIDConfigEntry
from .dep_board_api import PIDDepartureBoardAPI
from .errors import CannotConnect, NoDeparturesSelected, StopNotFound, StopNotInList, WrongApiKey
from .stop_list import STOP_LIST, ASW_IDS

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    try:
        data[CONF_ID] = ASW_IDS[STOP_LIST.index(data[CONF_STOP_SEL])]
    except Exception:
        raise StopNotInList

    if data[CONF_DEP_NUM] == 0:
        raise NoDeparturesSelected()

    # Convert user-friendly walking offset to API format:
    # User: positive = future, negative = past
    # API: positive = past, negative = future
    # So we need to invert the sign.
    walking_offset_timedelta = timedelta(minutes=-data.get(CONF_WALKING_OFFSET, 0))

    reply = await PIDDepartureBoardAPI.async_fetch_data(
        async_get_clientsession(hass),
        data[CONF_API_KEY],
        data[CONF_ID],
        data[CONF_DEP_NUM],
        time_before=walking_offset_timedelta,
    )

    title: str = reply["stops"][0]["stop_name"] + " " + (reply["stops"][0]["platform_code"] or "")
    return {"title": title}, data


async def validate_api_key(hass: HomeAssistant, api_key: str, stop_id: str) -> None:
    """Validate an API key against a known stop (used by the reauth flow)."""
    await PIDDepartureBoardAPI.async_fetch_data(
        async_get_clientsession(hass), api_key, stop_id, 1
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        # Check for any previous instance of the integration
        api_key: str | None = None
        entries = self.hass.config_entries.async_entries(DOMAIN)
        if entries:
            # If a previous instance exists, use its API key as suggestion for the new config.
            api_key = entries[0].data.get(CONF_API_KEY)

        data_schema: dict[Any, Any] = {
            vol.Required(CONF_API_KEY, default=api_key): str,
            vol.Required(CONF_DEP_NUM, default=1): int,
            CONF_STOP_SEL: selector({
                "select": {
                    "options": STOP_LIST,
                    "mode": "dropdown",
                    "sort": True,
                    "custom_value": True
                }
            }),
            vol.Optional(CONF_CAL_EVENTS_NUM, default=20): vol.All(
                vol.Coerce(int),
                vol.Range(0, 1000),
            ),
            vol.Optional(CONF_WALKING_OFFSET, default=0): vol.All(
                vol.Coerce(int),
                vol.Range(-30, 4320),
            ),
        }

        # Set dict for errors
        errors: dict[str, str] = {}

        # Steps to take if user input is received
        if user_input is not None:
            try:
                info, data = await validate_input(self.hass, user_input)
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
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(data[CONF_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=data)

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        """Handle a re-authentication (expired/changed API key)."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm re-authentication by validating a new API key."""
        reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert reauth_entry is not None
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_api_key(
                    self.hass, user_input[CONF_API_KEY], reauth_entry.data[CONF_ID]
                )
            except WrongApiKey:
                errors[CONF_API_KEY] = "wrong_api_key"
            except StopNotFound:
                errors["base"] = "stop_not_found"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unknown exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data={**reauth_entry.data, CONF_API_KEY: user_input[CONF_API_KEY]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: PIDConfigEntry,
    ) -> "OptionsFlowHandler":
        """Get the options flow for this handler."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle changes to the tunable options of a departure board."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = self.config_entry

        def current(key: str, default: Any) -> Any:
            return entry.options.get(key, entry.data.get(key, default))

        data_schema = vol.Schema({
            vol.Required(CONF_DEP_NUM, default=current(CONF_DEP_NUM, 1)): vol.All(
                vol.Coerce(int),
                vol.Range(min=1),
            ),
            vol.Optional(CONF_CAL_EVENTS_NUM, default=current(CONF_CAL_EVENTS_NUM, 20)): vol.All(
                vol.Coerce(int),
                vol.Range(0, 1000),
            ),
            vol.Optional(CONF_WALKING_OFFSET, default=current(CONF_WALKING_OFFSET, 0)): vol.All(
                vol.Coerce(int),
                vol.Range(-30, 4320),
            ),
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
