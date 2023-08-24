"""Button for Bbox router."""
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from bboxpy.exceptions import BboxException
from .const import DOMAIN
from .entity import BboxEntity

_LOGGER = logging.getLogger(__name__)

BUTTON_RESTART: tuple[ButtonEntityDescription, ...] = ButtonEntityDescription(
    key="restart", name="Restart", icon="mdi:restart-alert"
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [RestartButton(coordinator, BUTTON_RESTART)]
    async_add_entities(entities)


class RestartButton(BboxEntity, ButtonEntity):
    """Representation of a button for reboot router."""

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.bbox.device.async_reboot()
        except BboxException as error:
            _LOGGER.error(error)
