"""Support for tracking."""
from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BboxEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(key="tracker", translation_key="tracker"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SENSOR_TYPES:
        for device in coordinator.data["devices"]:
            entities.append(
                BboxDeviceTracker(coordinator, description, device["hostname"])
            )

    async_add_entities(entities)


class BboxDeviceTracker(BboxEntity, TrackerEntity):
    """Representation of a sensor."""

    def __init__(self, coordinator, description, hostname) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self.host = hostname

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.ROUTER

    @property
    def mac_address(self):
        """Return mac address."""
        return self.coordinator.data["devices"][self.host]["macaddress"]

    @property
    def ip_address(self):
        """Return mac address."""
        return self.coordinator.data["devices"][self.host]["ipaddress"]

    @property
    def is_connected(self):
        """Return connecting status."""
        return self.coordinator.data["devices"][self.host]["active"] == 1

    @property
    def name(self):
        """Return name."""
        return self.host
