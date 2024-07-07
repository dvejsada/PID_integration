from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect for unknown reason."""


class NoDeparturesSelected(HomeAssistantError):
    """Error to indicate wrong stop was provided."""


class StopNotFound(HomeAssistantError):
    """Error to indicate wrong stop was provided."""


class StopNotInList(HomeAssistantError):
    """Error to indicate stop not on the list was provided."""


class WrongApiKey(HomeAssistantError):
    """Error to indicate wrong API key was provided."""
