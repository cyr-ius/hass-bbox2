"""Parent Entity."""

from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BBOX_NAME, DOMAIN, MANUFACTURER
from .coordinator import BboxDataUpdateCoordinator
from .helpers import finditem


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
    """Base class for all device's entities connected to the Bbox."""

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
            self._device_name = str(device["userfriendlyname"])
        elif self._device.get("hostname") != "":
            self._device_name = str(device["hostname"])
        else:
            self._device_name = device["macaddress"]

        self._attr_name = str(self._device_name)
        self._attr_unique_id = f"{self._device_key}_device_tracker"
        self._attr_device_info = {
            "name": str(self._device_name),
            "identifiers": {(DOMAIN, self._device_key)},
            "connections": {(dr.CONNECTION_NETWORK_MAC, device["macaddress"])},
            "via_device": (DOMAIN, self.box_id),
        }

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            "link": self._device.get("link"),
            "last_seen": self._device.get("lastseen"),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Respond to a DataUpdateCoordinator update."""
        devices = (
            self.coordinator.data.get("devices", {}).get("hosts", {}).get("list", [])
        )
        self._device = next(
            (
                device
                for device in devices
                if device["macaddress"] == self._device.get("macaddress", None)
            ),
            {},
        )
        self.async_write_ha_state()
