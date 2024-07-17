from homeassistant.helpers.entity import Entity

from .hub import DepartureBoard


class BaseEntity(Entity):
    """Base class for entities in the PID Departures integration."""

    # NOTE: Do not set _attr_entity_name, it breaks localization!
    _attr_has_entity_name = True

    def __init__(self, departure_board: DepartureBoard) -> None:
        super().__init__()

        if hasattr(self, "entity_description") and not self.translation_key:
            self._attr_translation_key = self.entity_description.key
        assert self.translation_key is not None, "translation_key is not set"

        self._departure_board = departure_board
        self._attr_device_info = departure_board.device_info
        self._attr_unique_id = f"{departure_board.board_id}_{self.translation_key}"
