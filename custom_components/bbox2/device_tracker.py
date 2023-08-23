"""Support for tracking."""
from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BboxEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    description = SensorEntityDescription(key="tracker", translation_key="tracker")

    entities = [
        BboxDeviceTracker(coordinator, description, device)
        for device in coordinator.data["devices"]
    ]

    async_add_entities(entities)


class BboxDeviceTracker(BboxEntity, ScannerEntity):
    """Representation of a tracked device."""

    def __init__(self, coordinator, description, device) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self._device = device

    @property
    def unique_id(self):
        """Return unique_id."""
        return f"{self.box_id}-{self._device['id']}"

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.ROUTER

    @property
    def mac_address(self):
        """Return mac address."""
        return self._device["macaddress"]

    @property
    def ip_address(self):
        """Return mac address."""
        return self._device["ipaddress"]

    @property
    def is_connected(self):
        """Return connecting status."""
        for device in self.coordinator.data.get("devices", {}):
            if device["id"] == self._device["id"]:
                return device["active"] == 1

    @property
    def name(self):
        """Return name."""
        return self._device["hostname"]

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "via_device": (DOMAIN, self.box_id),
        }
