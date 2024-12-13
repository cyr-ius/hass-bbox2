"""Button for Bbox router."""

import logging

from bboxpy.exceptions import BboxException

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BBoxConfigEntry
from .entity import BboxEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: BBoxConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data
    entities = [
        RestartButton(
            coordinator,
            ButtonEntityDescription(
                key="restart", name="Restart", icon="mdi:restart-alert"
            ),
        ),
        RefreshButton(
            coordinator,
            ButtonEntityDescription(
                key="refresh", name="Refresh", icon="mdi:refresh-circle"
            ),
        ),
    ]
    async_add_entities(entities)


class RestartButton(BboxEntity, ButtonEntity):
    """Representation of a button for reboot router."""

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.bbox.device.async_reboot()
        except BboxException as error:
            _LOGGER.error(error)


class RefreshButton(BboxEntity, ButtonEntity):
    """Representation of a button for refreshing integration data."""

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.async_request_refresh()
        except BboxException as error:
            _LOGGER.error(error)
