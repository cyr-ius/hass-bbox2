"""Parent Entity."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BBOX_NAME, CONF_HOST, DOMAIN, MANUFACTURER
from .coordinator import BboxDataUpdateCoordinator
from .helpers import finditem

_LOGGER = logging.getLogger(__name__)


class BboxEntity(CoordinatorEntity[BboxDataUpdateCoordinator], Entity):
    """Base class for all Bbox entities."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: BboxDataUpdateCoordinator, description: EntityDescription
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description

        device = finditem(coordinator.data, "info.device")
        self.box_id = device.get("serialnumber", "ABC12345")
        self._attr_unique_id = f"{self.box_id}-{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.box_id)},
            "manufacturer": MANUFACTURER,
            "name": BBOX_NAME,
            "model": device.get("modelname"),
            "sw_version": device.get("main", {}).get("version"),
            "configuration_url": f"https://{coordinator.config_entry.data[CONF_HOST]}",
        }

class BboxDeviceEntity(BboxEntity):
    """Base class for all device's entities connected to the Bbox"""

    def __init__(
        self,
        coordinator: BboxDataUpdateCoordinator,
        description: EntityDescription,
        device: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)
        self._device = device
        self._device_key = f"{self.box_id}_{device['macaddress'].replace(':', '_')}"
        if self._device.get("userfriendlyname", "") != "":
            self._device_name = device["userfriendlyname"]
        elif self._device.get("hostname") != "":
            self._device_name = device["hostname"]
        else:
            self._device_name = device["macaddress"]
        self._attr_device_info = {
            "name": self._device_name,
            "identifiers": {(DOMAIN, self._device_key)},
            "connections": {(device_registry.CONNECTION_NETWORK_MAC, device["macaddress"])},
            "via_device": (DOMAIN, self.box_id),
        }

    @property
    def coordinator_data(self):
        """Return connecting status."""
        for device in (
            self.coordinator.data.get("devices", {}).get("hosts", {}).get("list", [])
        ):
            if device["macaddress"] == self._device["macaddress"]:
                return device
        return {}

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            "link": self._device.get("link"),
            "last_seen": self._device.get("lastseen"),
            "ip_address": self._device.get("ipaddress"),
        }