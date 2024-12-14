"""Support for tracking."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BBoxConfigEntry
from .coordinator import BboxDataUpdateCoordinator
from .entity import BboxDeviceEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: BBoxConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data
    description = SensorEntityDescription(key="tracker", translation_key="tracker")
    devices = coordinator.data.get("devices", {}).get("hosts", {}).get("list", [])
    entities = [
        BboxDeviceTracker(coordinator, description, device)
        for device in devices
        if device.get("macaddress")
    ]
    async_add_entities(entities)


class BboxDeviceTracker(BboxDeviceEntity, ScannerEntity):
    """Representation of a tracked device."""

    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: BboxDataUpdateCoordinator,
        description: SensorEntityDescription,
        device: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description, device)

    @property
    def source_type(self) -> str:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.ROUTER

    @property
    def mac_address(self) -> str:
        """Return mac address."""
        return self._device["macaddress"]

    @property
    def ip_address(self) -> str:
        """Return mac address."""
        return self._device["ipaddress"]

    @property
    def is_connected(self) -> bool:
        """Return connecting status."""
        return self._device.get("active", 0) == 1
